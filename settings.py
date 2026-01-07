from dotenv import load_dotenv
import os

load_dotenv('../.env')  # загружает переменные из .env в os.environ

DEVELOPER = bool(int(os.getenv('DEVELOPER')))

if DEVELOPER is True:
    DB_HOST = 'localhost'
else:
    DB_HOST = ''

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PORT = os.getenv('DB_PORT')
DB_PASSWORD = os.getenv('DB_PASSWORD')

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_BOT_USERNAME = os.getenv('TG_BOT_USERNAME')

LLM_URL = os.getenv('LLM_URL')

TG_API_ID = int(os.getenv('TG_API_ID'))
TG_API_HASH = os.getenv('TG_API_HASH')
TG_PHONE = os.getenv('TG_PHONE')

#rabbit
RABBITMQ_HOST=os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT=int(os.getenv('RABBITMQ_PORT'))
RABBITMQ_USER=os.getenv('RABBITMQ_USER')
RABBITMQ_PASS=os.getenv('RABBITMQ_PASS')
COMPANION_MESSAGE_QUEUE_NAME=os.getenv('COMPANION_MESSAGE_QUEUE_NAME')
