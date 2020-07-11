"""Mistune v2 Plugin for Reading Markdown Front Matter

Used by ConfluenceRenderer to enable the parsing of all front matter.

"""
import re
import yaml


FRONT_MATTER_PATTERN = re.compile((
    r'(?:---\n)'
    r'(?P<front_matter>[\s\S]+?)'
    r'(?:\n---)'
), flags=re.I)

FRONT_MATTER_REQUIRED_FIELDS = [
    'title',
]


class FrontMatterMissingError(Exception):
    pass


class FrontMatterParsingError(Exception):
    def __init__(self, yaml_error):
        self.yaml_error = yaml_error


class FrontMatterRequireFieldMissingError(Exception):
    def __init__(self, field):
        self.field = field


def parse_front_matter(md, s, state):
    m = FRONT_MATTER_PATTERN.match(s)

    if m:
        # parse front matter
        front_matter = m.groupdict()['front_matter']

        try:
            front_matter = yaml.load(front_matter)
        except yaml.YAMLError as e:
            raise FrontMatterParsingError(e)

        # check for required fields
        for required in FRONT_MATTER_REQUIRED_FIELDS:
            if required not in front_matter.keys():
                raise FrontMatterRequireFieldMissingError(required)

        # store front matter in state
        state['front_matter'] = front_matter

        # strip front matter from 's'
        markdown = s[m.end()+1:]

        return markdown, state
    else:
        raise FrontMatterMissingError()


def plugin_front_matter(md):
    md.before_parse_hooks.append(parse_front_matter)
