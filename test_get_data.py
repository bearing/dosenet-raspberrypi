import os
from auxiliaries import get_data
file_path =  os.path.abspath("data-log")
output = get_data(file_path)
print(output)
