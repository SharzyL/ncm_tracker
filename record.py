from getter import *
from database import Database

database = Database('record.db')
track_dict = database.tracked(reversed=True) # 一个 uid:nickname 字典
track_list = list(track_dict.keys()) # uid 列表


def record():
    """
    进行一次听歌量批量获取操作并写入数据库（not committed)
    :return: None
    """
    data = get_many(get_num, track_list)
    data_dict = {track_dict.get(uid): num for uid, num in data.items()}
    database.record(data_dict)


if __name__ == '__main__':
    record()
    database.commit()
