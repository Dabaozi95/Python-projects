import zerorpc
from .msg import Message
import threading
from utils import getlogger
from .state import *
from .executor import Executor

logger = getlogger(__name__,'d:/agentcm.log')

class ConnectionManager:
    def __init__(self,master_url,message:Message):
        self.master_url = master_url
        self.message = message #这是一个对象,才能调实例方法
        self.client = zerorpc.Client()
        self.event = threading.Event()
        self.state = WAITING    #Agent的工作状态
        self.exe = Executor()  #脚本执行

    def start(self,timeout=5):
        try:
            self.event.clear()  #重置event
            self.client.connect(self.master_url)  #连接
            self._send(self.message.reg()) #发送注册消息

            while not self.event.wait(timeout):
                self._send(self.message.heartbeat())
                if self.state == WAITING:    #Agent等待状态主动去Master拉任务
                    self._get_task(self.message.id)

        except Exception as e:
            logger.error('Failed connect master. Error:{}'.format(e))
            raise e  #向外抛异常，让主线程接收并重启连接

    def _send(self,msg):
        ack = self.client.sendmsg(msg)  #sendmsg为master的接口
        logger.info(ack)

    def shutdown(self):
        self.event.set()
        self.client.close()

    def _get_task(self,agent_id):
        task = self.client.take_task(self.message.id)
        if task:
            self.state = RUNNING  #拿到任务变更为运行状态
            #{'id':task_id,'script':task.script,'timeout':task.timeout}
            script = task['script']
            code,output = self.exe.run(script,task.timeout)   #调用Executor执行器，执行脚本
            self._send(self.message.result(task['id'],code,output))
            self.state = WAITING  #执行完成变更为等待状态