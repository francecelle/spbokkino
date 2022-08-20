from pyrogram import filters

class Cache:
    def __init__(self, client):
        self.pr = {}
        self.dialogs = None
        self.client = client
    def cache_filter(self, name: str):
        async def _filtercache(filter, client, msg):
            if msg.chat.id == self.pr[name]["chat_id"]:
                return True
            else:
                return False
        return filters.create(_filtercache)
    def on(self, type: str):
        df = {"chat_id":0, "args":()}
        def func(callback):
            #setattr(self, type, callback)
            @self.client.on_message(self.cache_filter(type))
            async def call(client, msg):
                await callback(msg, *self.pr[type]["args"])
        self.pr[type] = df
        return func
    async def process(self, name: str, chat_id: int, *other):
        if name:
            self.pr[name] = {"chat_id":chat_id, "args":other}
    async def close(self, name: str):
        if name in self.pr:
            self.pr[name] = {"chat_id":0, "args":()}
