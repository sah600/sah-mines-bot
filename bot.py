import os
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage

BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = os.environ.get("ADMIN_ID")
REGISTER_LINK = os.environ.get("REGISTER_LINK")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

signals_dir = "signals"
os.makedirs(signals_dir, exist_ok=True)

@router.message(F.text == "/start")
async def start_cmd(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Qeydiyyatdan keç", url=REGISTER_LINK)],
        [InlineKeyboardButton(text="Siqnal al", callback_data="get_signal")]
    ])
    await message.answer("Zəhmət olmasa qeydiyyatdan keçin:", reply_markup=kb)

@router.callback_query(F.data == "get_signal")
async def send_signal(callback: types.CallbackQuery):
    files = os.listdir(signals_dir)
    if not files:
        await callback.message.answer("Hazırda siqnal yoxdur.")
        await callback.answer("Siqnallar göndərildi.")
        return

    for fname in files:
        path = os.path.join(signals_dir, fname)
        try:
            await bot.send_photo(chat_id=callback.from_user.id, photo=FSInputFile(path))
        except Exception as e:
            await callback.message.answer(f"Xəta baş verdi: {e}")

    await callback.answer()

@router.message(F.text == "/panel")
async def admin_panel(message: types.Message):
    if str(message.from_user.id) == ADMIN_ID:
        await message.answer("Şəkil siqnalı göndərin və ya silmək üçün: /sil [ad]")
    else:
        await message.answer("Sizə icazə yoxdur.")

@router.message(F.photo)
async def upload_photo(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID:
        return

    photo = message.photo[-1]
    file_name = f"{photo.file_unique_id}.jpg"
    path = os.path.join(signals_dir, file_name)

    file = await bot.download(photo.file_id)
    with open(path, "wb") as f:
        f.write(file.read())

    await message.answer("Siqnal yükləndi.")

@router.message(F.text.startswith("/sil"))
async def delete_photo(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID:
        return

    try:
        name = message.text.split(" ", 1)[1]
        path = os.path.join(signals_dir, name)
        if os.path.exists(path):
            os.remove(path)
            await message.answer("Siqnal silindi.")
        else:
            await message.answer("Fayl tapılmadı.")
    except:
        await message.answer("İstifadə: /sil [ad]")
