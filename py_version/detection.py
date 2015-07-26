
import numpy as np
import warnings

# Find minimum value in array
def find_closest(a, p_value):    
    min_val = abs(a[0] - p_value)
    for i in a:
        curr_val = abs(i - p_value)
        if curr_val < min_val:
            min_val = curr_val
    return min_val

# Get two lists
def compute_closest_timing(obs, pred):
    timing = list()
    #if(obs.length > 0 & pred.length > 0) {
    for instance in obs: 
            timing.append(find_closest(pred, instance))	

    return timing

# Gets a list of doubles (error_timing) and an integer (time_threshold)
# Counts the number of instances that are greater or smaller than time_threshold  
def check_valid_timing(error_timing, time_threshold):
    
    positive_detection = 0
    negative_detection = 0
    
    for instance in error_timing: 
        if float(instance) / 60 <= time_threshold:
            positive_detection += 1
        else:
            negative_detection += 1

    return {
        "positive_detection": positive_detection, 
        "negative_detection": negative_detection 
    }

# Gets two lists of doubles and returns the positive-negative computation
def compute_detection(obs,pred,time_threshold):
    return check_valid_timing(compute_closest_timing(obs,pred),time_threshold)

# Gets two lists and time_threshold 
def compute_rat_detection(obs,pred,time_threshold):
    
    direct_metric = compute_detection(obs,pred,time_threshold)
    inverse_metric = compute_detection(pred,obs,time_threshold)

    return {
        "TR" : direct_metric["positive_detection"],
        "T" : direct_metric["negative_detection"],
        "R" : inverse_metric["negative_detection"],
        "RT" : inverse_metric["positive_detection"]
    }

def compute_percentage(a, b):
    if a + b == 0 : 
        return -1
    else:
        return abs(round(100 * (float(a) / (a + b))))

def find_key_value(x,label) :
    #label = "accuracy"
    if (x.get(label,None) != None) and (x[label]>0):
        return x[label]
    else : 
        return float('NaN')

def get_label_value(label) :
    return lambda x: find_key_value(x,label)

def get_detection_rate(neura_events, timeline_events, time_threshold, result):

    # rUnion keys from timeline and neura events
    events_id = set(neura_events.keys())
    events_id = events_id.union(timeline_events.keys())
    
    # For every event type do
    for i in events_id :
        curr_result = dict()
        
        # Build current result
        if timeline_events.get(i, None) == None :
            curr_result = {"TR": 0, "T": 0, "R": len(neura_events[i]), "RT": 0}
        elif neura_events.get(i, None) == None:
            curr_result = {"TR": 0, "T": len(timeline_events[i]), "R": 0, "RT": 0}
        else :
            curr_result = compute_rat_detection(timeline_events[i], neura_events[i],time_threshold)

        # insert to the result
        if result.get(i, None) == None :
            result[i] = curr_result
        else :
            result[i]["TR"] +=  curr_result["TR"]
            result[i]["T"] +=  curr_result["T"]
            result[i]["R"] +=  curr_result["R"]
            result[i]["RT"] +=  curr_result["RT"]

        # Compute metrics
        tr = result[i]["TR"]
        t = result[i]["T"]
        r = result[i]["R"]
        rt = result[i]["RT"]

        result[i]["true_positive"] = compute_percentage(tr,t)
        result[i]["false_positive"] = compute_percentage(rt,r)

        # Add accuracy 
        if not (((t > 0) & (rt + r == 0)) | ((r > 0) & (tr + t == 0))):    
            result[i]["accuracy"] = compute_percentage(rt + tr, r + t)

        # Add event_id
        result[i]["id"] = i

    result["total"] = dict()
    result["total"]["id"] = "total"
    
    # Compute sum
    result["total"]["TR"] = round(np.nansum(map(get_label_value("TR") , result.values())))
    result["total"]["T"] = round(np.nansum(map(get_label_value("T") , result.values())))
    result["total"]["R"] = round(np.nansum(map(get_label_value("R") , result.values())))
    result["total"]["RT"] = round(np.nansum(map(get_label_value("RT") , result.values())))

    # Compute mean
    result["total"]["true_positive"] = round(np.nanmean(map(get_label_value("true_positive") , result.values())))
    result["total"]["false_positive"] = round(np.nanmean(map(get_label_value("false_positive") , result.values())))
    result["total"]["accuracy"] = round(np.nanmean(map(get_label_value("accuracy") , result.values())))
    


    return result







