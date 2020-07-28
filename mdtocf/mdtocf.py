"""mdtocf.py

This script convert markdown pages and publish them to confluence pages

"""
import argparse
import os
from .ConfluencePublisher import ConfluencePublisher


def environ_bool(key, default=False):

    result = {
        'default': default
    }

    if os.environ.get(key):
        result['default'] = os.environ.get(key) is not None
    elif os.environ.get(f"INPUT_{key}"):
        result['default'] = os.environ.get(f"INPUT_{key}") is not None

    return result


def environ_string(key, default=None):

    result = {
        'metavar': key,
        'default': default
    }

    if os.environ.get(key):
        result['default'] = os.environ.get(key)
    elif os.environ.get(f"INPUT_{key}"):
        result['default'] = os.environ.get(f"INPUT_{key}")

    return result


def environ_or_required(key):

    result = {
        'metavar': key
    }

    if os.environ.get(key):
        result['default'] = os.environ.get(key)
    elif os.environ.get(f"INPUT_{key}"):
        result['default'] = os.environ.get(f"INPUT_{key}")
    else:
        result['required'] = True

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--confluence-username',
                        help='e.g. "example@example.com"',
                        **environ_or_required('CONFLUENCE_USERNAME'))
    parser.add_argument('--confluence-api-token',
                        help='e.g. "a87D98AfDsf98dsf7AdsNfaa2"',
                        **environ_or_required('CONFLUENCE_API_TOKEN'))
    parser.add_argument('--confluence-url',
                        help='e.g. "https://example.jira.com/"',
                        **environ_or_required('CONFLUENCE_URL'))
    parser.add_argument('--confluence-space',
                        help='e.g. ~989819389 (Personal Space), 78712486',
                        **environ_or_required('CONFLUENCE_SPACE'))
    parser.add_argument('--confluence-parent-pageid',
                        help='e.g. "Page Information: ?pageId=1650458860',
                        **environ_or_required('CONFLUENCE_PARENT_PAGEID'))
    parser.add_argument('--markdown-dir',
                        help='e.g. "../mydocs"',
                        **environ_or_required('MARKDOWN_DIR'))
    parser.add_argument('--confluence-page-title-prefix',
                        help='e.g. "[MyPrefix] "',
                        **environ_string('CONFLUENCE_PAGE_TITLE_PREFIX', default=''))
    parser.add_argument('--db-path',
                        help='e.g. "./dbs/mydocs.db"',
                        **environ_string('DB_PATH', default='./meta.db'))
    parser.add_argument('--force-update',
                        action="store_true",
                        help='default=False.' +
                        ' Force page update in Confluence',
                        **environ_bool('FORCE_UPDATE', default=True))
    parser.add_argument('--force-delete',
                        action="store_true",
                        help='default=False. Force page removal' +
                        ' (before update) in Confluence.',
                        **environ_bool('FORCE_DELETE', default=False))
    parser.add_argument('--skip-update',
                        action="store_true",
                        help='default=False. Skip page update' +
                        ' in Confluence',
                        **environ_bool('SKIP_UPDATE', default=False))

    args = parser.parse_args()

    force_update = int(args.force_update) == 1
    force_delete = int(args.force_delete) == 1
    skip_update = int(args.skip_update) == 1

    confluence_publisher = ConfluencePublisher(
        url=args.confluence_url,
        username=args.confluence_username,
        api_token=args.confluence_api_token,
        page_title_prefix=args.confluence_page_title_prefix,
        markdown_dir=args.markdown_dir,
        db_path=args.db_path,
        space=args.confluence_space,
        parent_pageid=args.confluence_parent_pageid,
        force_update=force_update,
        force_delete=force_delete,
        skip_update=skip_update
    )

    confluence_publisher.delete()
    if not skip_update:
        confluence_publisher.publish()


if __name__ == "__main__":
    main()
