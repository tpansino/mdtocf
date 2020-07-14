import sys
from mdtocf.FrontMatterPlugin import FRONT_MATTER_PATTERN


def main():
    print(sys.argv[1])

    with open(sys.argv[1], mode='r') as file:
        content = file.read()

    p = FRONT_MATTER_PATTERN

    m = p.match(content)

    if m:
        print('Match found:', m.group(1))
    else:
        print('No match')


if __name__ == "__main__":
    main()
