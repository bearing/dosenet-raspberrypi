# Python file to graph air quality test results
import numpy
import matplotlib
import csv

results_read = csv.reader("air_quality_test_results.csv", delimiter=",")
print(results_read)
