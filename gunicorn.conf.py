# gunicorn.conf.py
import os
from dotenv import load_dotenv

# Load environment variables from .env and .flaskenv files
for env_file in ('.env', '.flaskenv'):
    env = os.path.join(os.getcwd(), env_file)
    if os.path.exists(env):
        load_dotenv(env)
