import marshal

train = open("../train")
test = open("../test")
statistics_file = open("../statistics_feature", "w")

dict = {}
count = 0
line = train.readline()
while True:
    line = train.readline()
    if not line:
        break
    count += 1
    if count % 100000 == 0:
        print count
    category_list = line[:-2].split(",")
    for i in xrange(3, len(category_list)):
        label = chr(ord('a') + i - 3)
        feature = label + "_" + category_list[i]
        if feature in dict:
            dict[feature] += 1
        else:
            dict[feature] = 1

count = 0
line = test.readline()
while True:
    line = test.readline()
    if not line:
        break
    count += 1
    if count % 100000 == 0:
        print count
    category_list = line[:-2].split(",")
    for i in xrange(2, len(category_list)):
        label = chr(ord('a') + i - 2)
        feature = label + "_" + category_list[i]
        if feature in dict:
            dict[feature] += 1
        else:
            dict[feature] = 1

statistics = []
for atom in dict:
    if dict[atom] >= 10:
        statistics.append(atom)
marshal.dump(set(statistics), statistics_file)
