import time
import os
from conf import settings
from functools import wraps
from logs.log import logger
from core.db_handle import DbHangdle

class Auth(object):

    db_handle = DbHangdle().db_choice()
    def access_auth(self,username,password):
        '''
        用于验证是否登录成功
        :param username: 用户输入的用户名
        :param password: 用户输入的面膜
        :return: 返回字典,包含用户信息,是否登录成功
        '''
        user_info = {'status':False,'msg':None}

        user_data = self.db_handle.load_data(username)

        if not user_data:
            user_info['msg'] = '找不到该文件'
            print('找不到该文件')
            return user_info

        if user_data['status'] == 1:
            user_info['msg'] ='该用户被冻结'
            return user_info

        if user_data['password'] != password:
            user_info['msg'] ='密码错误'
            return user_info

        expire_time = time.mktime(time.strptime(user_data['expire_date'],'%Y-%m-%d'))
        if time.time() > expire_time:
            user_info['msg'] = '该用户已经过期'
            return user_info

        user_info['status'] =True
        user_info['msg'] = '登录成功'
        user_info['user_data'] = user_data
        logger.info('%s login success'%(username))
        return user_info

    def access_login(self):
        '''
        登录验证
        :return:返回登录成功后的用户信息
        '''
        user_login_count={}
        flag = True
        while flag:
            username=input('输入你的用户名:').strip()
            password = input('请输入你的密码:').strip()

            #校验是否存在该用户
            is_user = self.user_register(username)
            if not is_user:
                print('该用户不存在')
            else:
                user_info=self.access_auth(username,password)
                 #如果登录不成功

                if not user_info['status']:
                    logger.info('{}{}'.format(username,user_info['msg']))
                    print(user_info['msg'])

                    if username not in user_login_count.keys():
                        user_login_count[username]=0

                    user_login_count[username]+=1
                    if user_login_count[username] >=3:
                        flag=False
                        self.frozen_user(username)
                else:
                    return user_info

    def user_register(self,username):
        '''
        校验该用户是否已经注册
        :param username: 用户名
        :return: 返回布尔值
        '''
        is_user=False
        for item in os.listdir(settings.DB_PATH):
            if username + '.json' == item:
                is_user = True
        return is_user

    def frozen_user(self,username):
        '''
        冻结用户操作
        :param username: 用户账号
        :return:
        '''
        user_data = self.db_handle.load_data(username)
        user_data['status'] = 1
        result = self.db_handle.dump_data(username,user_data)
        if result:
            logger.info('%s 被冻结了'%username)

def check_login(func):
    '''装饰器 检查用户是否登录'''
    @wraps(func)
    def inner(cls_obj,*args,**kwargs):
        if not cls_obj.auth_data:
            return
        ret=func(cls_obj,*args,**kwargs)
        return ret
    return inner


