from subprocess import PIPE,Popen
from utils import getlogger

logger = getlogger(__name__,'d:/executor.log')

class Executor:
    def run(self,script,timeout=None):
        process = Popen(script,shell=True,stdout=PIPE)
        code = process.wait()  #状态码
        output = process.stdout.read() #脚本执行输出
        return code,output