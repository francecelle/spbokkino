import asyncio
from json import dumps
#$Env:api_hash = '588ceb8cd037458fee82fd153e6ca444'
#$Env:api_id = '1506646'
#$Env:id = '1076268780'
#$Env:token = '1375293377:AAGOirgwVaFWAnv7lpupLslKjehLK2psoZ4'
#$Env:session_string = 'BAAW_VYAxjL5R6SQfX9xCDqcYaLxaWchJCIClrrIG9-9mVKgEfnP-RL6jXLrTljx59TnLmtZn12mtR-onXmuWg-apClCtseCrLcamcDkclJbTyDFsevM2Ast3N02p6a3pdlKeTITmmNfwNOzD6OSE7mrRHJMB_t_jNOKdNJqbNiMGaHarqiklv2b06OoOpEKKb8CnKqhfNlSRCA4Us-JHM39oaQ-wHGDRJv0WecDy8K7sg0qlVe5ByIW6ml4U7oMi5ADzThbq7UpM5EFo3Fv--Lmpc67yCl4IvUvOTJNiLX1Xh_Pf1gsmoPCyDrBd2SwLqkOiLz0T6BsJesxV3bm0aBX7aXYQwAAAAFP4q7yAA'

class Crons(object):
    async def new(self, n: int):
        setattr(self, str(n), True)
    async def close(self, n: int):
        setattr(self, str(n), False)
    def __str__(self) -> str:
        return dumps(self.__dict__, indent=4)


class Loop:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.callback = None
        self.crons = Crons()
    def recall(self, t, n):
        if getattr(self.crons, str(n), None):
            self.loop.create_task(self.callback(n))
            self.loop.call_later(t, self.recall, t, n)
    async def start(self, n: int, t: int):
        await self.callback(n)
        await self.crons.new(n)
        self.loop.call_later(t, self.recall, t, n)
    async def stop(self, n: int):
        await self.crons.close(n)
    def spamming(self):
        def func(callback):
            self.callback = callback
        return func
