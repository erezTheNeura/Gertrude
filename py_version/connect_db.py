# Connect to mongoDB
import pymongo
from pymongo import MongoClient

#enviorment = "production"

# Required) database
raws_client = MongoClient(r'mongodb://neuraMan:865554da4397760adda0d822140558be@lighthouse.1.mongolayer.com:10009/neura')
views_client = MongoClient(r'mongodb://neuraMan:865554da4397760adda0d822140558be@lighthouse.1.mongolayer.com:10010/neura_views')

# Required db
raws_db = raws_client['neura']
views_db = views_client['neura_views']

# Required collection
raws_col =  raws_db.neura_events
views_col =  views_db.time_line_events

# Load maps from Neura events and timeline to Getrud_events 
import realtime_to_generic


def get_users(dateInt_startTime, dateInt_endTime, count_win = 1000) :
	#source = ['client', 'server'] # , 'client']
	
	query_ne = {'date': {'$gte': dateInt_startTime,'$lte': dateInt_endTime}} #,\
	#'source': {'$in' : source}}
	users_with_neura_events = set(raws_col.distinct('userId', query_ne))
	users_with_neura_events = users_with_neura_events.intersection(set(range(0,count_win)))
	print 'Number of users with neura events is ' + str(len(users_with_neura_events))
	
	query_tl = {'dateInt': {'$gte': dateInt_startTime,'$lte': dateInt_endTime}}
	users_with_timeline_events = set(views_col.distinct('userId',query_tl))
	users_with_timeline_events = users_with_timeline_events.intersection(set(range(0,count_win)))
	print 'Number of users with timeline events is ' + str(len(users_with_timeline_events))

	return list(users_with_neura_events.intersection(users_with_timeline_events))

# This function returns list of Neura events in Getrud format
def get_neura_events(user_id, dateInt_startTime, dateInt_endTime):
	
	source = ['server','client']

	# Query request
	query = {'userId': user_id , \
	'date': {'$gte': dateInt_startTime,'$lte': dateInt_endTime},\
	'source': {'$in' : source}}

	# Init event list
	events = dict()
	missed_events = dict()

	# Run on data from the database
	for post in raws_col.find(query).sort("timestamp"):
		generic_event = realtime_to_generic.neura_events_to_generic.get(post["name"], None)
		if generic_event == None:
			missed_events[post["name"]] = True
		elif events.get(generic_event["name"] + '_' + generic_event["type"], None) == None:
			events[generic_event["name"] + '_' + generic_event["type"]] = [post["timestamp"]]
		else:
			events[generic_event["name"] + '_' + generic_event["type"]].append(post["timestamp"])

	for i in events :
		events[i] = list(set(events[i]))

	return events

# Find a place label in timeline event document
def get_place_label(post) :
	event_name = None
	search_label = post.get("geolocation", None)
	if search_label != None :
		if len(search_label) > 0 :
			search_label = search_label[0]
			search_label = search_label.get("node", None)
			if search_label != None :
				search_label = search_label.get("label", None)
				if search_label != None : 
					event_name = search_label
	return event_name

# This function returns list of timeline events in Getrud format
def get_timeline_events(user_id, dateInt_startTime, dateInt_endTime): 

	# Query request
	query = {'userId': user_id , 'dateInt': {'$gte': dateInt_startTime,'$lte': dateInt_endTime}}

	# Init event list
	events = dict()
	missed_events = dict()
	sleep_at_place = dict()

	is_last_event_sleep = False

	# Run on data from the database
	for post in views_col.find(query).sort("startTime"):
		event_name = realtime_to_generic.timeline_to_generic.get(post["type"], None)
		
		# Check whether the place is home or work
		place_label = get_place_label(post)
		if event_name == None :
			event_name = place_label

		if event_name == None:
			missed_events[event_name] = True
		elif events.get(event_name + '_start', None) == None:
			events[event_name + '_start'] = [post["startTime"]]
			events[event_name + '_end'] = [post["endTime"]]
		else:
			events[event_name + '_start'].append(post["startTime"])
			events[event_name + '_end'].append(post["endTime"])

		# Check whether the last event was sleep
		if event_name == "sleeping" : 
			if place_label != None :
				event_name = place_label
				if sleep_at_place.get(event_name + '_start', None) == None:
					sleep_at_place[event_name + '_start'] = [post["startTime"]]
					sleep_at_place[event_name + '_end'] = [post["endTime"]]
				else:
					sleep_at_place[event_name + '_start'].append(post["startTime"])
					sleep_at_place[event_name + '_end'].append(post["endTime"])
				# print sleep_at_place
	return events
