import ujson

stats_today = {}
tag_index = 0

def update_stats(tagname):
    global stats_today
    
    with open("tasks.json", "r") as f:
        data = ujson.load(f)
    
    for task in data["tasks"]:   
        if task["summary"].lower() == tagname.lower():
            time_done = task["end_time"] - task["start_time"]
            
            if tagname in stats_today:
                stats_today[tagname] += time_done
            else:
                stats_today[tagname] = time_done
            break 
