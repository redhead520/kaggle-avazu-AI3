from datetime import datetime
import marshal

statistics_id = marshal.load(open("../statistics_id"))


def load_name_sample(in_file, isTest):
    file = open(in_file)
    # save label
    y = []
    # save
    x = []
    line = file.readline()
    index = 3
    if isTest is True:
        index = 2
    count = 0
    isValid = False

    while True:
        line = file.readline().strip()
        if not line:
            break
        category_list = line.split(',')
        if isTest is False:
            # click when the value is 0, value is -1
            label = int(category_list[1])
            if label == 0:
                label = -1
            y.append(label)
            if isValid is False:
                if int(category_list[2][4:6]) > 28:
                    isValid = True
        else:
            y.append(-1)

        current_category = []
        for i in xrange(index, len(category_list)):
            # device_ip
            if i == len(category_list) - 19:
                current_category.append(statistics_id["j_" + category_list[i]])
            # device_id
            elif i == len(category_list) - 20:
                continue
            # user_id(new)
            elif i == len(category_list) - 7:
                current_category.append(statistics_id["v_" + category_list[i]])
            elif i > len(category_list) - 7:
                current_category.append(int(category_list[i]))

        category2string = [str(x) for x in current_category]
        if isTest is True:
            print >> gbdt_test, str(y[count]) + " " + " ".join(category2string)
        else:
            print >> gbdt_train, str(y[count]) + " " + " ".join(category2string)
        count = count + 1
        if count % 1000000 == 0:
            print count


start = datetime.now()

gbdt_train = open("../GBDT_train", "w")
gbdt_test = open("../GBDT_test", "w")

load_name_sample('../new_train', False)
load_name_sample('../new_test', True)

gbdt_train.close()
gbdt_test.close()

end = datetime.now()
print (end - start).seconds
