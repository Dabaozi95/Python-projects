import zerorpc
from .cm import ConnectionManager
from .config import MASTER_URL


class Master:
    def __init__(self):
        self.tcpserver = zerorpc.Server(ConnectionManager())
        self.tcpserver.bind(MASTER_URL)

    def start(self):
        self.tcpserver.run()

    def shutdown(self):
        self.tcpserver.close()