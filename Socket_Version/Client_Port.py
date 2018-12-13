import socket
import threading
import datetime
import logging

FORMAT= "%(asctime)s %(thread)d %(message)s"
logging.basicConfig(level=logging.INFO,format=FORMAT)

class Chat_Client:
    def __init__(self,ip='127.0.0.1',port=9999):
        self.socket = socket.socket()
        self.addr = (ip,port)
        self.event = threading.Event()
        self.start()

    def start(self):
        self.socket.connect(self.addr)
        threading.Thread(target=self._recv).start()

    def _recv(self):
        while not self.event.is_set():
            try:
                data = self.socket.recv(1024)
            except Exception as e:
                logging.error(e)
                break

            msg = "{:%Y/%m/%d %H:%M:%S} {}:{}\n{}\n".format(datetime.datetime.now(), *self.addr, data.strip())
            logging.info(msg)

    def send(self,msg:str):
        data = "{}\n".format(msg.strip()).encode()
        self.socket.send(data)

    def stop(self):
        self.socket.close()
        self.event.wait(3)
        self.event.set()
        logging.info("{} stopped".format(self.addr))

def show_thread(e:threading.Event):
    while not e.wait(3):
        logging.info(threading.enumerate())

def main():
    e= threading.Event()
    cc = Chat_Client()
    print('-------------')
    threading.Thread(target=show_thread,args=(e,),daemon=True).start()
    while True:
        msg = input('>>>')
        if msg.strip() == 'quit':
            cc.stop()
            e.wait(3)
            break
        cc.send(msg)

if __name__ == "__main__":
    main()