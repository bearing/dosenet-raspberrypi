# Python file to graph air quality test results
import numpy as np
import matplotlib as plot

results = np.loadtxt(fname='air_quality_test_results.csv', delimiter=',')
graph = plot.pyplot.scatter(results)
print(graph)
