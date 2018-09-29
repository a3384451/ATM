from core import auth
from logs.log import logger
from core.auth import check_login
from conf.settings import OPERA_LIST
from core.calculate import AtmCalculate
from core.db_handle import DbHangdle
class ATM(object):
    '''
    atm的主要功能
    '''

    db_handle = DbHangdle().db_choice()
    atm_calculate= AtmCalculate()
    cls_auth = auth.Auth()

    def __call__(self, *args, **kwargs):
        '''进入主程序入口'''
        auth_data = self.cls_auth.access_login()
        if  auth_data['status']:
            print('登录成功')
            # 如果登录成功,将信息获取到self中
            try:
                self.auth_data=auth_data['user_data']
                self.username=self.auth_data['username']
            except KeyError as e:
                logger.warning('进入主程序入口KeyError')
            self.interactive()

    @check_login
    def account_info(self):
        '''
        查看账户信息
        :return:
        '''
        try:
            account_info= ['------%s 账户信息------'%(self.auth_data['real_name']),
                           '账户余额: %.2f元'%self.auth_data['balance'],
                           '信用金额: %.2f元'%self.auth_data['credit'],
                           '过期时间: %s'%self.auth_data['expire_date'],
                           '未还金额: %.2f'%self.auth_data['debts'],
                           '还款时间: %s天' % self.auth_data['pay_day'],
                           ]
            print('\n'.join(account_info))
        except KeyError as e:
            print('获取失败')
            logger.warning('查看账户信息key值获取失败')

    @check_login
    def repay(self):
        '''
        还款
        :return:
        '''
        while True:
            repay_number = input('请输入还款金额: ')
            # 对用户输入的内容进行校验
            if repay_number.lower() =='q':
                return

            if not repay_number.isdigit():
                print('请输入数字')
                continue

            repay_number= float(repay_number)
            try:
                balance = self.auth_data['balance']
                debts = self.auth_data['debts']
            except KeyError as e:
                logger.warning('还款KeyError')
                return

            if repay_number > debts:
                print('还款金额大于未还款金额')
                continue
            if repay_number > balance:
                print('余额不足')
                continue

            # 计算还款金额并保存
            try:
                after_balance_money = self.atm_calculate.dispatch('drop',balance,repay_number)
                self.auth_data['balance'] = after_balance_money
                print('after_balance_money',after_balance_money)
                after_debts_money = self.atm_calculate.dispatch('drop',debts,repay_number)
                self.auth_data['debts'] = after_debts_money

            except KeyError as e :
                logger.warning('还款KeyError')
                return
            except Exception as e:
                logger.warning('还款%s'%str(e))
                return

            ret = self.db_handle.dump_data(self.username,self.auth_data)
            if ret:
                print('成功还款%.2f元' % float(repay_number))
                logger.info('%s 还款 %.2f元' % (self.username, float(repay_number)))
                return
            else:
                print('还款失败')
                logger.warning('还款失败')
                reduce_balance=self.db_handle.load_data(self.username).get('balance')
                self.auth_data['balance'] = reduce_balance
                return

    @check_login
    def deposit(self):
        '''
        存款
        :return:
        '''
        while True:
            deposit_number = input('请输入存款金额: ')

            if deposit_number.lower() =='q':
                return
            if not deposit_number.isdigit():
                print('请输入数字: ')
                continue

            try:
                balance = self.auth_data['balance']
                after_add_money=self.atm_calculate.dispatch('save',balance,float(deposit_number))
                self.auth_data['balance'] = after_add_money
            except KeyError as  e:
                logger.warning('存款方法中金额获取失败')
            except Exception as e:
                logger.warning('存款方法%s'%str(e))

            ret = self.db_handle.dump_data(self.username,self.auth_data)
            if ret :
                print('成功存款%.2f元'%float(deposit_number))
                logger.info('%s 存款 %.2f元'%(self.username,float(deposit_number)))
                return
            else:
                print('存款失败')
                logger.warning('存款失败')
                reduce_balance = self.db_handle.load_data(self.username).get('balance')
                self.auth_data['balance'] = reduce_balance
                return

    @check_login
    def withdraw(self):
        '''
        取款
        :return:
        '''
        while True:
            withdraw_number = input('请输入还款金额: ')
            # 对用户输入的内容进行校验
            if not withdraw_number.isdigit():
                print('请输入数字')
                continue
            if withdraw_number.lower() =='q':
                return
            withdraw_number= float(withdraw_number)
            try:
                balance = self.auth_data['balance']
            except KeyError as e:
                logger.warning('还款KeyError')
                return

            if withdraw_number > balance:
                print('余额不足')
                continue
            try:
                after_balance_money = self.atm_calculate.dispatch('drop',balance,withdraw_number)
                self.auth_data['balance'] = after_balance_money

            except KeyError as e :
                logger.warning('取款KeyError')
                return
            except Exception as e:
                logger.warning('取款%s'%str(e))
                return

            ret = self.db_handle.dump_data(self.username,self.auth_data)
            if ret:
                print('成功取款%.2f元' % withdraw_number)
                logger.info('%s 取款 %.2f元' % (self.username, withdraw_number))
                return
            else:
                print('取款失败')
                logger.warning('取款失败')
                reduce_balance=self.db_handle.load_data(self.username).get('balance')
                self.auth_data['balance'] = reduce_balance
                return

    @check_login
    def transfer(self):
        '''
        转账
        :return:
        '''
        while True:
            transfer_user = input('请输入转账人账号: ')
            if transfer_user.lower() =='q':
                return
            user_exit = self.cls_auth.user_register(transfer_user)
            if not user_exit:
                print('该用户不存在')
                continue
            transfer_money = input('请输入转账金额: ')

            if transfer_money.lower() =='q':
                return
            if not transfer_money.isdigit():
                print('请输入数字')
                continue
            transfer_money = float(transfer_money)

            try:
                balance = self.auth_data['balance']
                transfer_user_info = self.db_handle.load_data(transfer_user)
                transfer_user_balance = transfer_user_info['balance']
            except KeyError as e:
                logger.warning('转账KeyError')
                return

            if transfer_money > balance:
                print('余额不足了')
                return

            # 如果使用事务操作会更好
            after_balance = self.atm_calculate.dispatch('drop',balance,transfer_money)
            after_tranfer_balance= self.atm_calculate.dispatch('save',transfer_user_balance,transfer_money)
            self.auth_data['balance'] = after_balance
            transfer_user_info['balance']=after_tranfer_balance

            ret = self.db_handle.dump_data(self.username,self.auth_data)
            tranfer_ret = self.db_handle.dump_data(transfer_user,transfer_user_info)

            if ret and tranfer_ret:
                logger.info('%s 转账 %.2f元 -->%s'%(self.username,transfer_money,transfer_user_info.get('username')))
                return

    @check_login
    def logout(self):
        '''
        账户退出
        :return:
        '''

        del self.auth_data
        return True
    @check_login
    def interactive(self):
        '''
        用户交互
        :return:
        '''
        while True:
            display_opare,opera_mapping_dict=self.ready_interactive()

            print(display_opare)
            opera_choice = input('请选择您的操作: ')

            if opera_choice not in opera_mapping_dict.keys():
                print('请选择正确的操作序号')
                continue
            try:
                opera_func=getattr(self,opera_mapping_dict[opera_choice])
                result = opera_func()
                if  result:
                    atm()
            except KeyError as e:
                logger.warning('获取ATM类方法错误:%s'%(opera_choice))

    @check_login
    def ready_interactive(self):
        '''
        初始化settings注册过的交互列表
        :return:
         print_msg:返回交互列表(字符串)
         opera_mapping_dict:功能对应关系(字典)
        '''

        opera_mapping_dict = {}
        display_opare = ['----- %s Bank------'%(self.auth_data.get('real_name'))]
        for item_index, opera_tuple, in enumerate(OPERA_LIST, 1):
            opera,opera_mapping = opera_tuple
            opera_mapping_dict[str(item_index)] = opera_mapping
            display_opare.append(' %s   %s  ' % (item_index, opera))
        display_opare = '\n'.join(display_opare)
        return display_opare,opera_mapping_dict


atm=ATM()