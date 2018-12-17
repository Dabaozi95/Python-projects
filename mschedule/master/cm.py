from utils import getlogger
from .storage import Storage
from .state import *
import uuid

logger = getlogger(__name__,'d:/mastercm.log')

class ConnectionManager:
    def __init__(self):
        self.store = Storage()

    def handle(self,msg):
        try:
            if msg['type'] in ('reg','heartbeat'):
                payload = msg['payload']
                info = {'hostname':payload['hostname'],'ip':payload['ip']}
                self.store.reg_hb(payload['id'],info)
                return "ack {}".format(msg)

            elif msg['type'] == 'result':
                payload = msg['payload']
                agent_id = payload['agent_id']
                task_id = payload['id']
                state = SUCCEED if payload['output']==0 else FAILED
                output = payload['output']

                task = self.store.get_task_by_agentid(task_id)
                t = task.targets[agent_id]
                t.state = state
                t.output = output
                return 'ack result'

        except Exception as e:
            logger.error("{}".format(e))
            return "Bad Request"

    sendmsg = handle  #zerorpc接口

    def get_agents(self):    #暴露给Web的接口，查询已注册的Agent列表
        return self.store.get_agents()

    def add_task(self,task): #Web添加任务的接口
        task['task_id'] = uuid.uuid4().hex
        return self.store.add_task(task)


    def take_task(self,agent_id):   #有属于对应Agent的任务就返回任务，没有就返回None
        # {'id':task_id,'script':task.script,'timeout':task.timeout}
        info = self.store.get_task_by_agentid(agent_id)
        if info:
            task,target = info
            task.state = RUNNING           #拿到任务将任务状态以及对应的Agent状态变更为RUNNING
            target['state'] = RUNNING
            return {
                'id':task.id,
                'script':task.script,
                'timeout':task.timeout
            }







