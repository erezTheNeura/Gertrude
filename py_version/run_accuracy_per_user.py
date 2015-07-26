
print("Begin Exec. Gertrud") 

import sys
import connect_db
import numpy as np
import time

# Input parameters 
dateInt_startTime = int(sys.argv[1])#20150619
dateInt_endTime = int(sys.argv[2])#20150622
number_of_users = int(sys.argv[3])



users = connect_db.get_users(dateInt_startTime,dateInt_endTime,number_of_users)

#users = [1439]

# Accuracy parameters in minutes
time_threshold = int(sys.argv[4])
if len(sys.argv)>5:
	users = sys.argv[5].split(",")
	users = map(int, users)

import detection
print ("reached here")
result = dict() 
users_with_neura_events = 0
users_with_timeline_events = 0

for user_id in users:
	
	print 'Started working on user ' + str(user_id)

	# Compute the event from the DB
	neura_events = connect_db.get_neura_events(user_id, dateInt_startTime, dateInt_endTime)
	timeline_events = connect_db.get_timeline_events(user_id, dateInt_startTime, dateInt_endTime)
	
	# Count users without neura_event
	if len(neura_events) > 0 :
		users_with_neura_events += 1
	if len(timeline_events) > 0 :
		users_with_timeline_events += 1

	# Add errors
	if (len(timeline_events)>0) & (len(neura_events) > 0):
		result_per_user = detection.get_detection_rate(neura_events,timeline_events,time_threshold,dict())
		result[user_id] = result_per_user["total"]
		result[user_id]['id'] = user_id
	else : 
		#result[user_id] = dict()
		#result[user_id]['true_positive'] = float('NaN')
		#result[user_id]['false_positive'] = float('NaN')
		#result[user_id]['accuracy'] = float('NaN')
		#result[user_id]['id'] = user_id
		print "NO DATA"

# Show users distribution 
print 'Number of users with neura events is ' + str(users_with_neura_events)
print 'Number of users with timeline events is ' + str(users_with_timeline_events)

# Translate result from dict to list 
result_list = []
for key in result:
	result_list.append(result[key])

# write file to csv
import csv
filename =time.strftime("%Y%m%d_%H:%M_") + 'test_per_user_' + str(len(users)) +".csv"

with open(filename, 'wb') as f:
	fieldnames = ['id', 'TR', 'T', 'R', 'RT', 'true_positive', 'false_positive', 'accuracy']
	writer = csv.DictWriter(f, fieldnames = fieldnames)
	writer.writeheader()
	writer.writerows(result_list)
