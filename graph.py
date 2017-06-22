# Python file to graph air quality test results
import numpy
import matplotlib
import csv

results_read = csv.reader("air_quality_test_results.csv", delimiter=",")
graph = matplotlib.pyplot.plotfile(results[1:])
print(results_read)
