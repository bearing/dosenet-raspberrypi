import os
from auxiliaries import get_data
#file_path =  os.path.abspath("data-log")
for r,d,f in os.walk("c:\\"):
    for files in f:
         if files == "data-log":
              file_path = os.path.join(r,files)
output = get_data(file_path)
print(output)
