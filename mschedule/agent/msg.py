import socket,netifaces
import logging,os,uuid
from utils import getlogger

class Message:
    def __init__(self,myid_path):
        if os.path.exists(myid_path):
            with open(myid_path) as f:
                self.id = f.readline()
        else:
            self.id = uuid.uuid4().hex
            with open(myid_path,'w') as f:
                f.write(self.id)

    def _get_addresses(self):
        '''取接口可用的IPV4地址'''
        addresses = []
        for interface in netifaces.interface():
            if 2 in netifaces.ipaddresses(interface).keys:
                for ip in netifaces.ipaddresses(interface)[2]:
                    ip = ipaddress.ip_address(ip['addr'])
                    if ip.version != 4:
                        continue
                    if ip.is_link_local:  # 169.254地址
                        continue
                    if ip.is_lookback:  # 回环地址
                        continue
                    if ip.is_multicast:  # 多播地址
                        continue
                    if ip.is_reserved:  # 保留地址
                        continue
                    addresses.append(ip)
        return addresses

    def reg(self):
        '''生成向Master发送的注册消息'''
        return {
            'type': 'reg',
            'payload': {
                'id': self.id,
                'hostname': socket.gethostname(),
                'ip': self._get_addresses()
            }
        }

    def heartbeat(self):
        return {
            'type': 'heartbeat',
            'payload': {
                'id': self.id,
                'hostname': socket.gethostname(),
                'ip': self._get_addresses()
            }
        }

    def result(self,task_id,code,output):
        return {
            'type': 'result',
            'payload': {
                'id': task_id,
                'agent_id': self.id,
                'code': code,
                'output':output
            }
        }