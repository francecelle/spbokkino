import os
from datetime import datetime

class MyLogger:
    def __init__(self, max: int=10):
        self.max = max
    async def log(self, text: str):
        print(text)
        with open("logs.txt", "a+") as f:
            t = f.read()
            if len(t.split("\n")) == self.max:
                f.close()
                os.remove("logs.txt")
                f = open("logs.txt", "a+")
                f.write(t.split("\n")[0:8])
            f.write(f'[{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] {text}\n')
            f.close()


logger = MyLogger()
