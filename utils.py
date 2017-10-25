from os.path import abspath, join
from urllib.parse import urlparse
from random import choice
from string import ascii_lowercase


def inside(dir, name):
    """
    Checks whenever a given file name lies within a folder.
    """
    dir = abspath(dir)
    name = abspath(name)
    return name.startswith(join(dir, ''))


def getPort(url):
    """
    Extracts the port from a url.
    """
    name = urlparse(url)[1]
    parts = name.split(':')
    return int(parts[-1])


def randomString(length):
    """
    Returns a random string of letters with the given length.
    """
    chars = []
    while length > 0:
        length -= 1
        chars.append(choice(ascii_lowercase))
    return ''.join(chars)
