import io
import hashlib
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload
import app.keyboards as kb
from dotenv import load_dotenv
import os

# === Инициализация роутера ===
load_dotenv()
material = Router()

# === Настройки Google Drive ===
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
ROOT_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')

# === Авторизация ===
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build('drive', 'v3', credentials=creds)

# Кэш: короткий ключ -> данные папки
folder_cache = {}

def make_short_key(folder_id: str) -> str:
    """Создает короткий уникальный ключ длиной <= 16 символов."""
    return hashlib.md5(folder_id.encode()).hexdigest()[:12]


async def send_folder_contents(callback: CallbackQuery, folder_id: str, parent_id: str | None = None, path: str = "Главная"):
    try:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="files(id, name, mimeType)",
            orderBy="name"
        ).execute()
        files = results.get("files", [])

        keyboard = []

        # Кнопки для файлов и папок
        for file in files:
            short_key = make_short_key(file["id"])
            folder_cache[short_key] = {
                "id": file["id"],
                "parent": folder_id,
                "path": f"{path} / {file['name']}",
                "parent_path": path
            }

            if file["mimeType"] == "application/vnd.google-apps.folder":
                keyboard.append([InlineKeyboardButton(
                    text=f"📂 {file['name']}",
                    callback_data=f"open_{short_key}"
                )])
            else:
                keyboard.append([InlineKeyboardButton(
                    text=f"📄 {file['name']}",
                    callback_data=f"getfile_{file['id']}"
                )])

        # Кнопки навигации
        nav_buttons = []
        if parent_id:
            short_parent = make_short_key(parent_id)
            folder_cache[short_parent] = {
                "id": parent_id,
                "path": path.rsplit(" / ", 1)[0] if " / " in path else "Главная",
                "parent_path": path.rsplit(" / ", 1)[0] if " / " in path else "Главная"
            }
            nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_{short_parent}"))
        nav_buttons.append(InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu"))
        keyboard.append(nav_buttons)

        await callback.message.edit_text(
            f"📁 Путь: {path}\n\nВыберите файл или папку:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )

    except Exception as e:
        await callback.message.answer(f"⚠️ Ошибка при загрузке содержимого папки: {e}")


# === Открытие папки ===
@material.callback_query(F.data.startswith("open_"))
async def open_folder(callback: CallbackQuery):
    short_key = callback.data.replace("open_", "")
    folder_info = folder_cache.get(short_key)
    if not folder_info:
        await callback.message.answer("⚠️ Не удалось открыть папку — данные не найдены.")
        return

    await send_folder_contents(
        callback,
        folder_info["id"],
        folder_info.get("parent"),
        folder_info.get("path", "Главная")
    )


# === Переход назад ===
@material.callback_query(F.data.startswith("back_"))
async def go_back(callback: CallbackQuery):
    short_key = callback.data.replace("back_", "")
    folder_info = folder_cache.get(short_key)
    if not folder_info:
        await callback.message.answer("⚠️ Не удалось вернуться — данные не найдены.")
        return

    folder_id = folder_info["id"]
    path = folder_info.get("parent_path", "Главная")

    # Узнаем родителя текущей папки
    file_info = service.files().get(fileId=folder_id, fields="parents").execute()
    parents = file_info.get("parents", [])
    parent_id = parents[0] if parents else None

    await send_folder_contents(callback, folder_id, parent_id, path)


# === Возврат в меню ===
@material.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await send_folder_contents(callback, ROOT_FOLDER_ID, None, "Главная")


# === Скачивание файлов ===
@material.callback_query(F.data.startswith("getfile_"))
async def download_file(callback: CallbackQuery):
    file_id = callback.data.replace("getfile_", "")
    try:
        file_info = service.files().get(fileId=file_id, fields="name, mimeType").execute()
        file_name = file_info["name"]

        request = service.files().get_media(fileId=file_id)
        file_data = io.BytesIO()
        downloader = MediaIoBaseDownload(file_data, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()

        file_data.seek(0)

        await callback.message.answer_document(
            BufferedInputFile(file_data.read(), filename=file_name),
            caption=f"📄 {file_name}"
        )

    except Exception as e:
        await callback.message.answer(f"⚠️ Ошибка при скачивании файла: {e}")

    await callback.message.answer('Для возврата нажмите "Назад в меню"', reply_markup=kb.back_stud_menu)


# === Открытие корневой папки ===
@material.callback_query(F.data == "materials")
async def list_root(callback: CallbackQuery):
    """Открывает корневую папку с материалами."""
    folder_cache.clear()  # очищаем кэш, чтобы не было конфликтов
    await send_folder_contents(callback, ROOT_FOLDER_ID, None, "Главная")

