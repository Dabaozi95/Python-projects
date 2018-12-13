import socket
import threading
import datetime
import logging

FORMAT= "%(asctime)s %(thread)d %(message)s"
logging.basicConfig(level=logging.INFO,format=FORMAT)

class ChatServer:
    def __init__(self,ip='127.0.0.1',port=9999):
        self.addr = (ip,port)
        self.socket = socket.socket()
        self.event = threading.Event()
        self.clients = {}

    def start(self):
        self.socket.bind(self.addr)
        self.socket.listen()
        threading.Thread(target=self._accept).start()

    def _accept(self):
        while not self.event.is_set():
            sock,client = self.socket.accept()
            self.clients[client] = sock
            threading.Thread(target=self._recv,args=(sock,client)).start()

    def _recv(self,sock:socket.socket,client):
        while not self.event.is_set():
            try:
                data = sock.recv(1024)
            except Exception as e:
                data = b'quit'
            data = data.decode()
            if data.strip() == 'quit': #客户端断开连接
                self.clients.pop(client)
                sock.close()
                break
            else:
                msg = "{:%Y/%m/%d %H:%M:%S} {}:{}\n{}\n".format(datetime.datetime.now(), *client, data)
                for c in self.clients.values():
                    c.send(msg.encode())
                    logging.info(msg)

    def stop(self):
        for sock in self.clients.values():
            sock.close()
        self.socket.close()
        self.event.set()

def show_thread(e:threading.Event):
    while not e.wait(3):
        logging.info(threading.enumerate())

def main():
    e= threading.Event()
    cs = ChatServer()
    cs.start()
    threading.Thread(target=show_thread,args=(e,)).start()
    while not e.wait(1):
        cmd = input('>>>').strip()
        if cmd == 'quit':
            cs.stop()
            e.wait(3)
            break

if __name__ == "__main__":
    main()
