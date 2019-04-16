import matplotlib.pyplot as plt
import numpy as np

from database import Database

plt.rcParams['font.sans-serif']=['Microsoft YaHei']
database = Database()
users = database.tracked()

if __name__ == '__main__':
    for nickname in list(users.keys())[0:10]:
        data = database.fetch_data(nickname)
        times = list(data.keys())
        times_offset = [(time - times[0]) / 3600 for time in times]
        nums = list(data.values())
        nums_offset = [num - nums[0] for num in nums]
        plt.plot(times_offset, nums_offset, label=nickname)

    plt.legend()
    plt.show()