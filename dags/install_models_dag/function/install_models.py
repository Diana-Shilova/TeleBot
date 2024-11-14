from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    pipeline
)
import whisper
import torch

device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")

models = [
    "Helsinki-NLP/opus-mt-ru-en",
    "Helsinki-NLP/opus-mt-en-ru",
    "Helsinki-NLP/opus-mt-mul-en",
    "j-hartmann/emotion-english-distilroberta-base",
    "openai/whisper-medium",
]

def download_model():
    try:
        for model in models:  # Скачивание всех моделей из списка
            if "opus-mt" in model:
                print(f"Загрузка модели перевода: {model}")
                AutoTokenizer.from_pretrained(model)
                AutoModelForSeq2SeqLM.from_pretrained(model)

            elif "emotion" in model:
                print(f"Загрузка модели классификации эмоций: {model}")
                pipeline("text-classification", model=model, device=0 if device == "cuda" else -1)

            elif "whisper" in model:
                print(f"Загрузка модели распознавания речи через whisper.load_model: {model}")
                whisper_model = whisper.load_model("medium", device=device)

        return "Все модели успешно установлены"

    except Exception as e:
        return f"Ошибка скачивания модели {model}: {e}"