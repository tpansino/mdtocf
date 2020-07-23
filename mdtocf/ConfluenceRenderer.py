"""Mistune v2 renderer for Confluence Storage Format (XHTML)

Used by ConfluencePublisher class to parse Markdown using
mistune v2 and convert it to Confluence XHTML Storage Format.

"""

import base64
import json
import mistune
import re

from urllib.parse import urlparse

REF_REGEX = re.compile(
    r"{{<\s*?(?:rel)?(?:ref)?\s+\"(?P<ref>.*)\"\s*?>}}", re.IGNORECASE)


class ConfluenceRenderer(mistune.HTMLRenderer):
    def image(self, src, alt="", title=None):
        is_external = bool(urlparse(src).netloc)
        if is_external:
            # External Image
            return '<ac:image><ri:url ri:value="' \
                + src + '" /></ac:image>'
        else:
            # Attached Image
            return '<ac:image>' \
                + '<ri:attachment ri:filename="' \
                + src + '" />' \
                + '</ac:image>'

    def hugo_ref_link(self, title, text=None):
        return \
            '<ac:link>' \
            + '<ri:page ri:content-title="{}" />'.format(title) \
            + '<ac:plain-text-link-body>' \
            + '<![CDATA[' \
            + '{}'.format(text if text is not None else title) \
            + ']]>' \
            + '</ac:plain-text-link-body>' \
            + '</ac:link>'

    def link(self, link, text=None, title=None):
        is_external = bool(urlparse(link).netloc)
        if is_external:
            return '<a href="' + link + '" alt="' \
                + (title if title is not None else '') + '">' \
                + (text if text is not None else link) + '</a>'
        else:
            # Attachment
            return \
                '<ac:link><ri:attachment ri:filename="' + link + '" />' \
                + '<ac:plain-text-link-body>' \
                + '<![CDATA[' \
                + (text if text is not None else 'Attachment') \
                + ']]>' \
                + '</ac:plain-text-link-body>' \
                + '</ac:link>'

    def block_code(self, code, info=None):
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
        else:
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

    def admonition(self, text, name, title=None):
        SUPPORTED_NAMES = {
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
            '<ac:structured-macro ac:name="' + SUPPORTED_NAMES[name] + '">' \
            + '<ac:parameter ac:name="icon">true</ac:parameter>' \
            + '<ac:parameter ac:name="title">' \
            + (title.strip() if title is not None and len(title)
                else name.title()) \
            + '</ac:parameter>' \
            + '<ac:rich-text-body>' \
            + '<p>' + text.strip() + '</p>' \
            + '</ac:rich-text-body>' \
            + '</ac:structured-macro>'

    def generate_autoindex(self):
        return '<ac:structured-macro ac:name="children" />'
