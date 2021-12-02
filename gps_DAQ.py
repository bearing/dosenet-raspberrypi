import json
import gps
import pika
import sys
import time
import argparse

sys.stdout.flush()

def send_data(data):
	connection = pika.BlockingConnection(
					  pika.ConnectionParameters('localhost'))
	channel = connection.channel()
	channel.queue_declare(queue='toGUI')
	message = {'id': 'GPS', 'data': data}

	channel.basic_publish(exchange='',
						  routing_key='toGUI',
						  body=json.dumps(message))
	connection.close()

def receive(ID, queue):
	'''
	Returns command from queue with given ID
	'''
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()
	channel.queue_declare(queue=queue)
	method_frame, header_frame, body = channel.basic_get(queue=queue)
	if body is not None:
		message = json.loads(body)
		if message['id']==ID:
			channel.basic_ack(delivery_tag=method_frame.delivery_tag)
			connection.close()
			return message['cmd']
		else:
			connection.close()
			return None
	else:
		connection.close()
		return None

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("--interval", "-i", type=int, default=1)

	args = parser.parse_args()
	arg_dict = vars(args)
	
	session = gps.gps("localhost","2947")
	session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
	
	recorded_time = time.time()
	
	while True: # Starts collecting and plotting data
		#lat, lon = uniform(37.875830,37.878), uniform(-122.268459,-122.278)
		
		# Uncomment the following block and delete the preceeding when it is time to incorporate actual gps data
		
		lat, lon = 0, 0
		
		command = receive('GPS', 'fromGUI')

		if command == 'EXIT':
			print("GPS daq has received command to exit")
			break
		
		try:
			report = session.next()
			#print report
			if report['class'] == "TPV":
				if hasattr(report,'lat'):
					lat = report.lat #getattr(report, 'lat', 0.0) #report.lat
					lon = report.lon #getattr(report, 'lon', 0.0) #report.lon
		except KeyError:
			pass
		except KeyboardInterrupt:
			quit()
		except StopIteration:
			session = None
			print("Gpsd has terminated")
		
		# print(str(lat) + ' | ' + str(lon))
		
		if time.time()-recorded_time >= arg_dict['interval']:
			recorded_time = recorded_time + arg_dict['interval']
			send_data([lat, lon])
					
		sys.stdout.flush()

# This was made by Big Al and Edward Lee
