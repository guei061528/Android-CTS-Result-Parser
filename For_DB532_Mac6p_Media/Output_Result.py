import sys
from functions.ParseFunction import *

if len(sys.argv) < 3:
    print('Update result usage: %s <New Report> <Update Report> <Report Path> <Trigger Number>' % sys.argv[0])
    sys.exit()

New_Result_Path = sys.argv[1]
Report_File= sys.argv[2]

try:
    with open(Report_File, 'r') as file:
        Report = file.readlines()
except:
    print("Error: Report File not found! Please check report file")
    sys.exit()

try:
    with open(Inject_Path, 'r') as file:
        Inject = file.readlines()
except:
    print("Warning: InjectedEnvVars-properties not found! Get information from report txt only")
    Inject_Path = None

try:
    Report_Path = sys.argv[3]
except:
    print("Warning: Report Path is not set... set report path to null")
    Report_Path = None

try:
    Trigger_Num = sys.argv[4]
except:
    print("Warning: Trigger Num is not set... set trigger num to null")
    Trigger_Num = None


new_info_list = get_info(New_Result_Path)[0]



with open('Final_Report.md', 'w') as out_file:
    out_file.write("# Mac6p CTS Media AUTO REPORT\n")
    out_file.write("### Environment Settings\n")
    out_file.write("|Environment| Value|\n")
    out_file.write("| ----------------- |:----------------------- |\n")
    out_file.write("|IMG Type|MacArthur6P-DB532-Odin|\n")
    for i in range(len(new_info_list)):
        out_file.write("|" + str(new_info_list[i][0]).replace('\n', '') + "|" + str(new_info_list[i][1]).replace('\n', '') + "|\n")
    out_file.write("*****\n")
    for i in Report:
        out_file.write(i)
    if Report_Path != None:
        out_file.write("### Result Path: " + Report_Path + "\n")
    if Trigger_Num != None:
        out_file.write("* If you want to save this report, please click on the link below...\n")
        out_file.write("    * [Save Report](http://rtkap1:1194d94e853443945d732d52e098ff6e9e@172.22.54.49:8080/job/AUTO_TEST_Save_Report/buildWithParameters?token=save_report&Trigger_Num=" + Trigger_Num + ")\n")
        out_file.write("    [ <font color=#DC143C>Warring: This will overwrite the original report, please confirm again and click</font> ]\n")