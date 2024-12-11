from dotenv import load_dotenv
import os

dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)

# EXPORTS VARIABLES
FILE_LOCAL_SERVER_PATH = os.getenv('FILE_LOCAL_SERVER_PATH')
print(FILE_LOCAL_SERVER_PATH)
