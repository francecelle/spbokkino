import pytz
import pyrogram.enums
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.messages = {
        1:{"message":None, "active":False, "time":0},
        2:{"message":None, "active":False, "time":0},
        3:{"message":None, "active":False, "time":0}
        }
        self.blocked = []
        self.las_time, self.tz = 0, pytz.timezone("Europe/Rome")
    async def get_groups(self, client):
        if client.cache.dialogs:
            if datetime.now()-timedelta(hours=24) >= self.last_time or not client.cache.dialogs:
                client.cache.dialogs = client.ubot.get_dialogs()
        async for chat in client.cache.dialogs:
            if chat.type in (pyrogram.enums.ChatType.SUPERGROUP, pyrogram.enums.GROUP):
                if chat.id not in self.blocked:
                    yield chat.id
    async def get_blocked(self):
        return self.blocked
    async def block(self, id: int):
        self.blocked.append(id)
    async def unblock(self, id:int):
        self.blocked.remove(id)
    async def set_time(self, t: int, n: int):
        self.messages[n]["time"] = t
    async def set_message(self, msg, n):
        self.messages[n]["message"] = msg
    async def get_mstatus(self):
        v = self.messages
        return self.getstring(v[1]["message"]), self.getstring(v[2]["message"]), self.getstring(v[3]["message"])
    async def get_status(self, n:int):
        return self.messages[n]["active"]
    async def get_time(self, n:int):
        return self.messages[n]["time"]
    async def get_message(self, n:int):
        return self.messages[n]["message"]
    def getstring(self, value: bool):
        return "✅" if  value else  "❌"
    
