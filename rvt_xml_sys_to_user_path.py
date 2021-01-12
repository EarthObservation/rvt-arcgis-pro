import os
import sys


# Parameters
# you can use the same paths for all three dirs if you wish to overwrite xml files and py files are in that directory
# directory with rft.xml files (the ones with system paths).
xml_dir = r"D:\example_path"
# output directory where new rft.xml files will be saved (if same as xml_dir it overwrites files)
new_xml_dir = r"D:\example_path"
# directory to be replaced to in xml (directory where py files are stored)
change_to_dir = r"D:\example_path"

# If len(sys.argv) > 1 if we input arguments, they are used as parameters otherwise top ones are used.
if len(sys.argv) > 1:
    for i_arg in range(len(sys.argv)):
        if sys.argv[i_arg] == "-xml_dir":
            if i_arg + 1 > len(sys.argv):
                raise Exception("Wrong input parameters!")
            elif sys.argv[i_arg + 1][0] == "-":
                raise Exception("Wrong input parameters!")
            else:
                xml_dir = r'{}'.format(sys.argv[i_arg + 1])
        if sys.argv[i_arg] == "-new_xml_dir":
            if i_arg + 1 > len(sys.argv):
                raise Exception("Wrong input parameters!")
            elif sys.argv[i_arg + 1][0] == "-":
                raise Exception("Wrong input parameters!")
            else:
                new_xml_dir = r'{}'.format(sys.argv[i_arg + 1])
        if sys.argv[i_arg] == "-change_to_dir":
            if i_arg + 1 > len(sys.argv):
                raise Exception("Wrong input parameters!")
            elif sys.argv[i_arg + 1][0] == "-":
                raise Exception("Wrong input parameters!")
            else:
                change_to_dir = r'{}'.format(sys.argv[i_arg + 1])

if not os.path.isdir(xml_dir):
    raise Exception("rvt_xml_sys_to_user_path: Directory xml_dir doesn't exists!")
if not os.path.isdir(new_xml_dir):
    raise Exception("rvt_xml_sys_to_user_path: Directory new_xml_dir doesn't exists!")
if not os.path.isdir(change_to_dir):
    raise Exception("rvt_xml_sys_to_user_path: Directory change_to_dir doesn't exists! "
                    "Can't change paths in xmls if directory doesn't exist!")

path_to_replace = r"[functions]Custom\rvt-arcgis-pro"
xml_files_list = [f for f in os.listdir(xml_dir) if f.endswith('.rft.xml')]  # all .rft.xml files from xml_dir
if xml_files_list == []:
    raise Exception("rvt_xml_sys_to_user_path: There is no .rft.xml files in xml_dir!")

for xml_file in xml_files_list:
    in_file_path = os.path.abspath(os.path.join(xml_dir, xml_file))
    out_file_path = os.path.abspath(os.path.join(new_xml_dir, xml_file))
    dat_in = open(in_file_path, "r")
    out_str = ""
    for line in dat_in:
        out_str += (line.replace(path_to_replace, change_to_dir))
    dat_in.close()
    dat_out = open(out_file_path, "w")
    dat_out.write(out_str)
    dat_out.close()

input("Press any key to close...")
