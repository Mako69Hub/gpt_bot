import requests
from config import url_tts, url_stt, params_stt, headers
from creds import get_creds  # модуль для получения токенов

IAM_TOKEN, FOLDER_ID = get_creds()  # получаем iam_token и folder_id из файлов


def text_to_speech(text):
    data_tts = {'text': text,
                'lang': 'ru-RU',
                'folderId': FOLDER_ID}

    response = requests.post(url_tts, headers=headers, data=data_tts)

    if response.status_code == 200:
        return True, response.content
    else:
        return False, f'При запросе в SpeechKit произошла ошибка под номером {response.status_code}'


def speech_to_text(file):
    response = requests.post(
        f"{url_stt}?{params_stt}",
        headers=headers,
        data=file)

    decoder_data = response.json()

    if response.status_code != 200:
        return False, f'Error {response.status_code}'
    return True, decoder_data['result']
