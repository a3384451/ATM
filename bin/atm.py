import os,sys
from core import main
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(BASE_DIR)

if __name__ == '__main__':
    main.atm()


