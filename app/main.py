import logging
import telebot
import random
import signal
from telebot import types
from text_to_speech import text_to_voice, speech_to_text, question_answer, translation_text, emotion_analysis
from google_drive import upload_new_file, create_folder_for_new_user
import os

# Проверка и создание папки для сохранения файлов
folder_path = "/all_info_for_drive"
sticker_dir = "/sticker"

if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    logging.info('Создана новая папка')

random_sentences = [
    'О, я вижу ты уже направил мне информацию, уже занимаюсь ее обработкой 🌝',
    'А ты шустрый 🤔, уже пошел обрабатывать твой запрос.',
    'Вот это скорость, уже занимаюсь обработкой твоего запроса 🙃',
    'Принял, ушел за обработкой твоего запроса.',
    'Подкинул же ты мне работенку, ушел обрабатывать информацию.',
    'Я очень рад, что могу тебе помочь 🫡. Постараюсь побыстрее дать ответ.'
]

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# JustSpeech
TOKEN = '7318753618:AAFGEcDELj5DgHutedK7vKFX0xgRXXDvRUo'
bot = telebot.TeleBot(TOKEN)

# Создание кнопок
markup_func_ru = types.InlineKeyboardMarkup()
btn1_ru = types.InlineKeyboardButton('Расшифровка аудио 📝', callback_data='ru транскрипция')
btn2_ru = types.InlineKeyboardButton('Озвучка текста 🔉', callback_data='ru озвучка')
btn3_ru = types.InlineKeyboardButton('Хочу задать вопрос', callback_data='ru вопрос')
btn4_ru = types.InlineKeyboardButton('Перевод текста 💼', callback_data='ru перевод текста')
btn5_ru = types.InlineKeyboardButton('Определить эмоциональную часть текста', callback_data='ru эмоция в тексте')
markup_func_ru.add(btn1_ru)
markup_func_ru.add(btn2_ru)
markup_func_ru.add(btn3_ru)
markup_func_ru.add(btn4_ru)
markup_func_ru.add(btn5_ru)

markup_audio = types.InlineKeyboardMarkup()
audio_without_timer = types.InlineKeyboardButton("Расшифровка аудио с временным интервалом", callback_data='audio_timer')
audio_with_timer = types.InlineKeyboardButton('Обычная расшифровка аудио', callback_data='audio')
back = types.InlineKeyboardButton('Назад 🔙', callback_data='back')
markup_audio.add(audio_without_timer)
markup_audio.add(audio_with_timer)
markup_audio.add(back)

logging.info("Бот запущен и готов к работе.")
call_type = None  # Глобальная переменная для типа обработки


