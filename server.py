from xmlrpc.client import ServerProxy, Fault
from os.path import join, abspath, isfile
from xmlrpc.server import SimpleXMLRPCServer
from urllib.parse import urlparse
import sys

SimpleXMLRPCServer.allow_reuse_address = 1

MAX_HISTORY_LENGTH = 6

UNHANDLED = 100
ACCES_DENIED = 200

class UnhandledQuery(Fault):
    def __init__(self, message="Couldn't handle the query"):
        super().__init__(UNHANDLED, message)

class AccessDenied(Fault):
    def __init__(self, message="Access denied"):
        super().__init__(ACCES_DENIED, message)

def inside(dir, name):
    dir = abspath(dir)
    name = abspath(name)
    return name.startswith(join(dir, ''))

def getPort(url):
    name = urlparse(url)[1]
    parts = name.split(':')
    return int(parts[-1])


class Node:
    def __init__(self, url, dirname, secret):
        self.url = url
        self.dirname = dirname
        self.secret = secret
        self.known = set()

    def query(self, query, history=[]):
        try:
            return self._handle(query)
        except UnhandledQuery:
            history = history + [self.url]
            if len(history) >= MAX_HISTORY_LENGTH: raise
            return self._broadcast(query, history)

    def hello(self, other):
        self.known.add(other)
        return 0

    def fetch(self, query, secret):
        if secret != self.secret: 
            raise AccessDenied

        result = self.query(query)
        code, data = self.query(query)
        if code == OK:
            f = open(join(self.dirname, query), 'w')
            f.write(data)
            f.close()
            return 0

    def _start(self):
        s = SimpleXMLRPCServer(('', getPort(self.url)), logRequests=False)
        s.register_instance(self)
        s.serve_forever()

    def _handle(self, query):
        dir = self.dirname
        name = join(dir, query)
        if not isfile(name): 
            raise UnhandledQuery
        if not inside(dir, name):
            raise AccessDenied

        return open(name).read()

    def _broadcast(self, query, history):
        for other in self.known.copy():
            if other in history: continue
            try:
                s = ServerProxy(other)
                return s.query(query, history)
            except Fault as f:
                if f.faultCode == UNHANDLED: pass
                else:
                    self.known.remove(other)
        raise UnhandledQuery
        
def main():
    url, directoty, secret = sys.argv[1:]
    n = Node(url, directoty, secret)
    n._start()

if __name__ == '__main__':
    main()