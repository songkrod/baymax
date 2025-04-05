import asyncio
from agent.core.agent import run

async def main():
    await run()

if __name__ == "__main__":
    asyncio.run(main())
