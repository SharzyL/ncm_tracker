from threading import Lock

class ProcessBar:
    def __init__(self, max, auto_clear = False):
        self.max = max
        self.count = 0
        self.lock = Lock()

    @staticmethod
    def output(portion):
        length = 50
        non_spaces = int(length * portion)
        spaces = length - non_spaces
        line = '[' + non_spaces*'#' + spaces*' ' + ']'
        print(line)

    def update(self):
        self.output(self.count / self.max)

    def wrap(self, func):
        def new_func(*args, **kwargs):
            result = func(*args, **kwargs)
            self.lock.acquire()
            self.count += 1
            self.update()
            self.lock.release()
            return result
        return new_func
