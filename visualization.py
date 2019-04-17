import matplotlib.pyplot as plt

from database import Database

time_base = 1555257600  # 15 Apr 2019 00:00:00 GMT+08:00
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 调整字体，防止中文乱码
database = Database()
users = database.tracked(key='nickname')

if __name__ == '__main__':
    for nickname in list(users.keys()):
        data = database.fetch_data(nickname)
        data = {key: value for key, value in data.items() if value}   # filter None data
        times = list(data.keys())
        times_offset = [(time - time_base) / 3600 / 24 for time in times]   # convert timestamp to number of day
        nums = list(data.values())
        nums_offset = [num - nums[0] for num in nums]
        if nums_offset[-1] < 10:
            continue   # filter inactive user
        plt.plot(times_offset, nums_offset, label=nickname)

    plt.legend()
    plt.show()
