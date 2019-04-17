from threading import Lock
import time
import sys


class ProcessBar:
    """
    一个显示进度条的类
    不支持在进行任务过程同时在控制台输出
    """
    def __init__(self, max_task, show_num=True, show_time=True, auto_clear=True):
        """
        :param max_task: 任务总数
        :param show_num: 是否显示已完成任务数
        :param show_time: 是否显示已用时间
        :param auto_clear: 是否不换行输出
        """
        self.max_task = max_task
        self.count = 0  # 已完成的任务数
        self.lock = Lock()
        self.show_num = show_num
        self.show_time = show_time
        self.auto_clear = auto_clear
        self.start_time = None
        self.started = False
        self.last_len = 0  # 记录上次输出长度，方便退格

    def output(self):
        """
        在每个函数执行完成时调用，显示一个类似于
        |#########                  |  12 / 30  32.1s
        的进度条，并换行

        :return: None
        """
        length = 50  # 进度条的长度
        non_spaces = int(length * self.count / self.max_task)  # 计算占位符'#'的数目
        spaces = length - non_spaces # 计算空格数
        text = '|%s%s|  ' % (non_spaces * '#', spaces * ' ')    # 将要输出的字符串

        if self.show_num:
            text += '%d / %d  ' % (self.count, self.max_task)
        if self.show_time:
            seconds = time.time() - self.start_time
            text += '%.1fs' % seconds

        print(text, end='' if self.auto_clear and self.count < self.max_task else '\n')    # 当需要自动清除时，这里不换行
        sys.stdout.flush()    # 清空输出缓冲区，否则可能不输出
        self.last_len = len(text)

    def wrap(self, func):
        """
        装饰器函数，调用装饰的函数，并在它完成后显示进度条

        :param func: 被装饰的函数（暂不支持**kwargs)
        :return: 被装饰后的函数（返回值不变）
        """
        def new_func(*args):
            if not self.started:
                self.started = True
                self.start_time = time.time()

            if self.count >= self.max_task:
                raise ValueError('too many tasks')

            result = func(*args)  # 执行函数
            self.lock.acquire()  # 防止多线程调用时输出错乱
            self.count += 1
            if self.auto_clear:
                print('\b' * self.last_len, end='')  # 输出退格用来删除原来的进度条
            self.output()
            self.lock.release()
            return result
        return new_func


if __name__ == '__main__':  # 一个测试程序
    def task():
        time.sleep(0.1)
    bar = ProcessBar(20)
    for i in range(20):
        bar.wrap(task)()
