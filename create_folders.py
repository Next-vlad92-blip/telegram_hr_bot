import os

# Корневая папка для документов
DOCS_DIR = "documents"

# Список категорий (транскрипция + комментарий для понимания)
categories = [
    "Sots_politika",   # социальная политика
    "Zarplata",        # зарплата
    "Zayavleniya"      # заявления
]

def create_folders():
    if not os.path.exists(DOCS_DIR):
        os.mkdir(DOCS_DIR)
        print(f"Создана папка: {DOCS_DIR}")

    for cat in categories:
        path = os.path.join(DOCS_DIR, cat)
        if not os.path.exists(path):
            os.mkdir(path)
            print(f"Создана папка: {path}")
        else:
            print(f"Папка уже существует: {path}")

if __name__ == "__main__":
    create_folders()
    print("Все папки созданы ✅")
