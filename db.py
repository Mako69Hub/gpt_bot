import sqlite3
import logging
from config import LOGS, DB_FILE

logging.basicConfig(filename=LOGS, level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")


def create_db():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    message TEXT,
                    role TEXT,
                    total_gpt_tokens INTEGER,
                    tts_symbols INTEGER,
                    stt_blocks INTEGER)
                ''')

            logging.info("DATABASE: База данных создана")  # делаем запись в логах

    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return None


# добавляем новое сообщение в таблицу messages
def add_message(user_id, full_message):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            message, role, total_gpt_tokens, tts_symbols, stt_blocks = full_message

            cursor.execute('''
                    INSERT INTO messages (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks) 
                    VALUES (?, ?, ?, ?, ?, ?)''',
                           (user_id, message, role, total_gpt_tokens, tts_symbols, stt_blocks)
                           )
            conn.commit()

            logging.info(f"DATABASE: INSERT INTO messages "
                         f"VALUES ({user_id}, {message}, {role}, {total_gpt_tokens}, {tts_symbols}, {stt_blocks})")

    except Exception as e:
        logging.error(e)
        return None


# считаем количество уникальных пользователей помимо самого пользователя
def count_users(user_id):
    try:
        # подключаемся к базе данных
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''SELECT COUNT(DISTINCT user_id) FROM messages WHERE user_id <> ?''', (user_id,))
            count = cursor.fetchone()[0]
            return count
    except Exception as e:
        logging.error(e)
        return None


# получаем последние <n_last_messages> сообщения
def select_n_last_messages(user_id, n_last_messages=4):
    messages = []  # список с сообщениями
    total_spent_tokens = 0  # количество потраченных токенов за всё время общения
    try:
        # подключаемся к базе данных
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute('''
            SELECT message, role, total_gpt_tokens FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?''',
                           (user_id, n_last_messages))
            data = cursor.fetchall()

            if data and data[0]:
                # формируем список сообщений
                for message in reversed(data):
                    messages.append({'text': message[0], 'role': message[1]})
                    total_spent_tokens = max(total_spent_tokens, message[2])  # находим максимальное количество потраченных токенов

            return messages, total_spent_tokens
    except Exception as e:
        logging.error(e)
        return messages, total_spent_tokens


# подсчитываем количество потраченных пользователем ресурсов (<limit_type> - символы или аудиоблоки)
def count_all_limits(user_id, limit_type):
    try:
        # подключаемся к базе данных
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            cursor.execute(f'''SELECT SUM({limit_type}) FROM messages WHERE user_id=?''', (user_id,))
            data = cursor.fetchone()

            if data and data[0]:

                logging.info(f"DATABASE: У user_id={user_id} использовано {data[0]} {limit_type}")
                return data[0]
            else:
                return 0

    except Exception as e:
        logging.error(e)
        return 0






# def execute_query(sql_query, data=None, db_path=DB_NAME):
#     with sqlite3.connect(db_path) as connection:
#         cursor = connection.cursor()
#         if data:
#             cursor.execute(sql_query, data)
#         else:
#             cursor.execute(sql_query)
#         connection.commit()
#
#
# def execute_selection_query(sql_query, db_path=DB_NAME):
#     connection = sqlite3.connect(db_path)
#     cursor = connection.cursor()
#
#     cursor.execute(sql_query)
#     rows = cursor.fetchall()
#     connection.close()
#     return rows
#
# def create_table():
#     sql_query = ()
#
#
# def user_history():
#     return 0
#
# def
