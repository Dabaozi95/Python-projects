from wsgiref.simple_server import make_server
from webob import Response,Request,exc
from Wsgi_Web import Application

product = Application.Router('/product')

Application.register(product)


@product.get('/{id:int}')
def showpython(ctx,request:Response):
    res =Response()
    res.content_type = 'text/plain'
    res.body = '<h1>好嗨哦，感觉人生已经到达了高潮~.vars ={}</h1>'.format(request.vars).encode()
    return res

@product.register_beforinterceptor
def showprefix(ctx,request:Request):
    print('prefix = {}'.format(ctx.router.prefix))
    return request

if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 9999
    server = make_server(ip,port,Application())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        server.server_close()










