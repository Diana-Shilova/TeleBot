from gtts import gTTS
from pydub import AudioSegment
from langdetect import detect
import soundfile as sf
import torch
import librosa
import whisper
import os, re
import ollama
from transformers import pipeline
import warnings
warnings.filterwarnings('ignore')

output_dir = "all_info_for_drive"

os.makedirs(output_dir, exist_ok=True)

device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
device_id = 0 if device == "cuda" else -1

translator_en_to_ru = pipeline("translation_en_to_ru", model="Helsinki-NLP/opus-mt-en-ru", device=device)
translator_mul_to_en = pipeline("translation", model="Helsinki-NLP/opus-mt-mul-en", device=device)

# Отключаем параллелизм токенизаторов
os.environ["TOKENIZERS_PARALLELISM"] = "false"

ModelSTT = whisper.load_model("medium", device='cpu')


def text_to_voice(msg):
    language = detect(text=msg)

    if language == 'ru':
        model, example_text = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_tts',
            language=language,
            speaker='v3_1_ru'
        )

        sample_rate = 48000
        speaker = 'xenia'  # Голоса: 'aidar', 'baya', 'xenia', 'eugene'

        audio = model.apply_tts(text=msg, speaker=speaker, sample_rate=sample_rate)

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'TextToSpeech.wav')

        sf.write(output_path, audio, sample_rate)

    else:
        tts = gTTS(msg, lang=language, slow=False)
        tts.save(os.path.join(output_dir, 'TextToSpeech.wav'))


def ogg2wav(ofn):
    ogg_path = os.path.join(output_dir, ofn + ".ogg")
    wav_path = os.path.join(output_dir, ofn + ".wav")

    if not os.path.exists(ogg_path):
        raise FileNotFoundError(f"Файл не найден: {ogg_path}")

    segment = AudioSegment.from_file(ogg_path)
    segment.export(wav_path, format='wav')

    if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
        raise ValueError("Ошибка конвертации: пустой .wav файл")
    return wav_path


def speech_to_text(file_path, call_type):
    wav_file_path = ogg2wav(file_path)

    if not os.path.exists(wav_file_path):
        raise FileNotFoundError(f"Файл {wav_file_path} не найден после конвертации")

    try:
        result = ModelSTT.transcribe(wav_file_path)

        if not result.get("text"):
            raise ValueError("Не удалось распознать текст в аудиофайле")

        # Получение продолжительности аудио
        y, sr = librosa.load(wav_file_path, sr=None)
        duration = librosa.get_duration(y=y, sr=sr)

        # Разделение текста на предложения
        sentences = result["text"].split('. ')
        timings = []
        start_time = 0

        # Формирование таймингов
        for sentence in sentences:
            end_time = start_time + (len(sentence) / len(result["text"])) * duration
            timings.append((start_time, end_time, sentence))
            start_time = end_time

        # Проверка на пустой результат
        if not result["text"].strip():
            raise ValueError("Текст пустой после транскрипции")
        if call_type == 'audio_timer':
            output = []
            for start, end, sentence in timings:
                output.append(
                    f'{start // 3600:02}:{(start % 3600) // 60:02}:{start % 60:05.2f}ms - {end // 3600:02}:{(end % 3600) // 60:02}:{end % 60:05.2f}ms: {sentence.strip()}')
            return "\n".join(output)

        elif call_type == 'audio':
            return sentences

    except Exception as e:
        return f"Не удалось распознать текст в аудиофайле. Произошла ошибка {e}."


def question_answer(text):
    text_en = "Tell me more about this: " + translator_mul_to_en(text)[0]['translation_text']

    try:
        response = ollama.chat(
            model="llama3.2:3b",
            messages=[{'role': 'user', 'content': text_en}],
            options={'temperature': 1.5, 'top_p': 0.9, 'max_tokens': 1000}  # Увеличиваем max_tokens
        )

        ollama_response = response['message']['content']
        print("Ответ модели (англ.):\n", ollama_response)

        sentences = re.split(r'(?<=[.!?])\s+', ollama_response)
        translated_sentences = []

        for sentence in sentences:
            translation = translator_en_to_ru(sentence)[0]['translation_text']
            translated_sentences.append(translation)

        full_translation = ' '.join(translated_sentences)
        print("Перевод на русский:\n", full_translation)

        return full_translation

    except Exception as e:
        return str(e)


def translation_text(text, command):
    if command == 'mul-en':
        translated_text_en = translator_mul_to_en(text, max_length=100)[0]['translation_text']
        return translated_text_en

    elif command == 'mul-ru':
        translated_text_en = translator_mul_to_en(text, max_length=100)[0]['translation_text']
        translated_text_ru = translator_en_to_ru(translated_text_en, max_length=100)[0]['translation_text']
        return translated_text_ru


def emotion_analysis(text):
    text_en = translator_mul_to_en(text)[0]['translation_text']

    emotion_analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base", device=0)
    result = emotion_analyzer(text_en, top_k=1)
    label = result[0]['label']
    score = round(result[0]['score'] * 100, 2)

    emotion_ru = translator_en_to_ru(label)[0]['translation_text']
    emotion_ru_lower = emotion_ru.lower()
    return f'Проанализировав предоставленный мне текст, я могу с точностью {score}% ' \
           f'сказать, что в этом тексте чувствуется такая эмоция, как - {emotion_ru_lower}.'