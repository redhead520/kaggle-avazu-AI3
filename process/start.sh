cd ../GBDT
make
cd ../FM
make

cd ../process

pypy add_category.py
pypy statistics_feature.py
pypy statistics_infrequent.py
pypy statistics_user_appear.py
pypy data_prepare.py
pypy statistics_id.py
pypy category4gbdt.py
pypy simple_index.py
pypy complex_index.py
../GBDT/gbdt -d 5 -t 19 ../GBDT_test ../GBDT_train ../test_gbdt_out ../train_gbdt_out

pypy merge_gbdt.py
../FM/fm -k 8 -t 5 -l 0.00001 ../fm_test_2 ../fm_train_2

pypy merge_gbdt_1.py
../FM/fm -k 8 -t 4 -l 0.00002 ../fm_test_2_1 ../fm_train_2_1
../FM/fm -k 8 -t 10 -l 0.00003 ../fm_test_2_2 ../fm_train_2_2
pypy split.py ../fm_test_2_split ../fm_test_2_1.out ../fm_test_2_2.out

