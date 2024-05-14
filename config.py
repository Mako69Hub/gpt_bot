HOME_DIR = '/home/student/the_end'

IAM_TOKEN_PATH = f'{HOME_DIR}/creds/iam_token.txt'  # файл для хранения iam_token
FOLDER_ID_PATH = f'{HOME_DIR}/creds/folder_id.txt'  # файл для хранения folder_id
BOT_TOKEN_PATH = f'{HOME_DIR}/creds/bot_token.txt'  # файл для хранения bot_token


IAM_TOKEN = "t1.9euelZrOx4uSlc6ViZaWkJubkpTNze3rnpWal4vNlMiLis_MncrNjJmMyMnl8_dnPHJN-e8lf3Jo_N3z9ydrb0357yV_cmj8zef1656Vmpaamp7Oy4mUi56JlIqWkJ7I7_zF656Vmpaamp7Oy4mUi56JlIqWkJ7IveuelZqRls-Kjo-ajY6dlI6VzpvPz7XehpzRnJCSj4qLmtGLmdKckJKPioua0pKai56bnoue0oye.n3oPozjYBNQHq2w7aBcNTQELzUgPFj4metH1c1Ai6QFpgpPsCJXkdjTDaVkN4ShpygpmWqZE6XJWeAij0OOgCA"
FOLDER_ID = os.getenv('FOLDER_ID')
TOKEN = os.getenv('TG_TOKEN')

MAX_USERS = 3
MAX_GPT_TOKENS = 120
COUNT_LAST_MSG = 4 #кол-во последних сообщений из диалога

MAX_USERS_STT_BLOCKS = 10
MAX_USER_TTS_SYMBOLS = 5000
MAX_USER_GPT_TOKENS = 2000

LOGS = f'{HOME_DIR}/logs.txt'
DB_FILE = f'{HOME_DIR}/messages.db'

SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты помощник. Общайся с пользователем на "ты". '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]

# text to voice
url_tts = 'https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize'

# voice to text
url_stt = 'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize'

headers = {'Authorization': f'Bearer {IAM_TOKEN}', }

params_stt = "&".join([
    "topic=general",
    f"folderId={FOLDER_ID}",
    "lang=ru-RU"
])
