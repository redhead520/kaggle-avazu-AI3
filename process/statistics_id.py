import marshal

"""
    统计不同user ID出现次数、不同device_ip出现次数、不同device_id出现次数
"""


def statistics(in_file):
    file = open(in_file)
    line = file.readline()
    count = 0
    while True:
        line = file.readline()
        if not line:
            break
        count += 1
        if count % 100000 == 0:
            print count
        category_list = line.split(",")
        # user_id
        index = len(category_list) - 7
        user_id = "v_" + category_list[index]
        if user_id in statistics_id:
            statistics_id[user_id] += 1
        else:
            statistics_id[user_id] = 1
        # device_ip
        index = len(category_list) - 19
        device_ip = "j_" + category_list[index]
        if device_ip in statistics_id:
            statistics_id[device_ip] += 1
        else:
            statistics_id[device_ip] = 1
        # device_id
        index = len(category_list) - 20
        device_id = "i_" + category_list[index]
        if device_id in statistics_id:
            statistics_id[device_id] += 1
        else:
            statistics_id[device_id] = 1
    file.close()


statistics_id = {}

statistics("../new_train")
statistics("../new_test")

marshal.dump(statistics_id, open("../statistics_id", "w"))
