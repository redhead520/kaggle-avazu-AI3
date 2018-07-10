import marshal

"""
   统计用户出现的天数
"""


def stat(in_file, isTest):
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
        # device_ip（设备ip）
        device_ip_index = 12
        if isTest:
            device_ip_index = 11
        new_device_ip = "j_" + category_list[device_ip_index]
        if new_device_ip in user_date:
            user_date[new_device_ip].add(category_list[2][4:6])
        else:
            s = set()
            s.add(category_list[2][4:6])
            user_date[new_device_ip] = s
        #  新建立的用户ID，用于区分不同用户
        device_ip_index = len(category_list) - 7
        user_id = "v_" + category_list[device_ip_index]
        if user_id in user_date:
            user_date[user_id].add(category_list[2][4:6])
        else:
            s = set()
            s.add(category_list[2][4:6])
            user_date[user_id] = s
    file.close()


user_date = {}
day_set = {}

stat("../new_train", False)
stat("../new_test", True)

for atom in user_date:
    day_set[atom] = len(user_date[atom])

marshal.dump(day_set, open("../statistics_user_appear", "w"))
