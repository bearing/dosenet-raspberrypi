from collections import deque
import ast
from globalvalues import DEFAULT_DATALOG_D3S
import numpy as np
import os

queue = deque('')

def grab_data(path=DEFAULT_DATALOG_D3S):
    if os.path.isfile(path):
        with open(path, 'r') as f:
            data = f.read()
        data = ast.literal_eval(data)
        for i in data:
           queue.append(i[1])
           
def sum_data(data):
   for i in data:
       i = np.array(i)
   total = data[0]
   i = 1
   while i < len(data):
       total += data[i]
       i+=1
   return total
   
   
grab_data()
total = sum_data(queue)
print total
