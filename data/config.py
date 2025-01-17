from environs import Env


env = Env()
env.read_env()


BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = [1849953640, 1796966691]
IP = env.str("ip")

DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST")

MESSAGE_SENDER_COMMAND = 'MultilevelBotMailing'

DATABASE_INFO = {
    'user': DB_USER,
    'password': DB_PASS,
    'database': DB_NAME,
    'host': DB_HOST
}
