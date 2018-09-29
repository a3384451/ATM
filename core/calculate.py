from logs.log import logger

class AtmCalculate(object):
    '''
    用于计算存取钱的
    '''
    def save(self,balace,calcu_number):
        '''存钱'''
        return round(balace+calcu_number,2)

    def drop(self,balance,calcu_number):
        '''取钱'''
        return round(balance-calcu_number,2)

    def dispatch(self,calcu_method,balance,calcu_number):
        '''分发存取款'''
        func = getattr(self,calcu_method)
        if callable(func):
            result = func(balance,calcu_number)
            return result

        else:
            logger.warning('分发计算方式失败')


