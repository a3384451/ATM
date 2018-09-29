import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(BASE_DIR)

#log的目录路劲
LOGS_DIR='logs/atm_log/atm.txt'

#数据库配置
DATABASES={
    'db_tool':'file',
    'path':'%s/db'%(BASE_DIR),
    'name':'account_msg'
}

DB_PATH=os.path.join(BASE_DIR,DATABASES['path'],DATABASES['name'])

OPERA_LIST = [
    ('用户信息','account_info'),
    ('存款', 'deposit'),
    ('还款','repay'),
    ('取款', 'withdraw'),
    ('转账', 'transfer'),
    ('退出','logout'),
]