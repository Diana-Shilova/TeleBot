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

models = [
    "Helsinki-NLP/opus-mt-ru-en",
    "Helsinki-NLP/opus-mt-en-ru",
    "Helsinki-NLP/opus-mt-mul-en",
    "facebook/blenderbot-400M-distill",
    "j-hartmann/emotion-english-distilroberta-base",
    "openai/whisper-medium",
]


def download_model():
    try:
        for model in models:  # Скачивание всех моделей из списка
            if "opus-mt" in model:
                AutoTokenizer.from_pretrained(model)
                AutoModelForSeq2SeqLM.from_pretrained(model)

            elif "blenderbot" in model:
                BlenderbotTokenizer.from_pretrained(model)
                BlenderbotForConditionalGeneration.from_pretrained(model)

            elif "gpt2" in model:
                GPT2Tokenizer.from_pretrained(model)
                GPT2LMHeadModel.from_pretrained(model)

            elif "emotion" in model:
                pipeline("text-classification", model=model, device=0 if device == "cuda" else -1)

            elif "whisper" in model:
                pipeline("automatic-speech-recognition", model=model, device=0 if device == "cuda" else -1)

        return f"Все модели успешно установлены"

    except Exception as e:
        return f"Ошибка скачивания модели {model}: {e}"

