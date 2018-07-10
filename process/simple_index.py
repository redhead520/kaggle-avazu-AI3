from datetime import datetime


def load_name_sample(in_file, isTest):
    file = open(in_file)
    y = []
    line = file.readline()
    index = 3
    if isTest is True:
        index = 2
    count = 0

    while True:
        line = file.readline()
        if line.strip() == "":
            break
        category_list = line.split(',')
        if isTest is False:
            label = int(category_list[1])
            if label == 0:
                label = -1
            y.append(label)
        else:
            y.append(-1)

        current_category = []
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
            idx = dict.get(category_list[i])
            if idx is None:
                current_category.append(len(dict))
                dict[category_list[i]] = len(dict)
            else:
                current_category.append(idx)
        category2string = [str(x) for x in current_category]
        if isTest is True:
            print >> fm_test, str(y[count]) + " " + " ".join(category2string)
        else:
            print >> fm_train, str(y[count]) + " " + " ".join(category2string)
        count = count + 1
        if count % 1000000 == 0:
            print count


start = datetime.now()

dict = {}

fm_train = open("../fm_train_1", "w")
fm_test = open("../fm_test_1", "w")

load_name_sample('../train_pre', False)
load_name_sample('../test_pre', True)

fm_train.close()
fm_test.close()

end = datetime.now()
print (end - start).seconds
