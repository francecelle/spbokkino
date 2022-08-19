class MyLogger:
    def __init__(self, max: int=10):
        self.logs = []
        self.max = max
    def log(self, text: str):
        print(text)
        if len(self.logs) < self.max:
            self.logs.append(text)
        else:
            self.logs.pop(0)
            self.logs.append(text)
            
            
logger = MyLogger()