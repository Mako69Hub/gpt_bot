import telebot
import logging
from config import LOGS, COUNT_LAST_MSG
from telebot.types import Message
from database import create_database, add_message, select_n_last_messages
from yandex_gpt import ask_gpt
from validators import *
from speeckit import speech_to_text, text_to_speech
from creds import get_bot_token

logging.basicConfig(filename=LOGS, level=logging.ERROR,
                    format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

bot = telebot.TeleBot(get_bot_token())


@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.send_message(message.chat.id, 'Ты приходишь ко мне и говоришь: “Бот Мэри, я хочу ответы”. '
                                      'Но ты просишь без уважения, не предлагаешь дружбы. Тебе и в голову не пришло '
                                      'назвать меня крестной матерью. Нет, ты приходишь в мой дом в день свадьбы моей '
                                      'дочери и просишь меня о токенах за деньги».')


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, "Чтобы приступить к общению, отправь мне голосовое сообщение или текст")


# обрабатываем команду /debug - отправляем файл с логами
@bot.message_handler(commands=['debug'])
def debug(message):
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)


@bot.message_handler(content_types=['voice'])
def handle_voice(message: Message):
    try:
        user_id = message.from_user.id

        # Проверка на максимальное количество пользователей
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        # Проверка на доступность аудиоблоков
        stt_blocks, error_message = is_stt_block_limit(user_id, message.voice.duration)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        file_id = message.voice.file_id
        file_info = bot.get_file(file_id)
        file = bot.download_file(file_info.file_path)

        status_stt, stt_text = speech_to_text(file)  # Обращение к функции speech_to_text для получения текста
        if not status_stt:
            bot.send_message(user_id, stt_text)
            return

        # Запись в БД
        add_message(user_id=user_id, full_message=[stt_text, 'user', 0, 0, stt_blocks])

        # Проверка на доступность GPT-токенов
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)

        if error_message:
            bot.send_message(user_id, error_message)
            return

        # Отправка нескольких последних сообщений от пользователя в GPT для генерации ответа
        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)
        # Запрос к GPT и обработка ответа
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer

        # Проверка на лимит символов для SpeechKit
        tts_symbols, error_message = is_tts_symbol_limit(user_id, answer_gpt)

        # Запись ответа GPT в БД
        add_message(user_id=user_id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])

        if error_message:
            bot.send_message(user_id, error_message)
            return

        # Преобразование ответа в аудио и отправка
        status_tts, voice_response = text_to_speech(answer_gpt)
        if status_tts:
            # Отправка голосового сообщения, если преобразование в аудио прошло успешно
            bot.send_voice(user_id, voice_response, reply_to_message_id=message.id)
        else:
            # Отправка текстового ответа GPT, если преобразование в аудио не удалось
            bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        user_id = message.from_user.id

        # ВАЛИДАЦИЯ: проверяем, есть ли место для ещё одного пользователя
        status_check_users, error_message = check_number_of_users(user_id)
        if not status_check_users:
            bot.send_message(user_id, error_message)
            return

        # БД: добавляем сообщение пользователя и его роль в базу данных
        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=user_id, full_message=full_user_message)

        # ВАЛИДАЦИЯ: считаем количество доступных пользователю GPT-токенов
        # получаем последние 4 (COUNT_LAST_MSG) сообщения и количество уже потраченных токенов

        last_messages, total_spent_tokens = select_n_last_messages(user_id, COUNT_LAST_MSG)

        # получаем сумму уже потраченных токенов + токенов в новом сообщении и оставшиеся лимиты пользователя
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(user_id, error_message)
            return

        # GPT: отправляем запрос к GPT
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)

        if not status_gpt:
            bot.send_message(user_id, answer_gpt)
            return

        total_gpt_tokens += tokens_in_answer

        # БД: добавляем ответ GPT и потраченные токены в базу данных
        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=user_id, full_message=full_gpt_message)

        bot.send_message(user_id, answer_gpt, reply_to_message_id=message.id)  # отвечаем пользователю текстом
    except Exception as e:
        logging.error(e)
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй написать другое сообщение")


@bot.message_handler(commands=['tts'])
def tts_handler(message: Message):
    bot.send_message(message.chat.id, 'What does the robot say?')
    status, message_kit = text_to_speech('Ты **устал**, но не сдаёшься, я **так** тобой горжусь')

    bot.send_voice(message.chat.id, message_kit)


@bot.message_handler(commands=['stt'])
def stt_handler(message: Message):
    bot.send_message(message.chat.id, 'Распознание речи')

    file_id = message.voice.file_id  # id ГС
    file_info = bot.get_file(file_id)  # инфо ГС
    file = bot.download_file(file_info.file_path)  # скачать ГС

    status, message_kit = speech_to_text(file)
    bot.send_voice(message.chat.id, message_kit)


create_database()
bot.polling()
