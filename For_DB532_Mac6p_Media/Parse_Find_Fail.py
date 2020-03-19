import sys
import re
import copy
import sqlite3
import numpy as np
from functions.ParseFunction import *

if len(sys.argv) < 3:
    print('Comparison report usage: %s <New Report HTML> <Old Report HTML>' % sys.argv[0])
    print('Single report usage : %s <New Report HTML> empty' % sys.argv[0])
    sys.exit()

#============================================================= Initial =============================================================#
# Set your Report path
New_Result_Path = sys.argv[1]
Old_Result_Path = sys.argv[2]

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
    print("Old Result Path empty... New report only compares with waive items")
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
#Special_TestCases_Modules = ['GtsYouTubeTestCases', 'CtsMediaTestCases', 'CtsMediaTestCases', 'CtsMediaTestCases', 'CtsMediaTestCases', 'VtsHalWifi']
Special_TestCases_Modules = ['VtsHalWifi'] # "-t testcases" cannot be used for measurements in this module
Special_TestCases = ['com.google.android.youtube.gts.DecodePerformanceTest#testVideoDecodePerformance',
                     'android.media.cts.DecodeAccuracyTest#testGLViewLargerHeightDecodeAccuracy',
                     'android.media.cts.DecodeAccuracyTest#testGLViewDecodeAccuracy',
                     'android.media.cts.DecodeAccuracyTest#testGLViewLargerWidthDecodeAccuracy',
                     'android.media.cts.DecodeAccuracyTest#testSurfaceViewVideoDecodeAccuracy',
                     ] # This testcases will have many similar sub-tests
#============================================================= Waive =============================================================#
new_fail_with_no_waive = copy.deepcopy(new_test_item)
new_fail_module_with_no_waive = copy.deepcopy(new_test_module)

WaiveFailNum_ = 0
for i in range(len(new_test_item)):
    for j in c_w.execute('SELECT * FROM WaiveList ORDER BY Module'):
        if new_test_item[i] == j[1]:
            WaiveFailNum_ += 1
            Result.append([j[0], new_test_item[i], 'Waive Item', 'N/A'])
            new_fail_with_no_waive.remove(new_test_item[i])
            new_fail_module_with_no_waive.remove(new_test_module[i])
            break

Record_Board['WaiveFailNum'] = WaiveFailNum_
#============================================================= Fail item appeared in the previous report =============================================================#

New_Fail_Result = []

if Old_Result_Path == 'empty':
    clean_new_fail_item = copy.deepcopy(new_fail_with_no_waive)
    clean_new_fail_module = copy.deepcopy(new_fail_module_with_no_waive)
    pass
else:
    FailInPreviousFailNum_ = 0
    clean_new_fail_item = copy.deepcopy(new_fail_with_no_waive)
    clean_new_fail_module = copy.deepcopy(new_fail_module_with_no_waive)
    for i in range(len(new_fail_with_no_waive)):
        for j in range(len(old_test_item)):
            if new_fail_with_no_waive[i] == old_test_item[j]:
                FailInPreviousFailNum_ += 1
                Result.append([new_fail_module_with_no_waive[i], new_fail_with_no_waive[i], 'Connect to the Extranet and enter lancher can pass', 'N/A'])
                try:
                    clean_new_fail_item.remove(new_fail_with_no_waive[i])
                    clean_new_fail_module.remove(new_fail_module_with_no_waive[i])
                except:
                    print("remove fail")
                for k in range(len(Special_TestCases)):
                    if Special_TestCases[k] in new_fail_with_no_waive[i]:
                        new_fail_with_no_waive[i] = Special_TestCases[k]
                        New_Fail_Result.append([new_fail_module_with_no_waive[i], new_fail_with_no_waive[i]])
                        break
                break
    Record_Board['FailInPreviousFailNum'] = FailInPreviousFailNum_

#============================================================= Handle Special Modules =============================================================#

clean_special_fail_item = copy.deepcopy(clean_new_fail_item)
clean_special_fail_module = copy.deepcopy(clean_new_fail_module)
New_Fail_Special_Modules = []
for i in range(len(Special_TestCases_Modules)):
    for j in range(len(clean_new_fail_module)):
        if Special_TestCases[i] in clean_new_fail_module[j]:
            New_Fail_Special_Modules.append(clean_new_fail_module[j])
            clean_special_fail_item.remove(clean_new_fail_item[j])
            clean_special_fail_module.remove(clean_new_fail_module[j])

New_Fail_Special_Modules = my_set_list(New_Fail_Special_Modules)
#============================================================= Handle Special TestCases =============================================================#

clean_new_fail_item_final = copy.deepcopy(clean_special_fail_item)
clean_new_fail_module_final = copy.deepcopy(clean_special_fail_module)

for i in range(len(Special_TestCases)):
    First = True
    for j in range(len(clean_special_fail_item)):
        if Special_TestCases[i] in clean_special_fail_item[j]:
            if First == True:
                if Special_TestCases[i] in clean_new_fail_item_final[j] and clean_new_fail_item_final[j] == clean_special_fail_item[j]:
                    clean_new_fail_item_final[j] = Special_TestCases[i]
                pass
            else:
                clean_new_fail_item_final.remove(clean_special_fail_item[j])
                clean_new_fail_module_final.remove(clean_special_fail_module[j])
            First = False

#============================================================= Handle Incomplete Modules =============================================================#
Incomplete_Modules = []

for i in range(len(new_test_incomplete_modules)):
    tmp = 0
    for j in range(len(clean_new_fail_module_final)):
        if new_test_incomplete_modules[i] == clean_new_fail_module_final[j]:
            tmp += 1
    if tmp == 0:
        Incomplete_Modules.append(new_test_incomplete_modules[i])

#============================================================= New Fail =============================================================#


for i in range(len(clean_new_fail_item)):
    Result.append([clean_new_fail_module[i], clean_new_fail_item[i], 'N/A', 'N/A'])

for i in range(len(New_Fail_Special_Modules)):
    New_Fail_Result.append([New_Fail_Special_Modules[i], ''])

for i in range(len(Incomplete_Modules)):
    New_Fail_Result.append([Incomplete_Modules[i], ''])

for i in range(len(clean_new_fail_item_final)):
    New_Fail_Result.append([clean_new_fail_module_final[i], clean_new_fail_item_final[i]])

Record_Board['NewFailNum'] = len(clean_new_fail_item)

# Double-check new fail items number
NewFailNum_tmp = Record_Board['TotalFailNum'] - Record_Board['WaiveFailNum'] - Record_Board['FailInPreviousFailNum']
if NewFailNum_tmp == Record_Board['NewFailNum']:
    print("New fail number calculated correctly !!")
else:
    print("New fail number calculated failed, need to check the entire process !!")

#============================================================= Save result =============================================================#
Compare_Result = np.asarray(Result)
np.save('Compare_Result', Compare_Result)

conn_waive.close()
