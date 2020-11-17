import pickle
import os
import numpy as np


path = r'D:\RVT_py\debug'
filename = 'debug.txt'
pickle_file = os.path.join(path, filename)
pix_array = pickle.load(open(pickle_file, "rb"))
print(np.min(pix_array))

#print(len(pix_array))

# layers = rvt.blend.BlenderLayers()
# layers.layers = pix_array
# # print(len(layers.layers))
# #print(layers.layers[-1].vis)
#
# for lyr in layers.layers:
#     if lyr.image is None:
#         print("None")
#         continue
#     print("{} {}".format(lyr.vis, lyr.image_path))

#print(layers.render_all_images())

# ###
# import pickle
# import os

# debug_logs_directory = r'D:\RVT_py\debug'
# fname = 'debug.txt'
# filename = os.path.join(debug_logs_directory, fname)
# pix_array = multihillshade
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