""" Confluence Publisher

Encapsulate the logic of processing a markdown directory tree.

"""
import hashlib
import mistune
import os

from mistune.directives import DirectiveInclude
from .AdmonitionsDirective import Admonition
from .HTMLCommentPlugin import plugin_html_comment
from .HugoRefLinkPlugin import HugoRefLinkPlugin
from .FrontMatterPlugin import plugin_front_matter
from .ConfluenceRenderer import ConfluenceRenderer, generate_autoindex
from .KeyValue import KeyValue
from atlassian import Confluence
from atlassian.confluence import ApiError
from requests import HTTPError
from .utilities import getFileContent


def sha256(value):
    h = hashlib.sha256(value.encode())
    return h.hexdigest()


def get_file_sha256(filepath):
    return sha256(getFileContent(filepath))


class ConfluencePublisher():

    def __init__(
            self, url, username, api_token,
            page_title_prefix, markdown_dir, db_path, space, parent_pageid,
            force_update=False, force_delete=False, skip_update=False,
            verbose=False):

        self.api = Confluence(url=url, username=username, password=api_token)
        self.page_title_prefix = page_title_prefix
        self.markdown_dir = markdown_dir
        self.kv = KeyValue(db_path)
        self.space = space
        self.parent_pageid = parent_pageid
        self.force_update = force_update
        self.force_delete = force_delete
        self.skip_update = skip_update
        self.confluence_renderer = ConfluenceRenderer(verbose)
        self.renderer = mistune.create_markdown(
            renderer=self.confluence_renderer,
            plugins=[
                plugin_front_matter,
                DirectiveInclude(),
                HugoRefLinkPlugin(self.markdown_dir),
                'strikethrough',
                'footnotes',
                'table',
                'url',
                Admonition(),
                plugin_html_comment,
            ]
        )

    def __update_page(self, space, parentid, filepath, autoindex=False):

        metadata = self.kv.load(filepath)

        current_title = metadata['title']
        current_hash = metadata['sha256']
        sha_hash = get_file_sha256(filepath)

        # --- Render (BEGIN)

        body = ''
        state = {'front_matter': {}}

        if autoindex:
            body = generate_autoindex()
            state['front_matter']['title'] = \
                os.path.basename(os.path.dirname(filepath)).title()
        else:
            if filepath.endswith("_index.md"):
                body = generate_autoindex()
            body += self.renderer.read(filepath, state)

        title = '{}{}'.format(self.page_title_prefix,
                              state['front_matter']['title'])

        # --- Render (END)

        if current_title and current_title != title:
            print('REN => Title: ' + title)
            confluence_page_id = self.api.get_page_id(space, current_title)
            self.api.update_page(confluence_page_id, title, body)

        if current_hash != sha_hash or self.force_update:
            if autoindex:
                print('IDX => Title: ' + title)
            else:
                print('UPD => Title: ' + title)

            if self.api.update_or_create(
                parent_id=parentid,
                title=title,
                body=body,
                representation='storage'
            ):
                confluence_page_id = self.api.get_page_id(space, title)
                self.kv.save(filepath,
                             {'id': confluence_page_id, 'title': title, 'sha256': sha_hash})
                return confluence_page_id

            return None
        else:
            print('SKP => Title: ' + title)
            return self.api.get_page_id(space, title)

    def __delete_attachment(self, filepath):
        metadata = self.kv.load(filepath)
        filename = os.path.basename(filepath)
        if metadata['id']:
            try:
                print('DEL Att. => Title: ' + filename)
                # https://confluence.atlassian.com/confkb/confluence-rest-api-lacks-delete-method-for-attachments-715361922.html
                # self.api.delete_attachment_by_id(metadata['id'], 1)
                self.api.remove_content(metadata['id'])
            except (HTTPError, ApiError):
                pass

    def __update_attachment(self, space, pageid, filepath):
        filename = os.path.basename(filepath)

        print('UPD Att. => Title: ' + filename)
        results = self.api.attach_file(filepath,
                                       name=filename,
                                       page_id=pageid,
                                       space=space)
        confluence_page_id = results['id'] if 'id' in results else results['results'][0]['id']
        self.kv.save(filepath, {'id': confluence_page_id,
                                'title': filename, 'sha256': None})
        return confluence_page_id

    def __publish_recursive(self, space, parentid, path, root=False):
        # File: _index.md
        index_parentid = parentid
        index_path = path + os.sep + '_index.md'
        if not root:
            if os.path.isfile(index_path):
                # Use local _index.md file
                index_parentid = self.__update_page(
                    space, parentid, index_path)
            else:
                # Autoindex simulate _index.md in Confluence if missing locally
                index_parentid = self.__update_page(
                    space, parentid, index_path, True)

        # Directories: */
        for f in os.scandir(path):
            if f.is_dir():
                self.__publish_recursive(space, index_parentid, f.path)

        # Files: *.* (Except _index.md)
        for f in os.scandir(path):
            if f.is_file():
                if f.path.endswith(".md"):
                    if not f.path.endswith(os.sep + '_index.md'):
                        self.__update_page(space, index_parentid, f.path)
                else:
                    self.__delete_attachment(f.path)
                    self.__update_attachment(space, index_parentid, f.path)

    def delete(self):
        for filepath in sorted(self.kv.keys()):
            metadata = self.kv.load(filepath)

            # Page has Sub-pages (Childs)?
            index_with_childs = False
            if filepath.endswith('_index.md'):
                childs = 0
                if os.path.isdir(os.path.dirname(filepath)):
                    for f in os.scandir(os.path.dirname(filepath)):
                        if f.path.endswith(".md") and \
                           not f.path.endswith('_index.md'):
                            childs = childs + 1
                index_with_childs = childs > 0

            if self.force_delete \
               or (not os.path.isfile(filepath) and not index_with_childs):
                print('DEL => Id: '
                      + metadata['id'] + ', Title: ' + metadata['title'])
                if filepath.endswith(".md"):
                    try:
                        if self.api.get_page_by_id(metadata['id']):
                            self.api.remove_page(metadata['id'])
                    except HTTPError as ex:
                        code = ex.response.status_code
                        if code != 404:
                            print("DEL Pag. (Error):" + str(code))
                        else:
                            pass
                else:
                    self.__delete_attachment(filepath)

                self.kv.remove(filepath)

    def publish(self):
        self.__publish_recursive(
            self.space, self.parent_pageid, self.markdown_dir, root=True)
