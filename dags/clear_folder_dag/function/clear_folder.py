import os
import time
import shutil


def clear_folder(folder_path):
    while True:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        time.sleep(7200)  # Чистка каждые 2 часа
