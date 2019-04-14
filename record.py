from getter import *
from database import Database

database = Database('record.db')

track_list = [91540849, 1324116998, 324871251, 481050559, 71493744, 89836002, 33760879, 335241920, 45818549, 349371774,
              310646473, 51147907, 132866939, 269250892, 67272355, 48353, 272415711, 2747182, 51065998]

track_dict = {91540849: 'Rhove',
              349371774: 'CH3I',
              71493744: 'Raven_Shelter',
              89836002: 'Silent_Twilight',
              45818549: 'Evephy_Z',
              324871251: 'priority_queue',
              1324116998: '第一Hentai',
              335241920: '赫卡雑砕面',
              33760879: '绵羊修道士',
              481050559: '人家是可爱爱的Dio哒',
              310646473: 'koroneko_',
              51147907: 'Weikesi_Hp',
              132866939: '初春在鹿野',
              67272355: 'CYchloe',
              269250892: '农夫山泉XZ',
              48353: '网易UFO丁磊',
              2747182: '音左',
              272415711: '烂头背枪_',
              51065998: '风笛手的呼唤'}

def ini():
    for uid, nickname in track_dict.items():
        database.track(uid, nickname)
    database.commit()

def get_track_dict():
    print(get_many(get_nickname, track_list))

def record():
    data = get_many(get_num, track_list)
    param_dict = {track_dict[uid]: num for uid, num in data.items()}
    database.record(param_dict)

if __name__ == '__main__':
    record()
    database.commit()
