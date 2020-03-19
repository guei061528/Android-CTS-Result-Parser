import sys
import re
import copy
import sqlite3
from functions.ParseFunction import *

# if len(sys.argv) < 3:
#     print('Comparison report usage: %s <New Report HTML> <Old Report HTML>' % sys.argv[0])
#     print('Single report usage : %s <New Report HTML> empty' % sys.argv[0])
#     sys.exit()

#============================================================= Initial =============================================================#
# Set your Report path
# New_Result_Path = sys.argv[1]
# Old_Result_Path = sys.argv[2]
New_Result_Path = '2020.03.18_13.58.15/test_result_failures_suite.html'
Old_Result_Path = '2020.03.18_13.58.15/test_result_failures_suite.html'
Waive_List_Path = 'Database/WaiveList.db'
conn_waive = sqlite3.connect(Waive_List_Path)
c_w = conn_waive.cursor()

# Get all data, like failed item, failed module, fail number...
new_info_list = get_info(New_Result_Path)[0]
new_test_module = get_info(New_Result_Path)[1]
new_test_fail_num = get_info(New_Result_Path)[2]
new_test_item = get_info(New_Result_Path)[3]
new_test_incomplete_modules = get_incomplete_modules(New_Result_Path)

if Old_Result_Path == 'empty':
    pass
else:
    old_info_list = get_info(Old_Result_Path)[0]
    old_test_module = get_info(Old_Result_Path)[1]
    old_test_fail_num = get_info(Old_Result_Path)[2]
    old_test_item = get_info(Old_Result_Path)[3]
    old_test_incomplete_modules = get_incomplete_modules(Old_Result_Path)

Result = []

Record_Board = {'TotalFailNum': int(get_total_fail(New_Result_Path)), 'WaiveFailNum': 0, 'MediaFailNum': 0, 'GraphicFailNum': 0,
                'FailInPreviousFailNum': 0, 'NewFailNum': 0}
#============================================================= Waive =============================================================#
Result.append('====================================================================')
Result.append("Waive")
new_fail_with_no_waive = copy.deepcopy(new_test_item)
new_fail_module_with_no_waive = copy.deepcopy(new_test_module)

WaiveFailNum_ = 0
for i in range(len(new_test_item)):
    for j in c_w.execute('SELECT * FROM WaiveList ORDER BY Module'):
        if new_test_item[i] == j[1]:
            WaiveFailNum_ += 1
            Result.append('[%s], [%s]' % (j[0], new_test_item[i]))
            new_fail_with_no_waive.remove(new_test_item[i])
            new_fail_module_with_no_waive.remove(new_test_module[i])
            break

Record_Board['WaiveFailNum'] = WaiveFailNum_
#============================================================= Graphic =============================================================#
Result.append('====================================================================')
Result.append('Graphic')
new_fail_with_no_graphic = copy.deepcopy(new_fail_with_no_waive)
new_fail_module_with_no_graphic = copy.deepcopy(new_fail_module_with_no_waive)

GraphFailNum_ = 0
for i in range(len(new_fail_with_no_waive)):
    for j in c_w.execute('SELECT * FROM Graphic ORDER BY Module'):
        if new_fail_with_no_waive[i] == j[1]:
            GraphFailNum_ += 1
            Result.append('[%s], [%s]' % (j[0], new_fail_with_no_waive[i]))
            new_fail_with_no_graphic.remove(new_fail_with_no_waive[i])
            new_fail_module_with_no_graphic.remove(new_fail_module_with_no_waive[i])
            break

Record_Board['GraphicFailNum'] = GraphFailNum_
#============================================================= Media =============================================================#
Result.append('====================================================================')
Result.append('Media')
new_fail_with_no_media = copy.deepcopy(new_fail_with_no_graphic)
new_fail_module_with_no_media = copy.deepcopy(new_fail_module_with_no_graphic)

MediaFailNum_ = 0
for i in range(len(new_fail_module_with_no_graphic)):
    for j in c_w.execute('SELECT * FROM Media ORDER BY Module'):
        if new_fail_module_with_no_graphic[i] == j[0]:
            MediaFailNum_ += 1
            Result.append('[%s], [%s]' % (j[0], new_fail_with_no_graphic[i]))
            new_fail_with_no_media.remove(new_fail_with_no_graphic[i])
            new_fail_module_with_no_media.remove(new_fail_module_with_no_graphic[i])
            break

Record_Board['MediaFailNum'] = MediaFailNum_
#============================================================= Fail item appeared in the previous report =============================================================#
if Old_Result_Path == 'empty':
    clean_new_fail_item = copy.deepcopy(new_fail_with_no_media)
    clean_new_fail_module = copy.deepcopy(new_fail_module_with_no_media)
    pass
else:
    Result.append('====================================================================')
    Result.append('Fail in previous report')
    FailInPreviousFailNum_ = 0
    clean_new_fail_item = copy.deepcopy(new_fail_with_no_media)
    clean_new_fail_module = copy.deepcopy(new_fail_module_with_no_media)
    for i in range(len(new_fail_with_no_media)):
        for j in range(len(old_test_item)):
            if new_fail_with_no_media[i] == old_test_item[j]:
                FailInPreviousFailNum_ += 1
                Result.append('[%s], [%s]' % (new_fail_module_with_no_media[i], new_fail_with_no_media[i]))
                try:
                    clean_new_fail_item.remove(new_fail_with_no_media[i])
                    clean_new_fail_module.remove(new_fail_module_with_no_media[i])
                except:
                    print("remove fail")
                break
    Record_Board['FailInPreviousFailNum'] = FailInPreviousFailNum_
#============================================================= New Fail =============================================================#
Result.append('====================================================================')
Result.append('New fail in this report')

for i in range(len(clean_new_fail_item)):
    Result.append('[%s], [%s]' % (clean_new_fail_module[i], clean_new_fail_item[i]))

Record_Board['NewFailNum'] = len(clean_new_fail_item)



NewFailNum_tmp = Record_Board['TotalFailNum'] - Record_Board['WaiveFailNum'] - Record_Board['GraphicFailNum'] - Record_Board['MediaFailNum'] - Record_Board['FailInPreviousFailNum']

if NewFailNum_tmp == Record_Board['NewFailNum']:
    print("New fail number calculated correctly !!")
else:
    print("New fail number calculated failed, need to check the entire process !!")
#============================================================= Total Conclusion =============================================================#
Result.append('====================================================================')
Result.append('Module:  Fail Num')
new_test_module = my_set_list(new_test_module)

for i in range(len(new_test_module)):
    Result.append('%s: %s' % (new_test_module[i], new_test_fail_num[i]))


Total_Form = ['Total Failed', 'Waive Failed', 'Graphic Failed', 'Media Failed', 'Failed In Previous Report', 'New Failed']
Total_Failed_Num = [Record_Board['TotalFailNum'], Record_Board['WaiveFailNum'], Record_Board['GraphicFailNum'],
                    Record_Board['MediaFailNum'], Record_Board['FailInPreviousFailNum'], Record_Board['NewFailNum']]

Result.append('====================================================================')
Result.append('Total Result')
for i in range(len(Total_Form)):
    Result.append('%s: %s' % (Total_Form[i], Total_Failed_Num[i]))

Result.append('====================================================================')
Result.append('Incomplete Modules')
for i in range(len(new_test_incomplete_modules)):
    Result.append('%s' % new_test_incomplete_modules[i])


with open('Report.txt', 'w') as out_file:
    for i in Result:
        s_i = str(i) + "\n"
        out_file.write(s_i)

conn_waive.close()