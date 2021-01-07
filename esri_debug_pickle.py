import pickle
import os
import numpy as np


path = r'D:\RVT_py\debug'
filename = 'debug.txt'
pickle_file = os.path.join(path, filename)
pix_array = pickle.load(open(pickle_file, "rb"))
print(pix_array)

#print(len(pix_array))


# ###  COPY INTO CODE AND UNCOMMENT IT
# import pickle
# import os

# debug_logs_directory = r'D:\RVT_py\debug'
# fname = 'debug.txt'
# filename = os.path.join(debug_logs_directory, fname)
# pix_array = array
# pickle.dump(pix_array, open(filename, "wb"))
# ###

# except Exception as e:
# exception_type, exception_object, exception_traceback = sys.exc_info()
# filename = exception_traceback.tb_frame.f_code.co_filename
# line_number = exception_traceback.tb_lineno
# err = "Exception type: {}, File name: {}, Line number: {}".format(exception_type, filename, line_number)
# ###
# import pickle
#
# debug_logs_directory = r'D:\RVT_py\debug'
# fname = 'debug.txt'
# filename = os.path.join(debug_logs_directory, fname)
# pix_array = err
# pickle.dump(pix_array, open(filename, "wb"))
# ###