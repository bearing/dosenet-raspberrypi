import json
import gps
import pika

def sendmsgcoords(coords):
	'''
	Sends a message through the selected queue.
	'''
	connection = pika.BlockingConnection(
					  pika.ConnectionParameters('localhost'))
	channel = connection.channel()
	channel.queue_declare(queue='toGUI_GPS')
	message = {'id': 'GPS', 'lat': coords[0], 'lon': coords[1]}

	channel.basic_publish(exchange='', routing_key='toGUI_GPS', body=json.dumps(message))
	connection.close()

def getmsg(queue):
	'''
	Returns first body from queue and acknowledges it automatically.
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost')) 
	channel = connection.channel()
	channel.queue_declare(queue=queue)
	
	return channel.basic_get(queue=queue, auto_ack=True)[2]

def getlastmsg(queue, text):
	'''
	Returns last body from queue and acknowledges all of the bodies in queue
	'''
	while True:
		body = getmsg(queue)
		if str(body) == 'None':
			break
		text=str(body)
	return text

if __name__ == '__main__':
	session = gps.gps("localhost","2947")
	session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
	while True: # Starts collecting and plotting data
		#lat, lon = uniform(37.875830,37.878), uniform(-122.268459,-122.278)
		
		# Uncomment the following block and delete the preceeding when it is time to incorporate actual gps data
		
		lat = 0
		lon = 0
		
		text = getlastmsg('fromGUI_GPS', None)
		
		if text == 'EXIT':
			break
		
		try:
			report = session.next()
			print report
			if report['class'] == "TPV":
				lat = report.lat #getattr(report, 'lat', 0.0) #report.lat
				lon = report.lon #getattr(report, 'lon', 0.0) #report.lon
		except KeyError:
			pass
		except KeyboardInterrupt:
			quit()
		except StopIteration:
			session = None
			print "Gpsd has terminated"
		
		print(str(lat) + ' | ' + str(lon))
		
		sendmsgcoords([lat, lon])

# This was made by Big Al and Edward Lee
