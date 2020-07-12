import re

REF_LINK_PATTERN = (
    r"(?:[^!]|^)\["
    r"(?P<text>[^\]]+)"
    r"\]\("
    r"{{<[ \t]*?(?:rel)?(?:ref)?[ \t]+\""
    r"(?P<ref>[^\n\"]+?)"
    r"\"[ \t]*?>}}\)"
)


class HugoRefLinkPlugin():
    def __init__(self, markdownDir):
        self.markdownDir = markdownDir

    # some method that receives the matches and state with __file__ info
    def parse_hugo_ref_link(self, inline, m, state):
        text = m.group(1)
        ref = m.group(2)

        print('TEXT: {text} -> REF: {ref}'.format(text=text, ref=ref))

        return 'hugo_ref_link', ref, text

    def render_html_hugo_ref_link(self, link, text):
        print('render_html_hugo_ref_link')
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
