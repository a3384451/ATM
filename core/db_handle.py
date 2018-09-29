import os
import json
from conf import settings
from logs.log import logger
from abc import ABC,abstractmethod


class DbHangdle(object):

    def db_choice(self):
        '''
        选择数据的存取方式
        :return: 返回选择的方法
        '''
        if settings.DATABASES['db_tool'] == 'file':
            return self.file_handle()
        if settings.DATABASES['db_tool'] == 'mysql':
            return self.mysql_handle()

    @classmethod
    def file_handle(self):
        '''
        选用文件操作数据
        :return:
        '''
        db_path = settings.DB_PATH
        return FileHandle(db_path)

    @classmethod
    def mysql_handle(self):
        '''
        选用数据库操作数据
        :return:
        '''
        pass

class Db_Base(ABC):
    '''抽象基类'''
    @abstractmethod
    def load_data(self,*args,**kwargs):
        '''
        子类必须有该方法 用于获取数据
        :return:
        '''

    @abstractmethod
    def dump_data(self,*args,**kwargs):
        '''
        子类必须有该方法 用于保存数据
        :return:
        '''

class FileHandle(Db_Base):
    '''
    处理文件数据内容
    '''
    def __init__(self,db_path):
        self.db_path=db_path

    def load_data(self,username):
        '''
        获取用户的数据
        :return:返回用户的数据
        '''

        load_data_path = '%s/%s.json'%(self.db_path,username)
        if not os.path.isfile(load_data_path):
            logger.info('获取用户文件错误')
            return None
        with open(load_data_path,'r',encoding='utf-8') as f:
            user_data = json.loads(f.read())
        if user_data:
            return user_data

    def dump_data(self,username,userinfo):
        '''
        保存数据
        :return:
        '''
        load_data_path = '%s/%s.json' % (self.db_path, username)
        if not os.path.isfile(load_data_path):
            logger.info('获取用户文件错误')
            return None
        with open(load_data_path, 'w',encoding='utf-8') as f:
            f.write(json.dumps(userinfo))
        return True

class MysqlHandle(Db_Base):
    '''
    用于扩展数据库
    '''
    pass


