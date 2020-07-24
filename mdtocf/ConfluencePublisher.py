""" Confluence Publisher

Encapsulate the logic of processing a markdown directory tree.

"""
import hashlib
import mistune
import os

from mistune.directives import DirectiveInclude
from .AdmonitionsDirective import Admonition
from .HugoRefLinkPlugin import HugoRefLinkPlugin
from .FrontMatterPlugin import plugin_front_matter
from .ConfluenceRenderer import ConfluenceRenderer
from .KeyValue import KeyValue
from atlassian import Confluence
from atlassian.confluence import ApiError
from requests import HTTPError
from .utilities import getFileContent


def sha256(value):
    h = hashlib.sha256(value.encode())
    return h.hexdigest()


def getFileSha256(filepath):
    return sha256(getFileContent(filepath))


class ConfluencePublisher():

    def __init__(
            self, url, username, apiToken,
            pageTitlePrefix, markdownDir, dbPath, space, parentPageId,
            forceUpdate=False, forceDelete=False, skipUpdate=False):
        self.api = Confluence(url=url, username=username, password=apiToken)
        self.pageTitlePrefix = pageTitlePrefix
        self.markdownDir = markdownDir
        self.kv = KeyValue(dbPath)
        self.space = space
        self.parentPageId = parentPageId
        self.forceUpdate = forceUpdate
        self.forceDelete = forceDelete
        self.skipUpdate = skipUpdate
        self.confluenceRenderer = ConfluenceRenderer()
        self.renderer = mistune.create_markdown(
            renderer=self.confluenceRenderer,
            plugins=[
                plugin_front_matter,
                DirectiveInclude(),
                HugoRefLinkPlugin(markdownDir),
                'strikethrough',
                'footnotes',
                'table',
                'url',
                Admonition(),
            ]
        )

    def __updatePage(self, space, parentId, filepath, autoindex=False):

        metadata = self.kv.load(filepath)

        currentTitle = metadata['title']
        currentHash = metadata['sha256']
        hash = getFileSha256(filepath)

        # --- Render (BEGIN)

        state = {'front_matter': {}}

        if autoindex:
            body = self.confluenceRenderer.generate_autoindex()
            state['front_matter']['title'] = \
                os.path.basename(os.path.dirname(filepath)).title()
        else:
            body = self.renderer.read(filepath, state)

        title = '{}{}'.format(self.pageTitlePrefix,
                              state['front_matter']['title'])

        # --- Render (END)

        if currentTitle and currentTitle != title:
            print('REN => Title: ' + title)
            pageId = self.api.get_page_id(space, currentTitle)
            self.api.update_page(pageId, title, body)

        if currentHash != hash or self.forceUpdate:
            if autoindex:
                print('IDX => Title: ' + title)
            else:
                print('UPD => Title: ' + title)

            if self.api.update_or_create(
                parent_id=parentId,
                title=title,
                body=body,
                representation='storage'
            ):
                id = self.api.get_page_id(space, title)
                self.kv.save(filepath,
                             {'id': id, 'title': title, 'sha256': hash})
                return id
            else:
                return None
        else:
            print('SKP => Title: ' + title)
            return self.api.get_page_id(space, title)

    def __deleteAttachment(self, filepath):
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

    def __updateAttachment(self, space, pageId, filepath):
        filename = os.path.basename(filepath)

        print('UPD Att. => Title: ' + filename)
        results = self.api.attach_file(filepath,
                                       name=filename,
                                       page_id=pageId,
                                       space=space)
        id = results['id'] if 'id' in results else results['results'][0]['id']
        self.kv.save(filepath, {'id': id, 'title': filename, 'sha256': None})
        return id

    def __publishRecursive(self, space, parentId, path, root=False):
        # File: _index.md
        indexParentId = parentId
        indexPath = path + os.sep + '_index.md'
        if not root:
            if os.path.isfile(indexPath):
                # Use local _index.md file
                indexParentId = self.__updatePage(space, parentId, indexPath)
            else:
                # Autoindex simulate _index.md in Confluence if missing locally
                indexParentId = self.__updatePage(
                    space, parentId, indexPath, True)

        # Directories: */
        for f in os.scandir(path):
            if f.is_dir():
                self.__publishRecursive(space, indexParentId, f.path)

        # Files: *.* (Except _index.md)
        for f in os.scandir(path):
            if f.is_file():
                if f.path.endswith(".md"):
                    if not f.path.endswith(os.sep + '_index.md'):
                        self.__updatePage(space, indexParentId, f.path)
                else:
                    self.__deleteAttachment(f.path)
                    self.__updateAttachment(space, indexParentId, f.path)

    def delete(self):
        for filepath in sorted(self.kv.keys()):
            metadata = self.kv.load(filepath)

            # Page has Sub-pages (Childs)?
            indexWithChilds = False
            if filepath.endswith('_index.md'):
                childs = 0
                if os.path.isdir(os.path.dirname(filepath)):
                    for f in os.scandir(os.path.dirname(filepath)):
                        if f.path.endswith(".md") and \
                           not f.path.endswith('_index.md'):
                            childs = childs + 1
                indexWithChilds = childs > 0

            if self.forceDelete \
               or (not os.path.isfile(filepath) and not indexWithChilds):
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
                    self.__deleteAttachment(filepath)

                self.kv.remove(filepath)

    def publish(self):
        self.__publishRecursive(
            self.space, self.parentPageId, self.markdownDir, root=True)
