# Python file to graph air quality test results
import numpy as np
import matplotlib as plot

results = np.loadtxt(fname='air_quality_test_results.csv', delimiter=',')
graph = plot.pyplot.plotfile(results[1:])
print(results)
