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
           queue.append(np.array(i))
           
def sum_data(data):
   total = data.popleft()
   i = 1
   while i < len(data):
       total += data.popleft()
       i+=1
   return total
   
   
grab_data()
total = sum_data(queue)

