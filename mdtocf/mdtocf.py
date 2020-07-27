"""mdtocf.py

This script convert markdown pages and publish them to confluence pages

"""
import argparse
import os
from .ConfluencePublisher import ConfluencePublisher


def environ_or_required(key):
    return (
        {'default': os.environ.get(key)} if os.environ.get(key)
        else {'required': True}
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--confluenceUsername',
                        help='e.g. "example@example.com"',
                        **environ_or_required('INPUT_CONFLUENCE-USERNAME'))
    parser.add_argument('--confluenceApiToken',
                        help='e.g. "a87D98AfDsf98dsf7AdsNfaa2"',
                        **environ_or_required('INPUT_CONFLUENCE-API-TOKEN'))
    parser.add_argument('--confluenceUrl',
                        help='e.g. "https://example.jira.com/"',
                        **environ_or_required('INPUT_CONFLUENCE-URL'))
    parser.add_argument('--confluenceSpace',
                        help='e.g. ~989819389 (Personal Space), 78712486',
                        **environ_or_required('INPUT_CONFLUENCE-SPACE'))
    parser.add_argument('--confluenceParentPageId',
                        help='e.g. "Page Information: ?pageId=1650458860',
                        **environ_or_required('INPUT_CONFLUENCE-PARENT-PAGEID')
                        )
    parser.add_argument('--confluencePageTitlePrefix',
                        required=False,
                        help='e.g. "[MyPrefix] "',
                        default='')
    parser.add_argument('--markdownDir',
                        help='e.g. "../mydocs"',
                        **environ_or_required('INPUT_MARKDOWN-DIR'))
    parser.add_argument('--dbPath',
                        required=False,
                        help='e.g. "./dbs/mydocs.db"',
                        default='./meta.db')
    parser.add_argument('--forceUpdate',
                        required=False,
                        default=False,
                        action="store_true",
                        help='default=False.' +
                        ' Force page update in Confluence')
    parser.add_argument('--forceDelete',
                        required=False,
                        default=False,
                        action="store_true",
                        help='default=False. Force page removal' +
                        ' (before update) in Confluence.')
    parser.add_argument('--skipUpdate',
                        required=False,
                        default=False,
                        action="store_true",
                        help='default=False. Skip page update' +
                        ' in Confluence')
    args = parser.parse_args()

    forceUpdate = int(args.forceUpdate) == 1
    forceDelete = int(args.forceDelete) == 1
    skipUpdate = int(args.skipUpdate) == 1

    confluencePublisher = ConfluencePublisher(
        url=args.confluenceUrl,
        username=args.confluenceUsername,
        apiToken=args.confluenceApiToken,
        pageTitlePrefix=args.confluencePageTitlePrefix,
        markdownDir=args.markdownDir,
        dbPath=args.dbPath,
        space=args.confluenceSpace,
        parentPageId=args.confluenceParentPageId,
        forceUpdate=forceUpdate,
        forceDelete=forceDelete,
        skipUpdate=skipUpdate
    )

    confluencePublisher.delete()
    if not skipUpdate:
        confluencePublisher.publish()


if __name__ == "__main__":
    main()
