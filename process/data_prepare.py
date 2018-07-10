import marshal

train = "../new_train"
test = "../new_test"
set_sf = marshal.load(open("../statistics_feature"))
set_si = marshal.load(open("../statistics_infrequent"))
pre_train = "../train_pre"
pre_test = "../test_pre"

statistics_user_appear = marshal.load(open("../statistics_user_appear"))


def generate_new_data(in_file, out_file, isTest):
    file = open(in_file)
    new_file = open(out_file, "w")
    line = file.readline()
    print >> new_file, line[:-1]
    count = 0
    offset = 3
    if isTest:
        offset = 2
    while True:
        line = file.readline()
        if not line:
            break
        count += 1
        if count % 100000 == 0:
            print count
        category_list = line[:-1].split(",")
        uid = "??"
        for i in xrange(offset, len(category_list)):
            label = chr(ord('a') + i - offset)
            if label == "j":
                ip = label + "_" + category_list[i]
                infrequent = set_si.get(ip)
                if infrequent is not None:
                    category_list[i] = "j_infrequent_" + str(infrequent)
                    continue
            if label == "i":
                id = label + "_" + category_list[i]
                infrequent = set_si.get(id)
                if infrequent is not None:
                    category_list[i] = "i_infrequent_" + str(infrequent)
                    continue
            if label == "v":
                id = label + "_" + category_list[i]
                uid = id
                infrequent = set_si.get(id)
                if infrequent is not None:
                    category_list[i] = "v_infrequent_" + str(infrequent)
                    continue
                elif statistics_user_appear.get(id) == 1:
                    category_list[i] = "v_id_s"
                    continue
            if label + "_" + category_list[i] not in set_sf and i < len(category_list) - 6:
                category_list[i] = label + "_infrequent"
            else:
                category_list[i] = label + "_" + category_list[i]
        category_list.append("statistics_user_appear_" + str(statistics_user_appear[uid]))
        print >> new_file, ",".join(category_list)
    file.close()
    new_file.close()


generate_new_data(train, pre_train, False)
generate_new_data(test, pre_test, True)
