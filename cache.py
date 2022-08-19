class Cache:
    def __init__(self):
        self.pr = {}
        self.dialogs = None
    def on(self, type: str):
        def func(callback):
            setattr(self, type, callback)
        return func
    async def process(name: str, chat_id: int, *other):
        if name:
            self.pr[name] = {"chat_id":chat_id, "args":other}
    async def close(name: str):
        if name in self.pr:
            del self.pr[name]
    async def call(self, msg):
        for name in self.pr.keys():
            if msg.chat.id == self.pr[name]["chat_id"]:
                callback = getattr(self, name)
                await callback(msg, *self.pr["args"])