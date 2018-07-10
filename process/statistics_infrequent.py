import marshal


def statistics(in_file, isTest):
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
        device_id_index = 11
        if isTest:
            device_id_index = 10
        new_id = "i_" + category_list[device_id_index]
        new_ip = "j_" + category_list[device_id_index + 1]
        user_id = "v_" + category_list[len(category_list) - 7]
        if new_id in dict:
            dict[new_id] += 1
        else:
            dict[new_id] = 1
        if new_ip in dict:
            dict[new_ip] += 1
        else:
            dict[new_ip] = 1
        if user_id in dict:
            dict[user_id] += 1
        else:
            dict[user_id] = 1
    file.close()


dict = {}

statistics("../new_train", False)
statistics("../new_test", True)

statistics_infrequent = {}

for feature in dict:
    if dict[feature] <= 10:
        statistics_infrequent[feature] = dict[feature]

marshal.dump(statistics_infrequent, open("../statistics_infrequent", "w"))