@bot.message_handler(commands=['start'])
def start(message):
    logging.info(f"Получена команда /start от пользователя {message.from_user.id}")

    folder_name = f'user_{message.from_user.id}'
    user_id = message.from_user.id
    create_folder_for_new_user(folder_name, user_id)
    logging.info(f"Проверка / регистрация пользователя {message.from_user.id}")

    bot.send_sticker(message.chat.id, open(os.path.join(sticker_dir, 'sticker_5.webp'), 'rb'))

    bot.send_message(
        message.chat.id,
        "Вот совершенно простой гайд для тебя, как можно пользоваться данным ботом 🗒."
        "\n\nУ нас есть несколько функций для тебя, которые могут тебе помочь в обычной жизни, при отсутствии возможности работы с текстом 🎯."
        "\n\nТы можешь выбрать озвучивание текста 🗣. Может быть полезно для тебя, если сам не хочешь заморачиваться и делать голосовые сообщения 👀."
        "\n\nУ тебя также есть возможность воспользоваться функцией для получения транскрипции аудио 📑, которая может быть полезна в момент отсутствия возможности прослушать чье-то сообщение."
        "\nПри этом у тебя есть возможность получить транскрипцию в обычном виде или с разбиением на временные интервалы разговорной речи 😳."
        "\n\nПеревод текста 👥, мы можем делать перевод с таких языков как: английский, китайский, испанский, португальский, норвежский, французский и это не все перечисленные языки - их более 30 насчитывается на русский, а также перевод с русского на английский."
        "\nЭто могло бы тебе помочь во время общения с иностранцами, если ты плохо знаешь иностранный язык."
        "\n\nАнализ тональности текста 💁 - помогает изучить массив текста и определить, как он эмоционально окрашен."
        "\n\nПочему бы не задать вопрос, если очень хочется❓Здесь ты также можешь задать любой вопрос, какой хотел бы.",
        reply_markup=markup_func_ru,
        parse_mode='HTML'
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    logging.info(f"Нажата кнопка {call.data} пользователем {call.from_user.id}")
    try:
        if call.data == 'ru транскрипция':
            bot.send_message(call.message.chat.id, 'Выберите тип расшифровки:', reply_markup=markup_audio)
        elif call.data == 'ru озвучка':
            bot.send_message(call.message.chat.id, "Введите текст ниже, начиная с команды /speech, только будь внимателен. Для корректной работы данной функции длинна текста должна быть не меньше 8 знаков.")
        elif call.data == 'ru эмоция в тексте':
            bot.send_message(call.message.chat.id, "Если ты хочешь понять, что за эмоция в тексте то перед началом написания текста используй команду /emotion.")
        elif call.data == 'ru перевод текста':
            bot.send_message(call.message.chat.id, "Если ты хочешь получить перевод с любого языка на английкий то перед началом написания текста используй команду /mul-en."
                                                   "\n\n"
                                                   "Если тебе интересен перевод с любого языка на русский то используй перед началом написания текста команду /mul-ru.")
        elif call.data == 'audio_timer' or call.data == 'audio':
            bot.send_message(call.message.chat.id, "Отправьте голосовое сообщение или аудиофайл.")
            # Сохраняем call_type в глобальную переменную
            global call_type
            call_type = call.data
        elif call.data == 'ru вопрос':
            bot.send_message(call.message.chat.id, "Если хочешь задать вопрос, начни его с команды /question."),
        elif call.data == 'back':
            bot.send_message(call.message.chat.id, "Выберите, что вас интересует:", reply_markup=markup_func_ru)

    except Exception as e:
        logging.info(f"Возникла ошибка {e} при работе с запросом {call.message.message_id}")
        bot.send_message(call.message.chat.id,
                         f"Произошла ошибка ⚠️: {e}.\n\n"
                         f"Если ты видишь эту ошибку, то сообщи об этом администратору @vaalberit")


@bot.message_handler(content_types=['voice', 'audio'])
def get_speech_to_text_message(message):
    global call_type
    os.makedirs(folder_path, exist_ok=True)  # Создаем директорию, если она не существует
    msg_id = message.message_id

    call_type_text = call_type
    logging.info(f"Проверяем тип call_type_text: {call_type}")

    if call_type is None:
        logging.error(f"Пользователь не выбрал функционал для дальнейшей обработки данных.")
        bot.send_message(message.chat.id,
                         f"Кажется ты забыл сделать выбор для дальнейшей обработки твоего запроса",
                         reply_markup=markup_func_ru)

    elif message.content_type in ['voice', 'audio']:
        logging.info(f"Получен аудиофайл от пользователя {message.from_user.id}, id_{message.message_id}")

        try:
            file = bot.get_file(
                message.voice.file_id if message.content_type == 'voice' else message.audio.file_id
            )
            bot.send_message(message.from_user.id, random.choice(random_sentences))

            # Загрузка и сохранение аудиофайла
            bytes = bot.download_file(file.file_path)
            ogg_file_path = os.path.join(folder_path, 'SpeechToText.ogg')
            with open(ogg_file_path, 'wb') as new_file:
                new_file.write(bytes)

            logging.info(f"Идет обработка сообщения id_{message.message_id} по модели speech_to_text")

            text = speech_to_text('SpeechToText', call_type=call_type_text)

            logging.info(f"Идет обработка аудиофайла от пользователя {message.from_user.id}")
            upload_new_file(ogg_file_path, message.from_user.id, function='speech_to_text')
            logging.info(f"Отправлен файл с текстом пользователю {message.from_user.id} в ответ на сообщение {msg_id}")

            with open(os.path.join(folder_path, "TranscriptMessage.txt"), "w") as file:
                file.write(str(text))

            upload_new_file(os.path.join(folder_path, "TranscriptMessage.txt"), message.from_user.id, function='speech_to_text')
            logging.info(f"Отправлен файл с текстом от пользователя {message.from_user.id} на сервер")

            # Проверка на пустой результат
            if not text or (isinstance(text, list) and len(text) == 0):
                logging.warning(f"Пустой результат транскрипции для сообщения id_{message.message_id}")
                bot.reply_to(message, "Не удалось распознать текст в аудиофайле. Попробуйте снова.")
            else:
                if isinstance(text, list):
                    text = ' '.join(text)
                bot.reply_to(message, text)

            bot.send_message(message.chat.id, "Чем еще могу помочь?", reply_markup=markup_func_ru)

        except Exception as e:
            logging.error(f"Ошибка при обработке запроса: {e}")
            bot.send_message(message.chat.id,
                             f"Произошла ошибка ⚠️: {e}.\n\n"
                             f"Если ты видишь эту ошибку, сообщи об этом администратору @vaalberit")


@bot.message_handler(
    func=lambda message: message.text.startswith('/') and message.text.split()[0] not in ['/start'])
def handle_all_commands(message):
    command, *args = message.text.split(maxsplit=1)
    text = args[0] if args else ""  # Извлекаем текст после команды

    # Проверка наличия текста после команды
    if not text:
        bot.reply_to(message, f"Пожалуйста, укажите текст после команды {command}.")
        return

    try:
        # Обработка команды /speech
        if command == '/speech':
            file_path = os.path.join(folder_path, "SpeechToText.txt")
            logging.info(f"Получен текст для озвучивания от пользователя ID_{message.from_user.id}, ID_message_{message.message_id}: {text}")

            # Сохранение текста и загрузка файла
            with open(file_path, "w") as file:
                file.write(text)
            upload_new_file(file_path, message.from_user.id, function='text_to_speech')
            logging.info(f"Отправлен файл с текстом от пользователя ID_{message.from_user.id} на сервер")

            # Озвучивание текста
            text_to_voice(text)
            with open(os.path.join(folder_path, 'TextToSpeech.wav'), 'rb') as f:
                bot.send_audio(chat_id=message.chat.id, reply_to_message_id=message.message_id, audio=f)
            logging.info(f"Отправлен озвученный текст пользователю ID_{message.from_user.id}")

            # Загрузка аудио на сервер
            audio_file_path = os.path.join(folder_path, 'TextToSpeech.wav')
            upload_new_file(audio_file_path, message.from_user.id, function='text_to_speech')
            logging.info(f"Отправлен файл с аудио от пользователя ID_{message.from_user.id} на сервер")

        # Обработка команды /question
        elif command == '/question':
            file_path = os.path.join(folder_path, "Question.txt")
            logging.info(f"Получен вопрос от пользователя ID_{message.from_user.id}, ID_message_{message.message_id}: {text}")

            # Сохранение текста и загрузка файла
            with open(file_path, "w") as file:
                file.write(text)
            upload_new_file(file_path, message.from_user.id, function='questions')
            logging.info(f"Отправлен файл с текстом от пользователя {message.from_user.id} на сервер")

            # Ответ на вопрос
            answer = question_answer(text)
            bot.reply_to(message, answer)
            logging.info(f"Отправлен ответ на вопрос пользователю {message.from_user.id} в ответ на сообщение {message.message_id}")

            # Сохранение ответа
            answer_file_path = os.path.join(folder_path, "Answer.txt")
            with open(answer_file_path, "w") as file:
                file.write(str(answer))
            upload_new_file(answer_file_path, message.from_user.id, function='questions')
            logging.info(f"Отправлен файл с ответом на вопрос от пользователя {message.from_user.id} на сервер")

        # Обработка команды /mul-en
        elif command == '/mul-en':
            file_path = os.path.join(folder_path, "TextMulEn.txt")
            logging.info(f"Получен текст для перевода на ENG от пользователя {message.from_user.id}, id_{message.message_id}: {text}")

            # Сохранение текста и перевод
            with open(file_path, "w") as file:
                file.write(text)
            upload_new_file(file_path, message.from_user.id, function='translate_text')
            logging.info(f"Отправлен файл c текстом от пользователя {message.from_user.id} на сервер")

            answer = translation_text(text, 'mul-en')
            bot.reply_to(message, answer)

            # Сохранение перевода
            answer_file_path = os.path.join(folder_path, "TranslateMulEn.txt")
            with open(answer_file_path, "w") as file:
                file.write(str(answer))
            upload_new_file(answer_file_path, message.from_user.id, function='translate_text')
            logging.info(f"Отправлен файл с переводом ENG от пользователя {message.from_user.id} на сервер")

        # Обработка команды /mul-ru
        elif command == '/mul-ru':
            file_path = os.path.join(folder_path, "TextMulRu.txt")
            logging.info(f"Получен текст для перевода на RU от пользователя {message.from_user.id}, id_{message.message_id}: {text}")

            # Сохранение текста и перевод
            with open(file_path, "w") as file:
                file.write(text)
            upload_new_file(file_path, message.from_user.id, function='translate_text')
            logging.info(f"Отправлен файл c текстом от пользователя {message.from_user.id} на сервер")

            answer = translation_text(text, 'mul-ru')
            bot.reply_to(message, answer)

            # Сохранение перевода
            answer_file_path = os.path.join(folder_path, "TranslateMulRu.txt")
            with open(answer_file_path, "w") as file:
                file.write(str(answer))
            upload_new_file(answer_file_path, message.from_user.id, function='translate_text')
            logging.info(f"Отправлен файл с переводом RU пользователя {message.from_user.id} на сервер")

        # Обработка команды /emotion
        elif command == '/emotion':
            file_path = os.path.join(folder_path, "Text.txt")
            logging.info(f"Получен текст для распознавания эмоции от пользователя {message.from_user.id}, id_{message.message_id}: {text}")

            # Сохранение текста и анализ эмоций
            with open(file_path, "w") as file:
                file.write(text)
            upload_new_file(file_path, message.from_user.id, function='emotions')
            logging.info(f"Направлен текст от пользователя {message.from_user.id}, id_{message.message_id}: {text}")

            answer = emotion_analysis(text)
            bot.reply_to(message, answer)

            # Сохранение результата анализа
            answer_file_path = os.path.join(folder_path, "EmotionInText.txt")
            with open(answer_file_path, "w") as file:
                file.write(str(answer))
            upload_new_file(answer_file_path, message.from_user.id, function='emotions')
            logging.info(f"Отправлен результат анализа текста пользователя {message.from_user.id}, id_{message.message_id}: {text}")

        # Обработка команды /restart
        elif command == '/restart':
            bot.send_sticker(message.chat.id, open(os.path.join(sticker_dir,'sticker_4.webp'), 'rb'))
            bot.send_message(message.chat.id, "Перезапуск бота...")
            os.kill(os.getpid(), signal.SIGINT)
            bot.send_message(message.chat.id,
                             "Кажется ты кое-что забыл. Сделай, пожалуйста, выбор 👇", reply_markup=markup_func_ru)

        # Сообщение о завершении
        bot.send_message(message.chat.id, "Чем еще могу помочь?", reply_markup=markup_func_ru)

    except Exception as e:
        logging.error(f"Ошибка при обработке команды {command}: {e}")
        bot.send_message(message.chat.id,
                         f"Хьюстон, у нас ошибка ⚠️: {e}.\n\n"
                         f"Если ты видишь эту ошибку, то знай что администратор @vaalberit уже ее решает.")
        bot.send_message(message.chat.id, "Из-за появившейся ошибки я сделаю перезапуск бота для дальнейшей корректной работы, пока ошибку устраняет администратор...")
        os.kill(os.getpid(), signal.SIGINT)


@bot.message_handler(content_types=['text'])
def give_a_choise(message):
    bot.send_message(message.chat.id, "Я не могу обработать данный текст, так как не понимаю что с ним делать дальше. Сначала выбери, что ты хочешь 👇", reply_markup=markup_func_ru)


if __name__ == '__main__':
    try:
        logging.info("Запуск bot.polling()")
        bot.polling(non_stop=True)
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}")
