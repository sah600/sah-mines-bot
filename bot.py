import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Router
from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
import shutil

# ENV dəyişənlərini render panelindən əlavə edəcəksən
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")
REGISTER_LINK = os.environ.get("REGISTER_LINK")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

users = set()  # qeydiyyatdan keçən istifadəçilər
signals_folder = "signals"
os.makedirs(signals_folder, exist_ok=True)

@router.message(F.text == "/start")
async def start_handler(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Qeydiyyatdan keç", url=REGISTER_LINK)],
        [InlineKeyboardButton(text="Siqnal al", callback_data="get_signal")]
    ])
    await message.answer("Qeydiyyatdan keçmək üçün aşağıdakı düyməyə klik et:", reply_markup=kb)

@router.callback_query(F.data == "get_signal")
async def get_signal(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in users:
        users.add(user_id)
    signals = os.listdir(signals_folder)
    if signals:
        for s in signals:
            path = os.path.join(signals_folder, s)
            photo = FSInputFile(path)
            await bot.send_photo(user_id, photo)
    else:
        await callback.message.answer("Hazırda siqnal yoxdur.")
    await callback.answer()

@router.message(F.text == "/panel")
async def admin_panel(message: Message):
    if str(message.from_user.id) == ADMIN_ID:
        await message.answer("Siqnal yükləmək üçün şəkil göndərin.\nSilmək üçün /sil [ad] yazın.")
    else:
        await message.answer("Bu əmr yalnız admin üçündür.")

@router.message(F.photo)
async def upload_signal(message: Message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    file_path = file.file_path.split("/")[-1]
    dest = os.path.join(signals_folder, file_path)
    await photo.download(destination_file=dest)
    await message.answer("Siqnal yükləndi.")

@router.message(F.text.startswith("/sil"))
async def delete_signal(message: Message):
    if str(message.from_user.id) != ADMIN_ID:
        return
    try:
        name = message.text.split(" ")[1]
        path = os.path.join(signals_folder, name)
        if os.path.exists(path):
            os.remove(path)
            await message.answer("Siqnal silindi.")
        else:
            await message.answer("Bu adla siqnal tapılmadı.")
    except:
        await message.answer("İstifadə: /sil [ad]")
