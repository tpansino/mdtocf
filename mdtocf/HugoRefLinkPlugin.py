import os
import yaml

from .utilities import getFileContent
from .FrontMatterPlugin import FRONT_MATTER_PATTERN

REF_LINK_PATTERN = (
    r"(?:[^!]|^)\["
    r"(?P<text>[^\]]+)"
    r"\]\("
    r"{{<[ \t]*?(?:rel)?(?:ref)?[ \t]+\""
    r"(?P<ref>[^\n\"]+?)"
    r"\"[ \t]*?>}}\)"
)


class HugoRefLinkTargetTitleNotFoundError(Exception):
    def __init__(self, target):
        self.target = target


class HugoRefLinkTargetNotFoundError(Exception):
    def __init__(self, source, target):
        self.source = source
        self.target = target


def get_front_matter_title(filepath):
    content = getFileContent(filepath)

    m = FRONT_MATTER_PATTERN.match(content)
    if m:
        front_matter = yaml.load(m.group(1), Loader=yaml.SafeLoader)
        if 'title' in front_matter.keys():
            return front_matter['title']

    # default to filepath of target if no title found
    raise HugoRefLinkTargetTitleNotFoundError(filepath)


class HugoRefLinkPlugin():
    def __init__(self, markdown_dir):
        self.markdown_dir = markdown_dir

    # some method that receives the matches and state with __file__ info
    def parse_hugo_ref_link(self, inline, m, state):
        text = m.group(1)
        ref = m.group(2)
        source = state['__file__']
        source_dir = os.path.dirname(source)

        destination = ''

        # relative or absolute path
        if ref.startswith('/'):
            destination = os.path.join(self.markdown_dir, ref[1:])
        else:
            destination = os.path.join(source_dir, ref)

        if os.path.exists(destination):
            # link to directory
            if os.path.isdir(destination):
                # check for _index.md
                index_md = os.path.join(destination, '_index.md')
                if os.path.exists(index_md):
                    title = get_front_matter_title(index_md)
                else:
                    # auto index
                    title = os.path.basename(destination).title()
            else:
                # link to *.md
                title = get_front_matter_title(destination)
        else:
            # link to page that doesn't exist
            print(os.getcwd())
            raise HugoRefLinkTargetNotFoundError(source, destination)

        return 'hugo_ref_link', title, text

    def render_html_hugo_ref_link(self, link, text):
        return '<a href="' + link + '">' + text + '</a>'

    def __call__(self, md):
        md.inline.register_rule(
            'hugo_ref_link',
            REF_LINK_PATTERN,
            self.parse_hugo_ref_link)

        index = md.inline.rules.index('inline_html')
        if index != -1:
            md.inline.rules.insert(index + 1, 'hugo_ref_link')
        else:  # pragma: no cover
            md.inline.rules.append('hugo_ref_link')

        if md.renderer.NAME == 'html':
            md.renderer.register(
                'hugo_ref_link',
                self.render_html_hugo_ref_link)
