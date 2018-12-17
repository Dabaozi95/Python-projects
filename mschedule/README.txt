
此次mshecudle主要完成类似ansible的任务调度功能
整个流程由3部分组成，Web、Master、Agent

Agent部分：
	1、cm模块负责连接，发送注册、心跳、任务执行结果信息以及拉任务
	2、msg模块负责为cm模块提供三种信息的获取
	3、executor模块负责执行cm模块获取到的任务中的脚本

Master部分：
	1、cm模块负责为Agent端与Web提供接口，接收信息以及Agent的任务请求
	2、storge模块负责存储Agent信息、Web端发来的任务信息，以及在Agent请求任务时查找是否存在对应的任务
	

注册消息
{	
   "type":"register",
   "payload":{
	 "id":"uuid",
	 "hostname":"xxx",
	 "ip":[]
   }
}

心跳信息
{	
   "type":"heartbeat",
   "payload":{
	 "id":"uuid",
	 "hostname":"xxx",
	 "ip":[]
   }
}


Master端存的Agent端数据结构

{
   "agent":{
	  "agent_id":{
		"heartbeat":"timestamp"
		"busy":"WAITING"            
		"info":{
		  "hostname":""
		  "ip":[]
		}
	  }
    }
}



Web端存的Task信息
{
  "tasks":{
    "task_id":{
	  "script":"base64encode",
	  "targets":{
	    "agent_id":{
		  "state":WAITING,
		  "output":""
		}
	  },
	  "state":"WAITING"
	}
  }
}























