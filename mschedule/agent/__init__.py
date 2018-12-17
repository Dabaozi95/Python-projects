from .cm import ConnectionManager
from .msg import Message
from .config import MASTER_URL,MY_IDPATH
import threading

class Agent:
    def __init__(self):
        self.msg = Message(MY_IDPATH)
        self.cm = ConnectionManager(MASTER_URL,self.msg)
        self.event = threading.Event()

    def start(self):
        while not self.event.is_set(): #重连
            try:
                self.cm.start()
            except Exception as e:
                self.cm.shutdown()
                self.event.wait(3)

    def shutdowm(self):
        self.event.set()
        self.cm.shutdown()