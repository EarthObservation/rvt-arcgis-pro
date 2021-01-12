REM path to rvt_xml_sys_to_user_path
set exe_path=".\rvt_xml_sys_to_user_path.exe"

REM you can use the same paths for all three dirs if you wish to overwrite xml files and py files are in that directory
REM directory with rft.xml files (the ones with system paths)
set xml_dir=""
REM output directory where new rft.xml files will be saved (if same as xml_dir it overwrites files)
set new_xml_dir=""
REM directory to be replaced to in xml (directory where py files are stored)
set change_to_dir=""

call %exe_path% "-xml_dir" %xml_dir% "-new_xml_dir" %new_xml_dir% "-change_to_dir" %change_to_dir%

pause