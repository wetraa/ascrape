import asyncio


def run(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)
