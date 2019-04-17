import sqlite3
import os
import time
import re


def format_nickname(nickname):
    """
    由于sql里不允许在列名中出现中划线，故需要把nickname中的中划线转为下划线才能作列名

    :param nickname: 昵称
    :return: 将标点全部转化为下划线后的昵称
    """
    return re.sub(r'\W', '_', nickname)


class Database:
    """
    一个对听歌量数据库操作的API封装
    """
    def __init__(self, db_dir='record.db'):
        """
        初始化，若数据库文件不存在则创建新数据库，并建立如下两张表（初始时无任何数据）
        song_record:
        +-------------------------------------+
        | record time | nickname1 | nickname2 |
        +-------------------------------------+
        | 1423554325  | 1432      | 3241      | //时间戳 + 听歌量 + 听歌量 + ...
        | 1423554923  | 1438      | 3301      |
        +-------------------------------------+
        nickname:
        +----------------------------+
        | nickname        | uid      |
        +----------------------------+
        | Rhove           | 91540849 |
        | 一缕炊烟          | 20452251 |
        | priority_queue  | 324871251|
        +----------------------------+

        :param db_dir: 数据库文件目录
        """
        if os.path.exists(db_dir):
            self.conn = sqlite3.connect(db_dir)
            self.cursor = self.conn.cursor()
        else:
            self.conn = sqlite3.connect(db_dir)
            self.cursor = self.conn.cursor()
            self.cursor.execute('CREATE TABLE song_record (record_time REAL)')
            self.cursor.execute('CREATE TABLE nickname (uid INT NOT NULL, nickname TEXT NOT NULL)')

    def tracked(self, reversed=False, key='uid'):
        """
        获取被记录的用户列表

        :param reversed: 是否颠倒字典键值
        :param key: 返回值的键值类型（'uid' or 'nickname'）
        :return: 一个形如 nickname:uid 或 uid:nickname的字典（依参数key而定），其中 uid 为int类型
        """
        self.cursor.execute('SELECT nickname, uid FROM nickname')
        return {row[1]: row[0] for row in self.cursor} if key == 'uid' \
            else {row[0]: row[1] for row in self.cursor}

    def track(self, uid, nickname):
        """
        将某个用户添加到记录列表

        :param uid: (int/str) UID
        :param nickname: (str) 昵称
        :return: None
        """
        nickname = format_nickname(nickname)
        self.cursor.execute('INSERT INTO nickname (uid, nickname) VALUES (?, ?)', (uid, nickname))
        self.cursor.execute('ALTER TABLE song_record ADD COLUMN %s INT' % (nickname,))

    def untrack(self, nickname_list):
        """
        取消对某些人记录，并将他的数据从数据库中删除
        提供批量操作是因为sqlite里删除列的操作比较慢

        :param nickname_list: 被删除的人的昵称列表（当只有一个人时可以不放入列表中）
        :return: None
        """
        if not isinstance(nickname_list, list):
            nickname_list = [nickname_list]
        tracked_nickname = list(self.tracked().keys())
        new_tracked = ['record_time'] + tracked_nickname
        for nickname in nickname_list:
            self.cursor.execute('DELETE from nickname WHERE nickname = ?', (nickname,))
            new_tracked.remove(nickname)
        param = str(new_tracked)[1:-1].replace('\'', '')
        self.cursor.execute("CREATE TABLE temp AS SELECT %s FROM song_record" % (param,))
        self.cursor.execute("DROP TABLE song_record")
        self.cursor.execute("ALTER TABLE temp RENAME TO song_record")

    def record(self, data_dict):
        """
        将一次记录添加进数据库中

        :param data_dict: 由 昵称:听歌量 组成的字典
        :return: None
        """
        if data_dict == {}:
            return
        t = time.time()
        nickname_tuple = ('record_time',) + tuple((str(nickname) for nickname in data_dict))
        num_tuple = (t,) + tuple(data_dict.values())
        self.cursor.execute('SELECT * FROM song_record')
        self.cursor.execute('INSERT INTO song_record %s VALUES %s' % (nickname_tuple, num_tuple))

    def fetch_data(self, nickname):
        """
        获取某人听歌量数据

        :param nickname: 昵称
        :return: 由 时间戳:听歌量 组成的字典，其中时间戳是float形式
        """
        self.cursor.execute('SELECT record_time, %s from song_record' % (nickname,))
        return {record_time: song_num for record_time, song_num in self.cursor.fetchall()}

    def commit(self, close=False):
        """
        提交对数据库的修改

        :param close: 是否关闭cursor
        :return: None
        """
        self.conn.commit()
        if close:
            self.cursor.close()

    def rollback(self, close=False):
        """
        放弃对数据库的修改

        :param close: 是否关闭cursor
        :return: None
        """
        self.conn.rollback()
        if close:
            self.cursor.close()