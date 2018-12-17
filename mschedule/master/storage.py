import datetime
from .tasks import Task
from .state import *

class Storage:
    def __init__(self):
        self.agents = {}
        self.tasks = {}

    def reg_hb(self,agent_id,info):
        self.agents['agent_id'] ={
            'heartbeat':datetime.datetime.now(),
            'info':info,
            'busy':self.agents.get(agent_id,{}).get('busy',False)
        }

    def get_agents(self):  #返回所有Agent
        return list(self.agents.keys())

    def add_task(self,task:dict):
        t = Task(**task)
        self.tasks[t.id] = t
        return t.id

    def iter_task(self,state={WAITING,RUNNING}):
        yield from (task for task in self.tasks.values() if task.state in state)

    def get_task_by_agentid(self,agent_id,state=WAITING):
        for task in self.iter_task():
            # {agent_id:{'state':WAITING,'output':""}}
            if agent_id in task.targets.keys():
                t = task.targets.get(agent_id)
                if t.get('state') == state:
                    return task      #根据agent_id查找任务，没有返回None