from datetime import datetime


def load_name_sample(in_file, isTest):
    file = open(in_file)
    line = file.readline()
    index = 3
    if isTest is True:
        index = 2
    count = 0
    label = -1
    id = "**"

    dict = {}
    while True:
        isApp = False
        line = file.readline()
        if line.strip() == "":
            break
        category_list = line.split(',')
        id = category_list[0]
        if isTest is False:
            label = int(category_list[1])
            if label == 0:
                label = -1

        current_category = []

        if category_list[index + 2] == "c_85f751fd":
            isApp = True
            dict = dict_app
        else:
            dict = dict_site

        for i in xrange(index, len(category_list)):
            if i == len(category_list) - 2:
                ss = category_list[i].split('_')
                if int(ss[1]) >= 50:
                    category_list[i] = ss[0] + "_50"
            elif i == len(category_list) - 5:
                ss = category_list[i].split('_')
                if int(ss[1]) >= 20:
                    category_list[i] = ss[0] + "_20"
            elif len(category_list) - 8 < i < len(category_list) - 1:
                ss = category_list[i].split('_')
                if int(ss[1]) >= 10:
                    category_list[i] = ss[0] + "_10"

            if isApp is True:
                if category_list[i][0] == "dict" or category_list[i][0] == "e" or category_list[i][0] == "c":
                    continue
            else:
                if category_list[i][0] == "g" or category_list[i][0] == "h" or category_list[i][0] == "file":
                    continue

            idx = dict.get(category_list[i])
            if idx is None:
                current_category.append(len(dict))
                dict[category_list[i]] = len(dict)
            else:
                current_category.append(idx)
        category2string = [str(x) for x in current_category]
        if isApp is False:
            if isTest is True:
                print >> fm_test_1, str(label) + " " + " ".join(category2string)
            else:
                print >> fm_train_1, str(label) + " " + " ".join(category2string)
        else:
            if isTest is True:
                print >> fm_test_2, str(label) + " " + " ".join(category2string)
            else:
                print >> fm_train_2, str(label) + " " + " ".join(category2string)
        count = count + 1
        if count % 100000 == 0:
            print count


start = datetime.now()

dict_app = {}
dict_site = {}

fm_train_1 = open("../fm_train_1_1", "w")
fm_test_1 = open("../fm_test_1_1", "w")
fm_train_2 = open("../fm_train_1_2", "w")
fm_test_2 = open("../fm_test_1_2", "w")

load_name_sample('../train_pre', False)
load_name_sample('../test_pre', True)

fm_train_1.close()
fm_test_1.close()
fm_train_2.close()
fm_test_2.close()

end = datetime.now()

print (end - start).seconds
