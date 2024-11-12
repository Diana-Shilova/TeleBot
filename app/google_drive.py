from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from googleapiclient.errors import HttpError
import json
import os
import time

gauth = GoogleAuth()
gauth.LoadCredentialsFile("/mycreds.txt")
drive = GoogleDrive(gauth)


def get_file_path_excluding_file(file_path):
    return os.path.dirname(file_path)


def get_file_type(filename):
    basename, extension = os.path.splitext(filename)
    return extension[1:]


def upload_new_file(full_path, user_id, function):
    folder_path = get_file_path_excluding_file(full_path)
    file_name = os.path.basename(full_path)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    new_file_name = f"{timestamp}_{file_name}"
    new_file_name_path = os.path.join(folder_path, new_file_name)
    os.rename(full_path, new_file_name_path)

    file_type = get_file_type(new_file_name)

    try:
        with open('google_folder_id.json', 'r', encoding='utf8') as json_file:
            info = json.load(json_file)
            user_folders = next(({
                'subfolder_TTS_id': user_info['subfolder_TTS_id'],
                'subfolder_STT_id': user_info['subfolder_STT_id'],
                'subfolder_question_id': user_info['subfolder_question_id'],
                'subfolder_translations_id': user_info['subfolder_translations_id'],
                'subfolder_emotions_in_text_id': user_info['subfolder_emotions_in_text_id']
            } for user_info in info['users'] if user_info['user_id'] == user_id), None)
            return 'User registrated'

            if user_folders is None:
                return 'User ID not found.'

        if function == 'text_to_speech':
            if file_type == 'txt':
                file_metadata = {'title': new_file_name, 'parents': [{'id': user_folders['subfolder_STT_id']}]}
                file = drive.CreateFile(file_metadata)
                file.SetContentString(open(new_file_name_path).read())
                file.Upload()

            elif file_type in ['mp3', 'wav']:
                file_metadata = {'title': new_file_name, 'parents': [{'id': user_folders['subfolder_STT_id']}]}
                file = drive.CreateFile(file_metadata)
                file.SetContentFile(new_file_name_path)
                file.Upload()

            return f'Файл {new_file_name} успешно загружен на сервер.'

        if function == 'questions':
            if file_type == 'txt':
                file_metadata = {'title': new_file_name, 'parents': [{'id': user_folders['subfolder_question_id']}]}
                file = drive.CreateFile(file_metadata)
                file.SetContentString(open(new_file_name_path).read())
                file.Upload()

        if function == 'emotions':
            if file_type == 'txt':
                file_metadata = {'title': new_file_name, 'parents': [{'id': user_folders['subfolder_emotions_in_text_id']}]}
                file = drive.CreateFile(file_metadata)
                file.SetContentString(open(new_file_name_path).read())
                file.Upload()

        if function == 'translate_text':
            if file_type == 'txt':
                file_metadata = {'title': new_file_name, 'parents': [{'id': user_folders['subfolder_translations_id']}]}
                file = drive.CreateFile(file_metadata)
                file.SetContentString(open(new_file_name_path).read())
                file.Upload()

        elif function == 'speech_to_text':
            if file_type == 'txt':
                file_metadata = {'title': new_file_name, 'parents': [{'id': user_folders['subfolder_TTS_id']}]}
                file = drive.CreateFile(file_metadata)
                file.SetContentString(open(new_file_name_path).read())
                file.Upload()

            elif file_type in ['mp3', 'wav']:
                file_metadata = {'title': new_file_name, 'parents': [{'id': user_folders['subfolder_TTS_id']}]}
                file = drive.CreateFile(file_metadata)
                file.SetContentFile(new_file_name_path)
                file.Upload()

            return 'Данный тип файла не поддерживается. Пожалуйста, загрузите файл формата TXT или WAV/MP3.'

    # Обработка ошибок HTTP-запроса (API)
    except HttpError as error:
        if error.resp.status == 403:
            return "Ошибка 403: Доступ запрещен. Проверьте права доступа и квоты."
        elif error.resp.status == 404:
            return "Ошибка 404: Папка или ресурс не найден. Проверьте 'parent_id'."
        else:
            return f"HTTP ошибка: {error.resp.status} - {error._get_reason()}"

    except Exception as e:
        return (f"Произошла ошибка при загрузке файла '{new_file_name}': {e}")


def create_folder_for_new_user(folder_name, user_id):
    try:
        with open('parent_google_folder_id_.json', 'r', encoding='utf8') as json_file:
            parent_folder = json.load(json_file)
            parent_folder_id = parent_folder['folder_id']

        with open('google_folder_id.json', 'r', encoding='utf8') as json_file:
            data = json.load(json_file)

        # Check if user_id already exists
        existing_user = next((user for user in data['users'] if user['user_id'] == user_id), None)
        if existing_user:
            return f'Пользователь {user_id} уже зарегистрирован'

        folder_metadata = {
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{'id': parent_folder_id}]
        }

        folder = drive.CreateFile(folder_metadata)
        folder.Upload()

        # Создаем подпапки для корневой папки нового пользователя
        subfolder_metadata1 = {'title': 'speech_to_text',
                               'mimeType': 'application/vnd.google-apps.folder',
                               'parents': [{'id': folder['id']}]}
        subfolder1 = drive.CreateFile(subfolder_metadata1)
        subfolder1.Upload()

        subfolder_metadata2 = {'title': 'text_to_speech',
                               'mimeType': 'application/vnd.google-apps.folder',
                               'parents': [{'id': folder['id']}]}
        subfolder2 = drive.CreateFile(subfolder_metadata2)
        subfolder2.Upload()

        subfolder_metadata3 = {'title': 'question_answer',
                               'mimeType': 'application/vnd.google-apps.folder',
                               'parents': [{'id': folder['id']}]}
        subfolder3 = drive.CreateFile(subfolder_metadata3)
        subfolder3.Upload()

        subfolder_metadata4 = {'title': 'translations_text',
                               'mimeType': 'application/vnd.google-apps.folder',
                               'parents': [{'id': folder['id']}]}
        subfolder4 = drive.CreateFile(subfolder_metadata4)
        subfolder4.Upload()

        subfolder_metadata5 = {'title': 'emotions_in_text',
                               'mimeType': 'application/vnd.google-apps.folder',
                               'parents': [{'id': folder['id']}]}
        subfolder5 = drive.CreateFile(subfolder_metadata5)
        subfolder5.Upload()

        # Создаем JSON файл, где будут данные по папкам для разных пользователей (ID)
        new_user = {
                'user_id': user_id,
                'folder_id': folder['id'],
                'subfolder_TTS_id': subfolder1['id'],
                'subfolder_STT_id': subfolder2['id'],
                'subfolder_question_id': subfolder3['id'],
                'subfolder_translations_id': subfolder4['id'],
                'subfolder_emotions_in_text_id': subfolder5['id'],
                }

        with open('google_folder_id.json', 'r', encoding='utf8') as json_file:
            data = json.load(json_file)

        data['users'].append(new_user)

        with open('google_folder_id.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

        return f'Файл {folder_name} успешно загружен на сервер.'

    except Exception as _ex:
        return f'Хьюстон, у нас проблемы! Ошибка {_ex} Проверь код!'

