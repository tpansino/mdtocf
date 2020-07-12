def getFileContent(filepath):
    try:
        with open(filepath, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        content = ''
    return content
