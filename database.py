import sqlite3
import os
import time


class Database:
    def __init__(self, db_dir='data.db'):
        if os.path.exists(db_dir):
            self.conn = sqlite3.connect(db_dir)
            self.cursor = self.conn.cursor()
        else:
            self.conn = sqlite3.connect(db_dir)
            self.cursor = self.conn.cursor()
            self.cursor.execute('CREATE TABLE song_record (record_time REAL)')
            self.cursor.execute('CREATE TABLE nickname (uid INT NOT NULL, nickname TEXT NOT NULL)')

    def tracked(self):
        self.cursor.execute('SELECT nickname, uid FROM nickname')
        return {row[0]: row[1] for row in self.cursor}

    def track(self, uid, nickname):
        self.cursor.execute('INSERT INTO nickname (uid, nickname) VALUES (?, ?)', (uid, nickname))
        self.cursor.execute('ALTER TABLE song_record ADD COLUMN %s INT' % (nickname,))

    def untrack(self, nickname_list):
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
        t = time.time()
        nickname_tuple = ('record_time',) + tuple((str(nickname) for nickname in data_dict))
        num_tuple = (t,) + tuple(data_dict.values())
        self.cursor.execute('SELECT * FROM song_record')
        ins = 'INSERT INTO song_record %s VALUES %s' % (nickname_tuple, num_tuple)
        self.cursor.execute(ins)

    def fetch_data(self, nickname):
        self.cursor.execute('SELECT record_time, %s from song_record' % (nickname,))
        return {record_time: song_num for record_time, song_num in self.cursor.fetchall()}

    def show_nickname(self):
        self.cursor.execute('SELECT * FROM nickname')
        return self.cursor.fetchall()

    def show_record(self, table='song_record'):
        self.cursor.execute('SELECT * FROM %s' % table)
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()
        self.cursor.close()
