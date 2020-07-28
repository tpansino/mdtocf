import re

BLOCK_HTML_COMMENT_PATTERN = re.compile((
    r"<!--(?!>|->)((?:(?!--)([\s\S]))+?)(?<!-)-->\n*"
))

INLINE_HTML_COMMENT_PATTERN = (
    r"<!--(?!>|->)((?:(?!--)([\s\S]))+?)(?<!-)-->"
)


def parse_block_html_comment(block, m, state):
    comment = m.group(1)
    return {
        'type': 'block_html_comment',
        'comment': comment,
        'blank': True,
    }


def parse_inline_html_comment(inline, m, state):
    comment = m.group(1)
    return 'inline_html_comment', comment


def render_block_html_comment():
    return ""


def render_inline_html_comment(comment):
    return ""


def plugin_html_comment(md):
    md.block.register_rule(
        'block_html_comment',
        BLOCK_HTML_COMMENT_PATTERN,
        parse_block_html_comment)

    index = md.block.rules.index('block_html')
    if index != -1:
        md.block.rules.insert(index - 1, 'block_html_comment')
    else:  # pragma: no cover
        md.block.rules.append('block_html_comment')

    if md.renderer.NAME == 'html':
        md.renderer.register('block_html_comment',
                             render_block_html_comment)

    md.inline.register_rule(
        'inline_html_comment',
        INLINE_HTML_COMMENT_PATTERN,
        parse_inline_html_comment)

    index = md.inline.rules.index('inline_html')
    if index != -1:
        md.inline.rules.insert(index - 1, 'inline_html_comment')
    else:  # pragma: no cover
        md.inline.rules.append('inline_html_comment')

    if md.renderer.NAME == 'html':
        md.renderer.register('inline_html_comment',
                             render_inline_html_comment)
