import mistune

class ConfluenceRenderer(mistune.HTMLRenderer):

    def __init__(self, confluenceUrl=None):
        self.confluenceUrl=confluenceUrl
        super().__init__(self)

    def image(self, src, alt="", title=None):
        if src.find('/') == -1:
            # Attached Image
            return '<ac:image>' + '<ri:attachment ri:filename="' + src + '" />'  + '</ac:image>'
        else:
            # External Image
            return '<ac:image><ri:url ri:value="' + src +'" /></ac:image>'

    def link(self, link, text=None, title=None):
        if link.find('/') == -1:
            return \
                '\n<ac:link><ri:attachment ri:filename="' + link + '" />' \
                + '<ac:plain-text-link-body>' \
                + '<![CDATA[Link to a Confluence Attachment]]>' \
                + '</ac:plain-text-link-body>' \
                + '</ac:link>\n'
        else:
            return '<a href="' + link + '" alt="' + (title if title!=None else '') + '">' + (text if text!=None else link) + '</a>'

    def block_code(self, code, info=None):
        return \
            '\n<ac:structured-macro ac:name="code">' \
            + '<ac:parameter ac:name="title">Snippet</ac:parameter>' \
            + '<ac:parameter ac:name="theme">Emacs</ac:parameter>' \
            + '<ac:parameter ac:name="linenumbers">true</ac:parameter>' \
            + '<ac:parameter ac:name="language">'+(info.strip() if info!=None else '')+'</ac:parameter>' \
            + '<ac:parameter ac:name="firstline">0001</ac:parameter>' \
            + '<ac:parameter ac:name="collapse">false</ac:parameter>' \
            + '<ac:plain-text-body><![CDATA['+mistune.escape(code)+']]></ac:plain-text-body>' \
            + '</ac:structured-macro>\n'