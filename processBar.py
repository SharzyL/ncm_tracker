from threading import Lock
import time

class ProcessBar:
    def __init__(self, max, show_num=True, show_time=True):
        self.max = max
        self.count = 0
        self.lock = Lock()
        self.show_num = show_num
        self.show_time = show_time
        self.start_time = None
        self.started = False

    def start(self):
        self.started = True
        self.start_time = time.time()

    def output(self):
        length = 50
        portion = self.count / self.max
        non_spaces = int(length * portion)
        spaces = length - non_spaces
        print('[' + non_spaces*'#' + spaces*' ' + ']', end=' ')
        if self.show_num:
            print('%d / %d' % (self.count, self.max), end=' ')
        if self.show_time:
            seconds = time.time() - self.start_time
            print('time:%.1fs' % seconds, end='')
        print('') # print \n

    def wrap(self, func):
        def new_func(*args, **kwargs):
            if not self.started:
                self.start()
            result = func(*args, **kwargs)
            self.lock.acquire()
            self.count += 1
            self.output()
            self.lock.release()
            return result
        return new_func
