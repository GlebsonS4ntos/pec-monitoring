import asyncio
from main import loop_monitoramento
from send import run_bot
from dotenv import load_dotenv

load_dotenv()

async def run():
    monitoramento_task = asyncio.create_task(loop_monitoramento())
    bot_task = asyncio.create_task(run_bot())

    await asyncio.gather(monitoramento_task, bot_task)

if __name__ == "__main__":
    asyncio.run(run())
