import sys
import re
import copy
import sqlite3
import numpy as np
from functions.ParseFunction import *

if len(sys.argv) < 3:
    print('Update result usage: %s <New Result> <Compare Result> <Release Result> <Test Result>' % sys.argv[0])
    sys.exit()

Release = True
Test = True
New_Result_Path = sys.argv[1]
Compare_Result_Path = sys.argv[2]

try:
    Release_Result_Path = sys.argv[3]
    with open(Release_Result_Path, 'r') as file:
        Release_Build_Result = file.readlines()
except:
    print("Warring: Release Result not found! Please check again!")
    Release = False

try:
    Test_Result_Path = sys.argv[4]
    with open(Test_Result_Path, 'r') as file:
        Test_Build_Result = file.readlines()
except:
    print("Warring: Test Result not found! GTS and STS don't have test build result!")
    Test = False

Compare_Result = np.load(Compare_Result_Path)

Special_TestCases = ['com.google.android.youtube.gts.DecodePerformanceTest#testVideoDecodePerformance',
                     'android.media.cts.DecodeAccuracyTest#testGLViewLargerHeightDecodeAccuracy',
                     'android.media.cts.DecodeAccuracyTest#testGLViewDecodeAccuracy',
                     'android.media.cts.DecodeAccuracyTest#testGLViewLargerWidthDecodeAccuracy',
                     'android.media.cts.DecodeAccuracyTest#testSurfaceViewVideoDecodeAccuracy',
                     'VtsHalWifi', 'VtsHalBluetooth'
                     ]

if Release == True or Test == True:
    for i in range(len(Compare_Result)):
        for j in Special_TestCases:
            if j in Compare_Result[i][1]:
                Compare_Result[i][2] = j # for special testcases
else:
    print("Warring: Release-build Result and Test-build Result are not found! Just parse from new report or new fail numbers equal to zero")
    for i in range(len(Compare_Result)):
        if Compare_Result[i][2] == 'N/A':
            Compare_Result[i][2] = 'New Fail'


if Release == True:
    for i in range(len(Compare_Result)):
        for j in Release_Build_Result:
            if Compare_Result[i][1] in j and 'pass' in j:
                Compare_Result[i][2] = 'Single Pass'
            elif Compare_Result[i][2] in j and 'pass' in j: # Compare_Result[i][2] for special testcases
                Compare_Result[i][2] = 'Single Pass'
            elif Compare_Result[i][1] in j and 'fail' in j:
                Compare_Result[i][2] = 'Single Fail'
            elif Compare_Result[i][2] in j and 'fail' in j:  # Compare_Result[i][2] for special testcases
                Compare_Result[i][2] = 'Single Fail'
            else:
                pass

if Test == True:
    for i in range(len(Compare_Result)):
        for j in Test_Build_Result:
            if Compare_Result[i][1] in j and 'pass' in j:
                Compare_Result[i][3] = 'Single Pass'
            elif Compare_Result[i][2] in j and 'pass' in j: # Compare_Result[i][2] for special testcases
                Compare_Result[i][2] = 'N/A'
                Compare_Result[i][3] = 'Single Pass'
            elif Compare_Result[i][1] in j and 'fail' in j:
                Compare_Result[i][3] = 'Single Fail'
            elif Compare_Result[i][2] in j and 'fail' in j:  # Compare_Result[i][2] for special testcases
                Compare_Result[i][2] = 'N/A'
                Compare_Result[i][3] = 'Single Fail'
            else:
                pass


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
############################################ Fail Analysis #######################################################
Result.append('### Fail Analysis')
if Record_Board['TotalFailNum'] != 0:
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