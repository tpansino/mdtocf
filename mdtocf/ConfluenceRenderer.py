"""Mistune v2 renderer for Confluence Storage Format (XHTML)

Used by ConfluencePublisher class to parse Markdown using
mistune v2 and convert it to Confluence XHTML Storage Format.

"""

import base64
import json

from .HTMLCommentPlugin import render_inline_html_comment, render_block_html_comment
from mistune import HTMLRenderer
from urllib.parse import urlparse


def generate_autoindex():
    return """
    <ac:structured-macro ac:name="children">
        <ac:parameter ac:name="sort">title</ac:parameter>
        <ac:parameter ac:name="depth">2</ac:parameter>
        <ac:parameter ac:name="all">true</ac:parameter>
    </ac:structured-macro>
    """


class ConfluenceRenderer(HTMLRenderer):

    def __init__(self, verbose=False, escape=True,
                 allow_harmful_protocols=None):
        self.verbose = verbose
        super(ConfluenceRenderer, self).__init__(
            escape, allow_harmful_protocols)

    def admonition(self, text, name, title=None):
        supported_names = {
            "attention": "note",
            "caution": "warning",
            "danger": "warning",
            "error": "warning",
            "hint": "tip",
            "important": "info",
            "info": "info",
            "note": "note",
            "tip": "tip",
            "warning": "warning",
        }

        return \
            '<ac:structured-macro ac:name="' + supported_names[name] + '">' \
            + '<ac:parameter ac:name="icon">true</ac:parameter>' \
            + '<ac:parameter ac:name="title">' \
            + (title.strip() if title
                else name.title()) \
            + '</ac:parameter>' \
            + '<ac:rich-text-body>' \
            + '<p>' + text.strip() + '</p>' \
            + '</ac:rich-text-body>' \
            + '</ac:structured-macro>'

    def block_code(self, code, info=None):
        if self.verbose:
            print(f"block code (lang): {info}")
        if info and 'mermaid' in info:
            # Generate Payload for mermaid.ink Request
            payload = json.dumps({
                'code': code,
                'mermaid': '{"theme":"default"}'
            }).encode('utf-8')
            src = 'https://mermaid.ink/img/{}'.format(
                base64.b64encode(payload).decode('ascii'))

            # External Image
            return '\n<ac:image><ri:url ri:value="' \
                + src + '" /></ac:image>\n'

        return \
            '\n<ac:structured-macro ac:name="code">' \
            + '<ac:parameter ac:name="title"></ac:parameter>' \
            + '<ac:parameter ac:name="theme">Emacs</ac:parameter>' \
            + '<ac:parameter ac:name="linenumbers">true</ac:parameter>' \
            + '<ac:parameter ac:name="language">' \
            + (info.strip() if info is not None else '') \
            + '</ac:parameter>' \
            + '<ac:parameter ac:name="firstline">0001</ac:parameter>' \
            + '<ac:parameter ac:name="collapse">false</ac:parameter>' \
            + '<ac:plain-text-body><![CDATA[' \
            + code \
            + ']]></ac:plain-text-body>' \
            + '</ac:structured-macro>\n'

    def block_error(self, html):
        if self.verbose:
            print(f"block error: {html}")
        return super(ConfluenceRenderer, self).block_error(html)

    def block_html(self, html):
        if self.verbose:
            print(f"block html: {html}")
        return super(ConfluenceRenderer, self).block_html(html)

    def block_html_comment(self):
        if self.verbose:
            print(f"block html comment")
        return render_block_html_comment()

    def block_quote(self, text):
        if self.verbose:
            print(f"block quote: {text}")
        return super(ConfluenceRenderer, self).block_quote(text)

    def block_text(self, text):
        if self.verbose:
            print(f"block quote: {text}")
        return super(ConfluenceRenderer, self).block_text(text)

    def codespan(self, text):
        if self.verbose:
            print(f"codespan: {text}")
        return super(ConfluenceRenderer, self).codespan(text)

    def emphasis(self, text):
        if self.verbose:
            print(f"emphasis: {text}")
        return super(ConfluenceRenderer, self).emphasis(text)

    def heading(self, text, level):
        if self.verbose:
            print(f"heading: {level} {text}")
        return super(ConfluenceRenderer, self).heading(text, level)

    def hugo_ref_link(self, title, text=None):
        if self.verbose:
            print("hugo ref link")
        return \
            '<ac:link>' \
            + '<ri:page ri:content-title="{}" />'.format(title) \
            + '<ac:plain-text-link-body>' \
            + '<![CDATA[' \
            + '{}'.format(text if text is not None else title) \
            + ']]>' \
            + '</ac:plain-text-link-body>' \
            + '</ac:link>'

    def image(self, src, alt="", title=None):
        if self.verbose:
            print("image")
        is_external = bool(urlparse(src).netloc)
        if is_external:
            # External Image
            return '<ac:image><ri:url ri:value="' \
                + src + '" /></ac:image>'

        # Attached Image
        return '<ac:image>' \
            + '<ri:attachment ri:filename="' \
            + src + '" />' \
            + '</ac:image>'

    def inline_html(self, html):
        if self.verbose:
            print(f"inline html: {html}")
        return super(ConfluenceRenderer, self).inline_html(html)

    def inline_html_comment(self, comment):
        if self.verbose:
            print(f"inline html comment: {comment}")
        return render_inline_html_comment(comment)

    def linebreak(self):
        if self.verbose:
            print("linebreak")
        return super(ConfluenceRenderer, self).linebreak()

    def link(self, link, text=None, title=None):
        if self.verbose:
            print(f"link: {title} -> {text}")
        is_external = bool(urlparse(link).netloc)
        if is_external:
            return '<a href="' + link + '" alt="' \
                + (title if title is not None else '') + '">' \
                + (text if text is not None else link) + '</a>'

        # Attachment
        return \
            '<ac:link><ri:attachment ri:filename="' + link + '" />' \
            + '<ac:plain-text-link-body>' \
            + '<![CDATA[' \
            + (text if text is not None else 'Attachment') \
            + ']]>' \
            + '</ac:plain-text-link-body>' \
            + '</ac:link>'

    def list(self, text, ordered, level, start=None):
        if self.verbose:
            print(f"list: {level} {ordered} {text} {start}")
        return super(ConfluenceRenderer, self).list(text, ordered, level,
                                                    start)

    def list_item(self, text, level):
        if self.verbose:
            print(f"list_item: {level} {text}")
        return super(ConfluenceRenderer, self).list_item(text, level)

    def newline(self):
        if self.verbose:
            print("newline")
        return super(ConfluenceRenderer, self).newline()

    def paragraph(self, text):
        if self.verbose:
            print(f"paragraph: {text}")
        return super(ConfluenceRenderer, self).paragraph(text)

    def strong(self, text):
        if self.verbose:
            print(f"strong: {text}")
        return super(ConfluenceRenderer, self).strong(text)

    def text(self, text):
        if self.verbose:
            print(f"text: {text}")
        return super(ConfluenceRenderer, self).text(text)

    def thematic_break(self):
        if self.verbose:
            print("thematic break")
        return super(ConfluenceRenderer, self).thematic_break()
