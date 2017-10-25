"""
This is a simple peer-to-peer file sharing program.

Example:

    You can use the program as following:

        python client.py urls.txt directory http://server.name:{portNumber}
"""

from xmlrpc.client import ServerProxy, Fault
from cmd import Cmd
from server import Node, UNHANDLED
from threading import Thread
from time import sleep
from utils import randomString
import sys

HEAD_START = 0.1
SECRET_LENGTH = 100


class Client(Cmd):
    """
    A simple text-based interface to the node class.
    """
    prompt = '> '

    def __init__(self, url, dirname, urlfile):
        super().__init__()
        self.secret = randomString(SECRET_LENGTH)
        n = Node(url, dirname, self.secret)
        t = Thread(target=n._start)
        t.setDaemon(1)
        t.start()
        sleep(HEAD_START)
        self.server = ServerProxy(url)
        with open(urlfile) as input:
            for line in input:
                line = line.strip()
                self.server.hello(line)

    def do_fetch(self, arg):
        try:
            self.server.fetch(arg, self.secret)
        except Fault as f:
            if f.faultCode != UNHANDLED:
                raise
            print("Couldn't find the file ", arg)

    def do_exit(self, arg):
        print("Exiting program...")
        sys.exit()


def main():
    urlfile, directory, url = sys.argv[1:]
    client = Client(url, directory, urlfile)
    client.cmdloop()


if __name__ == '__main__':
    main()
