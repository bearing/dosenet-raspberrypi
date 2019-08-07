import pandas as pd
import time
from pylab import cm
import matplotlib as mpl
import os

import sys
sys.path.insert(0, 'folium')
sys.path.insert(0, 'branca')

import branca
import folium
from branca.element import MacroElement

from jinja2 import Template

class BindColormap(MacroElement):
    """Binds a colormap to a given layer.

    Parameters
    ----------
    colormap : branca.colormap.ColorMap
        The colormap to bind.
    """
    def __init__(self, layer, colormap):
        super(BindColormap, self).__init__()
        self.layer = layer
        self.colormap = colormap
        self._template = Template(u"""
        {% macro script(this, kwargs) %}
            {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
            {{this._parent.get_name()}}.on('overlayadd', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'block';
                }});
            {{this._parent.get_name()}}.on('overlayremove', function (eventLayer) {
                if (eventLayer.layer == {{this.layer.get_name()}}) {
                    {{this.colormap.get_name()}}.svg[0][0].style.display = 'none';
                }});
        {% endmacro %}
        """)  # noqa

def popuptext(sensor_chosen):
	'''
	Formats text for popup labels
	'''
	# List for popup label (current time and values)
	popup = "Time: " + str(time.ctime(df.iloc[i]['Epoch time'])) + '<br>'
	
	for sensor in header_list[1:]:
		if sensor == sensor_chosen:
			popup = popup + sensor + " (shown): "
		else:
			popup = popup + sensor + ": "

		popup = popup + str(df.iloc[i][sensor]) + "<br>"
	return popup

df = pd.read_csv("/home/pi/data/GPS_GUI_Data_2019-07-31_15:25:39_ACHPRRRRT.csv") # Insert filename between quotes. If file is not in the same directory, insert full filepath

location = folium.Map(location = [37.875381,-122.259019], zoom_start = 15)

sensor_dict = {'Air Quality PM 2.5 (ug/m3)': {'max': 100, 'min': 0}, 'CO2 (ppm)': {'max': 1000, 'min': 300}, 'Humidity (%)': {'max': 60, 'min': 30}, 'Pressure (Pa)': {'max': 101400, 'min': 99500}, 'Radiation (cps)': {'max': 100, 'min': 0}, 'Radiation Bi (cps)': {'max': 15, 'min': 0}, 'Radiation K (cps)': {'max': 15, 'min': 0}, 'Radiation Tl (cps)': {'max': 15, 'min': 0}, 'Temperature (C)': {'max': 30, 'min': 15}} 

header_list = list(df) # Generates a list of column names
sensor_list = header_list[3:]

set_min_and_max = input('Would you like to set the min and max values to plot (y/N)? ')
if set_min_and_max in ['y', 'Y', 'yes', 'Yes']:
	for label in sensor_list:
		minimum = input('Min value for ' + label + ' (For default = ' + str(sensor_dict[label]['min']) + ', input nothing): ')
		maximum = input('Max value for ' + label + ' (For default = ' + str(sensor_dict[label]['max']) + ', input nothing): ')
		if minimum != '':
			sensor_dict[label]['min'] = int(minimum)
		if maximum != '':
			sensor_dict[label]['max'] = int(maximum)

for label in sensor_list:
	sensor_dict[label]['fg'] = folium.FeatureGroup(name=label, show=False)
	sensor_dict[label]['cm'] = branca.colormap.LinearColormap(['b','c','g','y','r'], vmin=sensor_dict[label]['min'], vmax=sensor_dict[label]['max'], caption=label)
	
	location.add_child(sensor_dict[label]['fg'])
	location.add_child(sensor_dict[label]['cm'])
	location.add_child(BindColormap(sensor_dict[label]['fg'], sensor_dict[label]['cm']))

	sensor_dict[label]['fg'].add_to(location)

location.add_child(folium.map.LayerControl())

for i in range(0, len(df['Latitude'])):
	if (df.iloc[i]['Latitude'] != 0):
		for label in sensor_list:
			point_color = mpl.colors.rgb2hex(sensor_dict[label]['cm'].rgba_floats_tuple(df.iloc[i][label]))
			folium.Circle(radius = 15, location = [(df.iloc[i]['Latitude']),(df.iloc[i]['Longitude'])],popup = popuptext(label),fill_color = point_color,color = '#000000',fill_opacity = 1,stroke = 1,weight = 1).add_to(sensor_dict[label]['fg'])

location.save('log.html')
os.system('xdg-open log.html')		
