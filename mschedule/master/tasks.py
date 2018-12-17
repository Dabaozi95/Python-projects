import uuid
from .state import *

class Task:
    def __init__(self,task_id,script,targets,timeout):
        self.id = task_id
        self.script = script
        self.timeout =timeout
        self.state = WAITING
        self.targets = {agent_id:{'state':WAITING,'output':""}for agent_id in targets}
        self.target_count = len(self.targets)

