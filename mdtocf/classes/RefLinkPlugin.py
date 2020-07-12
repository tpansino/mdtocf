import re

REF_LINK = re.compile((
    r"(?:[^!]|^)\["
    r"(?P<text>[^\]]+)"
    r"\]\("
    r"{{<[ \t]*?(?:rel)?(?:ref)?[ \t]+\""
    r"(?P<ref>[^\n\"]+?)"
    r"\"[ \t]*?>}}\)"
), re.IGNORECASE)


class RefLinkPlugin():
    def __init__(self, markdownDir):
        self.markdownDir = markdownDir

    # some method that receives the matches and state with __file__ info

    def __call__(self, md):
        pass
