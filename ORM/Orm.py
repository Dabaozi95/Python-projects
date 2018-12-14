import pymysql
#字段设置为表的类属性，使用描述器完成对数据的部分判断

class Field:
    def __init__(self,name,column=None,pk=False,unique=False,index=False,nullable=True,defult=None):
        self.name = name
        if column is None:
            self.column = name
        else:
            self.column = column
        self.pk =pk
        self.uniqe = unique
        self.index = index
        self.nullable = nullable
        self.default = defult

    def cheak(self,value):
        raise NotImplementedError

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        self.cheak(value)
        instance.__dict__[self.name] = value

    def __str__(self):
        return '{} <{}>'.format(self.__class__.__name__,self.name)
    __repr__ = __str__

class Intfield(Field):
    def __init__(self,name,column=None,pk=False,unique=False,index=False,nullable=True,defult=None,auto_increment=False):
        super().__init__(name,column,pk,unique,index,nullable,defult)
        self.auto_increment = auto_increment #增加一个是否自增

    def cheak(self,value):
        if value is None: # primary key 和 nullable=False 要求不能为空
            if self.pk:
                raise TypeError('{} is primary key,not allow None'.format(self.name))
            if not self.nullable:
                raise TypeError('{} require not None'.format(self.name))
        else:
            if not isinstance(value,int):
                raise TypeError('{} require int'.format(self.name))

class StringField(Field):
    def __init__(self,name,column=None,pk=False,unique=False,index=False,nullable=True,defult=None,auto_increment=False,length=False):
        super().__init__(name,column,pk,unique,index,nullable,defult)
        self.length = length  #str类字段增加一个长度属性

    def cheak(self,value):
        if value is None: # primary key 和 nullable=False 要求不能为空
            if self.pk:
                raise TypeError('{} is primary key,not allow None'.format(self.name))
            if not self.nullable:
                raise TypeError('{} require not None'.format(self.name))
        else:
            if not isinstance(value,str):
                raise TypeError('{} require str'.format(self.name))
        if len(value) > self.length:
            raise ValueError('{} is too long'.format(value))

class ModelMata(type): #构建元类，减少创建多表的重复代码
    def __new__(cls,what,bases,dict):
        #what类名，bases继承的类元组，dict类属性字典

        if '__tablename__' not in dict.keys():
            dict['__tablename__'] = what  #默认添加表名为类名
        mapping = {}     # 放属性名和字段实例方便查询
        primarykey = []  #联合主键
        for k,v in dict.items():  # k：类变量名（字段id） v：Intfield 实例
            if isinstance(v,Field):
                mapping[k] = v
                if v.column is None:
                    v.column = v.name
                if v.pk:
                    primarykey.append(v)
        #添加属性进入类属性字典，不止primary
        dict['__mapping__'] = mapping
        dict['__primary__'] = primarykey
        return super().__new__(cls,what,bases,dict)

class Student(metaclass=ModelMata):
    id = Intfield('id','id',pk=True,nullable=False,auto_increment=True)
    name = StringField('name',nullable=False,length=64)
    age = Intfield('age',nullable=False)

    def __init__(self,id,name,age):
        self.id = id
        self.name = name
        self.age = age

    def __str__(self):
        return 'Student({},{},{})'.format(self.id,self.name,self.age)
    __repr__ = __str__

class Teacher(metaclass=ModelMata):
    id = Intfield('id','id',pk=True,nullable=False,auto_increment=True)
    name = StringField('name',nullable=False,length=64)
    age = Intfield('age',nullable=False)

    def __init__(self,id,name,age):
        self.id = id
        self.name = name
        self.age = age

    def __str__(self):
        return 'Teacher({},{},{})'.format(self.id,self.name,self.age)
    __repr__ = __str__


class Session:
    def __init__(self,*args,**kwargs):
        self.conn = pymysql.connect(*args,**kwargs)
        self.cursor = None

    def execute(self,instance):
        if self.cursor is None:
            self.cursor = self.conn.cursor()
        names = []
        values = []
        for k, v in instance.__mapping__.items():
            names.append('`{}`'.format(k))
            values.append(instance.__mapping__[k])
        query = "insert into {} ({}) values ({})".format(instance.__tablename__,
                                                         ",".join(names),
                                                         ",".join(['%s'] * len(values)))  # 拼接query语句

        self.cursor.execute(query)

    def __enter__(self):
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        if exc_type:
            self.conn.rollback()
        else:
            self.conn.commit()

s = Student(1,'Tom',18)
session = Session('192.168.142.134','root','root','test')
session.execute()

