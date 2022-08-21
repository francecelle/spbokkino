import asyncio
import datetime, time
#$Env:api_hash = '588ceb8cd037458fee82fd153e6ca444'
#$Env:api_id
#$Env:api_id = '1506646'
#$Env:id = '1076268780'
#$Env:token = '1375293377:AAGOirgwVaFWAnv7lpupLslKjehLK2psoZ4'

class Crons(object):
    async def new(self, n: int):
        setattr(self, str(n), True)
    async def close(self, n: int):
        setattr(self, str(n), False)
class Loop:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.callback = None
        self.crons = Crons()
    async def recall(self, t, n):
        if getattr(self.crons, n, None):
            await cb(n)
            self.loop.call_at(time.time() + t, self.recall, t, self.callback, n)
    async def start(self, n: int, t: int):
        await self.callback(n)
        await self.crons.new(n)
        self.loop.call_at(time.time() + t, self.recall, t, self.callback, n)
    async def stop(self, n: int):
        await self.crons.close(n)
    def spamming(self):
        print("cacata")
        def func(callback):
            self.callback = callback
        return func
