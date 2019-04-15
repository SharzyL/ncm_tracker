from threading import Lock
import time

class ProcessBar:
    """
    一个显示进度条的类
    """
    def __init__(self, max, show_num=True, show_time=True):
        """
        :param max: 任务总数
        :param show_num: 是否显示已完成任务数
        :param show_time: 是否显示已用时间
        """
        self.max = max
        self.count = 0
        self.lock = Lock()
        self.show_num = show_num
        self.show_time = show_time
        self.start_time = None
        self.started = False

    def _start(self):
        """
        在第一个任务开始时自动调用，记录当前时间

        :return: None
        """
        self.started = True
        self.start_time = time.time()

    def output(self):
        """
        在每个任务完成时调用，显示一个类似于
        [#########           ] 12 / 30 time:32.1s
        的进度条，并换行

        :return: None
        """
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
        print('') # 换行

    def wrap(self, func):
        """
        装饰器函数，调用装饰的函数，并在它完成后显示进度条

        :param func: 被装饰的函数（暂不支持**kwargs)
        :return: 由参数序对与返回值所连接成的序对
        """
        def new_func(*args):
            if not self.started:
                self._start()
            result = func(*args)
            self.lock.acquire()
            self.count += 1
            self.output()
            self.lock.release()
            return args + (result,)
        return new_func
