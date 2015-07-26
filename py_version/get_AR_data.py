
# Connect to mongoDB
import pymongo
from pymongo import MongoClient

#enviorment = "production"

# Required) database
raws_client = MongoClient(r'mongodb://neuraMan:865554da4397760adda0d822140558be@lighthouse.0.mongolayer.com:10009/neura')
views_client = MongoClient(r'mongodb://neuraMan:865554da4397760adda0d822140558be@lighthouse.0.mongolayer.com:10010/neura_views')

# Required db
raws_db = raws_client['neura']
views_db = views_client['neura_views']

# Required collection
raws_col =  raws_db.activity_minutes
views_col =  views_db.time_line_events

# Load dataframes
import pandas as pd
import numpy as np

# This function returns list of Neura events in Getrud format
def get_data(user_id, startTime, endTime):

    # Query request
    query = {'user_id' : user_id, 'start' : {'$gte': startTime, '$lte' : endTime}}

    # Init event list
    result = dict();
    ar_types = set(["still", "strong_tilting", "tilting"]);
    start = list();


    for post in raws_col.find(query).sort("start").limit(100):
        minute = post["start"] 
        result_instance = result.get(minute,None)
        
        if post["name"] == "still" :
            curr_ar = "still"
        elif post["name"] == "on_foot": 
            curr_ar = "strong_tilting"
        elif post["name"] == "in_vehicle":
            curr_ar = "strong_tilting" 
        # elif post["name"] == "unknown":
        #    curr_ar = "strong_tilting"     
        else :
            curr_ar = "tilting"

        if result_instance == None :
            result[minute] = [curr_ar]
        else:
            result[minute].append(curr_ar)

        # Save the current minute
        start.append(minute)

        # Insert ar to types 
        ar_types.add(curr_ar)

    if len(start) == 0 | len(ar_types) < 2 :
        return list();
        
    # Convert ar_types to list
    ar_types = list(ar_types)

    # Find maximum and minimum values of start
    # start_minimum = np.min(start) 
    # start_minimum -= start_minimum % 60
    start_minimum = startTime        

    # start_maximum = np.max(start) 
    # start_maximum -= start_maximum % 60 
    start_maximum = endTime

    time_col = list(np.arange(start_minimum, start_maximum, 60))
    time_col.append(start_maximum+60)

    time_col.append(start_maximum)
    ar_values = np.zeros((len(time_col), len(ar_types)))

    for instance in result :
        col = ar_types.index(result[instance][0])
        row = time_col.index(instance -  instance % 60)
        #if col == "tilting" : 
        #    value = np.log(row+1) 
        #else: 
        #    value = 1
        value = np.log(row+1)
        ar_values[row,col] = value

    b = pd.DataFrame(ar_values, index=time_col, columns=ar_types)
    
    return b


def get_sleeeping(user_id, dateInt_startTime, dateInt_endTime): 

    # Query request
    query = {'userId': user_id , 'dateInt': {'$gte': dateInt_startTime,'$lte': dateInt_endTime}, "type": "sleeping"}
    restrict = {"startTime" : 1, "endTime" : 1, "duration" : 1}

    # Init event list
    result = []
    
    # number of minutes in boundery
    bound_min = 30

    # Run on data from the database
    for post in views_col.find(query,restrict).sort("startTime"):
        # result.append({"startTime" : int(post["startTime"]) + 60 * 10, "endTime" : int(post["endTime"]) + 60*10})
        # result.append({"startTime" : int(post["endTime"]) - 60*bound_min, "endTime" : int(post["endTime"]) + 60*bound_min, "duration": int(post["duration"])/60})
        result.append({"startTime" : int(post["endTime"]) - 60*5, "endTime" : int(post["endTime"]) + 60*bound_min, "duration": int(post["duration"])/60})

    return result





