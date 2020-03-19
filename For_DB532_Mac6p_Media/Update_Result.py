import sys
import re
import copy
import sqlite3
import numpy as np
from functions.ParseFunction import *

if len(sys.argv) < 2:
    print('Update result usage: %s <New Result> <Compare Result> <Release Result> <Test Result>' % sys.argv[0])
    sys.exit()


New_Result_Path = sys.argv[1]
Compare_Result_Path = sys.argv[2]
Compare_Result = np.load(Compare_Result_Path)

for i in range(len(Compare_Result)):
    if Compare_Result[i][2] == 'N/A':
        Compare_Result[i][2] = 'New Fail'

Special_TestCases = ['com.google.android.youtube.gts.DecodePerformanceTest#testVideoDecodePerformance',
                     'android.media.cts.DecodeAccuracyTest#testGLViewLargerHeightDecodeAccuracy',
                     'android.media.cts.DecodeAccuracyTest#testGLViewDecodeAccuracy',
                     'android.media.cts.DecodeAccuracyTest#testGLViewLargerWidthDecodeAccuracy',
                     'android.media.cts.DecodeAccuracyTest#testSurfaceViewVideoDecodeAccuracy'
                     ]

# Get all data, like failed item, failed module, fail number...
new_info_list = get_info(New_Result_Path)[0]
new_test_module = get_info(New_Result_Path)[1]
new_test_fail_num = get_info(New_Result_Path)[2]
new_test_item = get_info(New_Result_Path)[3]
new_test_incomplete_modules = get_incomplete_modules(New_Result_Path)

Result = []
Record_Board = {'TotalFailNum': int(get_total_fail(New_Result_Path)), 'WaiveFailNum': 0, 'FailInPreviousFailNum': 0, 'NewFailNum': 0}

for i in range(len(Compare_Result)):
    if 'Fail' in Compare_Result[i][2] and Compare_Result[i][3] == 'N/A':
        Record_Board['NewFailNum'] += 1
    elif 'Fail' in Compare_Result[i][3] and Compare_Result[i][2] == 'N/A':
        Record_Board['NewFailNum'] += 1
    elif 'Fail' in Compare_Result[i][2] and 'Fail' in Compare_Result[i][3]:
        Record_Board['NewFailNum'] += 1
    else:
        pass
############################################ New Fail in this report #######################################################

if Record_Board['NewFailNum'] != 0:
    Result.append('### New Fail in this report')
    Result.append('|Module |Item |Status |')
    Result.append('| ----------------- |:----------------------- |:----------------------- |')
    for i in range(len(Compare_Result)):
        if 'Fail' in Compare_Result[i][2] and Compare_Result[i][3] == 'N/A':
            Result.append('|%s|%s|<font color=#DC143C>New Fail</font>|' % (Compare_Result[i][0], Compare_Result[i][1]))
        elif 'Fail' in Compare_Result[i][3] and Compare_Result[i][2] == 'N/A':
            Result.append('|%s|%s|<font color=#DC143C>New Fail</font>|' % (Compare_Result[i][0], Compare_Result[i][1]))
        elif 'Fail' in Compare_Result[i][2] and 'Fail' in Compare_Result[i][3]:
            Result.append('|%s|%s|<font color=#DC143C>New Fail</font>|' % (Compare_Result[i][0], Compare_Result[i][1]))
        else:
            pass
else:
    Result.append('### New Fail in this report: N/A')

Result.append('*****')


############################################ Incomplete Modules #######################################################
if len(new_test_incomplete_modules) != 0:
    Result.append('### Incomplete Modules')
    for i in range(len(new_test_incomplete_modules)):
        Result.append('* %s' % (new_test_incomplete_modules[i]))
else:
    Result.append('### Incomplete Modules: N/A')

Result.append('*****')

############################################ Test Detail #######################################################
Result.append('### Test Detail')

Total_Form = ['Total Failed']
Total_Failed_Num = [Record_Board['TotalFailNum']]

for i in range(len(new_info_list)):
    if 'Module' in new_info_list[i][0]:
        Result.append('* %s: %s' % (new_info_list[i][0], new_info_list[i][1]))
for i in range(len(Total_Form)):
    Result.append('* %s: %s' % (Total_Form[i], str(Total_Failed_Num[i])))


new_test_module = my_set_list(new_test_module)
if len(new_test_module) == 0:
    Result.append('* Fail numbers of modules: 0')
else:
    Result.append('* Fail numbers of modules')
    for i in range(len(new_test_module)):
        Result.append('    * %s: %s' % (new_test_module[i], new_test_fail_num[i]))


Result.append('*****')
############################################ Fail Analysis #######################################################
Result.append('### Fail Analysis')
if Total_Failed_Num != 0:
    Result.append('|Module |Item |Release Status |TestBuild Status|')
    Result.append('| ----------------- |:----------------------- |:----------------------- |:----------------------- |')

    for i in range(len(Compare_Result)):
        if 'Pass' in Compare_Result[i][2] and Compare_Result[i][3] == 'N/A':
            Result.append('|%s|%s|<font color=#2E8B57>%s</font>|%s|' % (
            Compare_Result[i][0], Compare_Result[i][1], Compare_Result[i][2], Compare_Result[i][3]))
        elif 'Fail' in Compare_Result[i][2] and 'Pass' in Compare_Result[i][3]:
            Result.append('|%s|%s|<font color=#DC143C>%s</font>|<font color=#2E8B57>%s</font>|' % (
            Compare_Result[i][0], Compare_Result[i][1], Compare_Result[i][2], Compare_Result[i][3]))
        elif 'Fail' in Compare_Result[i][2] and Compare_Result[i][3] == 'N/A':
            Result.append('|%s|%s|<font color=#DC143C>%s</font>|%s|' % (
            Compare_Result[i][0], Compare_Result[i][1], Compare_Result[i][2], Compare_Result[i][3]))
        elif Compare_Result[i][2] == 'N/A' and 'Fail' in Compare_Result[i][3]:
            Result.append('|%s|%s|%s|<font color=#DC143C>%s</font>|' % (
            Compare_Result[i][0], Compare_Result[i][1], Compare_Result[i][2], Compare_Result[i][3]))
        elif 'Fail' in Compare_Result[i][2] and 'Fail' in Compare_Result[i][3]:
            Result.append('|%s|%s|<font color=#DC143C>%s</font>|<font color=#DC143C>%s</font>|' % (
            Compare_Result[i][0], Compare_Result[i][1], Compare_Result[i][2], Compare_Result[i][3]))
        else:
            Result.append('|%s|%s|<font color=#4169E1>%s</font>|%s|' % (
            Compare_Result[i][0], Compare_Result[i][1], Compare_Result[i][2], Compare_Result[i][3]))
else:
    Result.append('#### No fail! No analysis required!')

Result.append('*****')

############################################ Save Report ########################################################

with open('Report.txt', 'w') as out_file:
    for i in range(len(Result)):
        strline = str(Result[i]) + "\n"
        out_file.write(strline)