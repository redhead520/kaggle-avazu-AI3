def get_feature_num(train, max_num):
    file = open(train)
    num = max_num
    while True:
        line = file.readline()
        if not line:
            break
        ss = line.split(" ")
        for i in xrange(1, len(ss)):
            if num < int(ss[i]):
                num = int(ss[i])
    file.close()
    return num


def merge(in_file, gbdt, out_file, num):
    file = open(in_file)
    file_gbdt = open(gbdt)
    new_file = open(out_file, "w")
    while True:
        line1 = file.readline().strip()
        line2 = file_gbdt.readline().strip()
        if not line1:
            break
        gbdt_feature = []
        ss = line2.split(" ")
        for i in xrange(1, len(ss)):
            feature = str(i) + "_" + ss[i]
            idx = dict.get(feature)
            if idx is None:
                dict[feature] = num + 1 + len(dict)
            gbdt_feature.append(str(dict[feature]))
        print >> new_file, line1 + " " + " ".join(gbdt_feature)
    file.close()
    file_gbdt.close()
    new_file.close()


num = -1
dict = {}

input_train = "../fm_train_1"
input_test = "../fm_test_1"

gbdt_train = "../train_gbdt_out"
gbdt_test = "../test_gbdt_out"

output_train = "../fm_train_2"
output_test = "../fm_test_2"
num = get_feature_num(input_train, num)
num = get_feature_num(input_test, num)

merge(input_train, gbdt_train, output_train, num)
merge(input_test, gbdt_test, output_test, num)
