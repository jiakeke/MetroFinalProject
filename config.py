########## Site Settings #####################################
import os

db_name = 'pilotv2'
db_user = ''
db_pass = ''
db_host = 'localhost'
db_port = 3306

reloader_mode = False
debug = False
site_host = 'localhost'
site_port = 8888

jwt_secret_key = 'Please Modify the Secret Key in local_config.py'

# Load the local variables from config.py
if os.path.exists('local_config.py'):
    from local_config import *

