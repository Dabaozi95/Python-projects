from webob import Request,Response,exc
from webob.dec import wsgify
import re

class Dictobj: #把字典对象化，方便用.来访问属性
    def __init__(self,d:dict):
        if isinstance(d,dict):
            self.__dict__['_dict'] = d
        else:
            self.__dict__['_dict'] = {}

    def __getattr__(self, item):
        try:
            return self.__dict[item]
        except KeyError:
            raise AttributeError('AttributeError {} Not Found'.format(item))

    def __setattr__(self, key, value):
        raise NotImplementedError

class Context(dict): #为Application提供一个全局字典来进行全局共享数据
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError('AttributeError {} Not Found'.format(item))

    def __setattr__(self, key, value):
        self[key] = value

class NestedContext(Context): #Router的实例上下文字典
    def __init__(self,globalcontext:Context=None):
        super().__init__()
        self.relate(globalcontext)

    def relate(self,globalcontext:Context=None): #给实例绑定全局字典
        self.globalcontext = globalcontext

    def __getattr__(self, item):
        if item in self.keys():
            return self[item]
        return self.globalcontext[item]

class _Router:
    TYPEPATTERNS = {
        'str': r'[^/]+',
        'word': r'\w+',
        'int': r'[+-]?\d+',
        'float': r'[+-]?\d+\.\d+',
        'any': r'.+'
    }

    TYPECAST = {
        'str': str,
        'word': str,
        'int': int,
        'float': float,
        'any': str
    }
    KVPATTERN = re.compile(r'/({[^{}:]+:?[^{}:]*})')  # /stdudent/{name:str}/{id:int} -> /stdudent/(?P<name>:[^/]+)/(?P<id>[+-]?\d+)

    def _transform(self, kv: str=""):
        name, _, type = kv.strip('/{}').partition(':')
        return '/(?P<{}>{})'.format(name, self.TYPEPATTERNS.get(type,'\w+')), name, self.TYPECAST.get(type, str)

    def _parse(self, src:str):
        startpos = 0
        res = ''
        translator = {}  # 用来存URL类型
        while True:
            matcher = self.KVPATTERN.search(src, startpos)
            if matcher:
                res += matcher.string[startpos:matcher.start()]  # 取出前缀
                tmp = self._transform(matcher.string[matcher.start():matcher.end()])  # 匹配部分拿去URL转换正则

                res += tmp[0]
                translator[tmp[1]] = tmp[2]
                startpos = matcher.end()
            else:
                break
        if res:
            return res, translator
        else:
            return src, translator

    def __init__(self,prefix:str=""):
        self.__prefix = prefix.rstrip('/\\')
        self.__routeable = []   #路由表

        self.befor_interceptor = []  #拦截器
        self.after_interceptor = []

        self.ctx = NestedContext()  #实例上下文字典

    @property
    def prefix(self):
        return self.__prefix

    def register_beforinterceptor(self,fn):
        self.befor_interceptor.append(fn)
        return fn

    def register_afterinterceptor(self,fn):
        self.after_interceptor.append(fn)
        return fn

    def route(self,rule,*methods):
        def wrapper(handler):
            pattern,translator = self._parse(rule)
            self.__routeable.append((methods,re.compile(pattern),translator,handler))
            return handler
        return wrapper

    def get(cls,pattern):
        return cls.route(pattern,'GET')

    def post(cls,pattern):
        return cls.route(pattern,'POST')

    def match(self,request:Request) -> Response:
        if not request.path.startswith(self.__prefix):
            return None

        for fn in self.befor_interceptor:
            request = fn(self.ctx,request)

        for methods,pattern,translator,handler in self.__routeable:
            if not methods or request.method.upper() in methods:
                matcher = pattern.match(request.path.replace(self.__prefix,'',1))
                if matcher:
                    newdict = {}
                    for k,v in matcher.groupdict().items(): #命名分组的字典
                        newdict[k] = translator[k](v)
                    request.vars = Dictobj(newdict)

                    response = handler(self.ctx,request) #增加上下文
                    for fn in self.after_interceptor:
                        response = fn(self.ctx,request,response)
                    return response

class Application:
    Router = _Router
    Request = Request
    Response = Response

    ctx = Context()
    def __init__(self,**kwargs):
        self.ctx.app = self
        for k,v in kwargs:
            self.ctx[k] = v

    ROUTERS = []

    BEFOR_INTERCEPTOR = []
    AFTER_INTERCEPTOR = []

    @classmethod
    def register_beforinterceptor(cls,fn):
        cls.BEFOR_INTERCEPTOR.append(fn)
        return fn

    @classmethod
    def register_afterinterceptor(cls,fn):
        cls.AFTER_INTERCEPTOR.append(fn)
        return fn

    @classmethod
    def register(cls,router:Router):
        router.ctx.relate(cls.ctx)  #注册Router实例时注入全局上下文
        router.ctx.router = router
        cls.ROUTERS.append(router)

    @wsgify
    def __call__(self,request:Request):
        for fn in self.BEFOR_INTERCEPTOR:
            request = fn(self.ctx,request)

        for router in self.ROUTERS:
            response = router.match(request)

            for fn in self.AFTER_INTERCEPTOR:
                response = fn(self.ctx,request,response)
            if response:
                return response
        raise exc.HTTPNotFound('<h1>你访问的页面被外星人劫持了</h1>')