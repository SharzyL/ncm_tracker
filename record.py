import shutil
from datetime import datetime
from time import sleep

from database import Database
from getter import *

database = Database('record.db') # database 实例
track_dict = database.tracked(reversed=True) # 一个 uid:nickname 字典
track_list = list(track_dict.keys()) # uid 列表


def record():
    """
    根据数据库中的数据进行一次听歌量批量获取操作并写入数据库
    注意：需要调用database.commit()才能保存修改

    :return: None
    """
    data = get_many(get_num, track_list)
    data_dict = {track_dict[uid]: num for uid, num in data.items()}
    database.record(data_dict)
    print("record succeeded")
    print("time: %s" % datetime.now().isoformat(sep=' ', timespec='seconds'))
    print('totally record %d users' % len(track_list))

def add_track(uid=None, nickname=None):
    """
    将一个用户加入到track list中，需提供uid，nickname两参数中的至少一个
    注意：需要调用database.commit()才能保存修改

    :param uid: UID
    :param nickname: 昵称
    :return: None
    """
    if uid or nickname:
        if not nickname:
            nickname = get_nickname(uid)
        if not uid:
            uid = get_uid(nickname)
    else:
        raise ValueError('Empty input')
    if uid in track_list:
        raise ValueError('Existed user')
    database.track(uid, nickname)
    print("successfully add user %s (uid=%d) to track list" % nickname, uid)


if __name__ == '__main__':
    while True:
        record()
        database.commit()
        shutil.copy('record.db', 'C:\_dev\_path')
        sleep(3600)
