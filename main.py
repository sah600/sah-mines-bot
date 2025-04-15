import uvicorn
from fastapi import FastAPI
from bot import dp, bot

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=10000)
