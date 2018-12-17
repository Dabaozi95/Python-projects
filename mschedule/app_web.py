from aiohttp import web,log
import zerorpc

client = zerorpc.Client()
client.connect("tcp://127.0.0.1:9999")

async def targetshandler(request:web.Request):
    agent_list = client.get_agents()   #Master接口
    return web.json_response(agent_list)

async def taskhandler(request:web.Request):
    j = await request.json()
    txt = client.add_task(j)
    return web.Response(text=txt,status=201)

app = web.Application()
app.router.add_get('/task/targets',targetshandler)
web.run_app(app,host='0.0.0.0',port=9000)
app.router.add_post('/task',taskhandler)
