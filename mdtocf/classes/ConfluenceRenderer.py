"""Mistune v2 renderer for Confluence Storage Format (XHTML)

Used by ConfluencePublisher class to parse Markdown using
mistune v2 and convert it to Confluence XHTML Storage Format.

"""

import mistune

from urllib.parse import urlparse


class ConfluenceRenderer(mistune.HTMLRenderer):

    def __init__(self, confluenceUrl=None):
        self.confluenceUrl = confluenceUrl
        super().__init__(self)

    def image(self, src, alt="", title=None):
        if src.find('/') == -1:
            # Attached Image
            return '<ac:image>' + '<ri:attachment ri:filename="' \
                   + src + '" />' + '</ac:image>'
        else:
            # External Image
            return '<ac:image><ri:url ri:value="' + src + '" /></ac:image>'

    def link(self, link, text=None, title=None):
        is_external = bool(urlparse(link).netloc)
        if is_external:
            return '<a href="' + link + '" alt="' \
                + (title if title is not None else '') + '">' \
                + (text if text is not None else link) + '</a>'
        else:
            if link.lower().endswith('.md'):
                # Reference to Another Markdown Page
                pass
            else:
                # Attachment
                return \
                    '\n<ac:link><ri:attachment ri:filename="' + link + '" />' \
                    + '<ac:plain-text-link-body>' \
                    + '<![CDATA[' \
                    + (text if text is not None else 'Attachment') \
                    + ']]>' \
                    + '</ac:plain-text-link-body>' \
                    + '</ac:link>\n'

    def block_code(self, code, info=None):
        return \
            '\n<ac:structured-macro ac:name="code">' \
            + '<ac:parameter ac:name="title"></ac:parameter>' \
            + '<ac:parameter ac:name="theme">Emacs</ac:parameter>' \
            + '<ac:parameter ac:name="linenumbers">true</ac:parameter>' \
            + '<ac:parameter ac:name="language">' \
            + (info.strip() if info is not None else '')+'</ac:parameter>' \
            + '<ac:parameter ac:name="firstline">0001</ac:parameter>' \
            + '<ac:parameter ac:name="collapse">false</ac:parameter>' \
            + '<ac:plain-text-body><![CDATA['+code+']]></ac:plain-text-body>' \
            + '</ac:structured-macro>\n'

    def generate_autoindex(self):
        return '<ac:structured-macro ac:name="children" />'
