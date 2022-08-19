import asyncio

class Loop:
    def __init__(self):
        self.spam = False
    async def start():
        self.spam = True
    async def stop():
        self.spam = False
    async def _range(self):
        yield 1
        yield 2
        yield 3
    async def loop(self, cb):
        if self.spam:
            async for n in self._range():
                t = await cb(n)
                await asyncio.sleep(t)
        await self.loop(cb)
    async def spamming(self):
        async def func(callback):
            await self.loop(callback)
        return func