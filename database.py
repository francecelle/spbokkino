import pytz
import pyrogram.enums
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.messages = {
        "1":{"message":None, "active":False, "time":0},
        "2":{"message":None, "active":False, "time":0},
        "3":{"message":None, "active":False, "time":0}
        }
        self.blocked = []
        self.las_time, self.tz = 0, pytz.timezone("Europe/Rome")
    async def get_groups(self, client):
        #if not client.cache.dialogs: #or datetime.now()-timedelta(minutes=15) >= self.last_time:
            #client.cache.dialogs = client.ubot.get_dialogs()
        async for dialog in client.ubot.get_dialogs():
            if dialog.chat.type in (pyrogram.enums.ChatType.SUPERGROUP, pyrogram.enums.ChatType.GROUP):
                if dialog.chat.id not in self.blocked:
                    yield dialog.chat.id
        #self.last_time = datetime.now()
    async def get_blocked(self):
        return self.blocked
    async def block(self, id: int):
        self.blocked.append(id)
    async def unblock(self, id:int):
        self.blocked.remove(id)
    async def set_time(self, t: int, n: int):
        self.messages[str(n)]["time"] = t
    async def set_message(self, msg, n):
        self.messages[str(n)]["message"] = msg
    async def get_mstatus(self):
        v = self.messages
        return self.getstring(v["1"]["active"]), self.getstring(v["2"]["active"]), self.getstring(v["3"]["active"])
    async def get_status(self, n:int):
        return self.messages[str(n)]["active"]
    async def get_time(self, n:int):
        return self.messages[str(n)]["time"]
    async def get_message(self, n:int):
        return self.messages[str(n)]["message"]
    def getstring(self, value: bool):
        return "✅" if  value else  "❌"
