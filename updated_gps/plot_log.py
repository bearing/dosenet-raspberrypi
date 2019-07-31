import folium
import pandas as pd

df = pd.read_csv("/home/pi/data/map1.csv") # Insert filename between quotes. If file is not in the same directory, insert full filepath

location = folium.Map(location = [37.875381,-122.259019], zoom_start = 15)

header_list = list(df) # Generates a list of column names

popup_text = ''


i = 0

while i < len(df['Latitude']):
	if (df.iloc[i]['Latitude'] != 0.0):
		popup_text = ''
		for label in header_list:
			popup_text += str(label)+":"+'%.5f'%(df.iloc[i][label]) + ' <br>'
		
		print (popup_text)
		folium.Marker([(df.iloc[i]['Latitude']),(df.iloc[i]['Longitude'])],popup = popup_text).add_to(location)
	
	i= i+1

location.save('log.html')
