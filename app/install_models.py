from transformers import (
    BlenderbotTokenizer,
    BlenderbotForConditionalGeneration,
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    GPT2LMHeadModel,
    GPT2Tokenizer,
    pipeline
)
import torch

device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")

# Список моделей для загрузки
models = [
    "Helsinki-NLP/opus-mt-ru-en",
    "Helsinki-NLP/opus-mt-en-ru",
    "Helsinki-NLP/opus-mt-mul-en",
    "facebook/blenderbot-400M-distill",
    "j-hartmann/emotion-english-distilroberta-base",
    "openai-community/gpt2",
    "openai/whisper-medium"
]


def download_model():
    try:
        for model in models:
            print(f"Загрузка модели: {model}")

            if "opus-mt" in model:
                tokenizer = AutoTokenizer.from_pretrained(model)
                model_obj = AutoModelForSeq2SeqLM.from_pretrained(model)

            elif "blenderbot" in model:
                tokenizer = BlenderbotTokenizer.from_pretrained(model)
                model_obj = BlenderbotForConditionalGeneration.from_pretrained(model)

            elif "gpt2" in model:
                tokenizer = GPT2Tokenizer.from_pretrained(model)
                model_obj = GPT2LMHeadModel.from_pretrained(model)

            elif "emotion" in model:
                pipeline("text-classification", model=model, device=0 if device == "cuda" else -1)

            elif "whisper" in model:
                pipeline("automatic-speech-recognition", model=model, device=0 if device == "cuda" else -1)

            print(f"Модель {model} успешно загружена и закэширована.")

    except Exception as e:
        print(f"Ошибка скачивания модели {model}: {e}")


download_model()
