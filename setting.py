import os
from dotenv import load_dotenv
load_dotenv()

ACCOUNT_DB_HOST = os.getenv('ACCOUNT_DB_HOST')
DATA_DB_HOST = os.getenv('DATA_DB_HOST')
ACCOUNT_AVAILABLE_INTERVAL_FROM_LAST_LOGIN = 24
IS_WINDOWS = True

