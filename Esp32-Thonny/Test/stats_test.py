import ujson

stats_today = {}
tag_index = 0

def update_stats_for_schedule(tagname):
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


def update_stats_tag(tag):
    with open("focus_data", "r") as f:
        data = ujson.load(f)
        
        if data[flair]:
             new_record = {
            "start_time" = start_time,
            "end_time" = end_time,
            "focused_time" = elapsed_time,  
            }
            data[tag].append(new_record)
            print("New Record Added")
            with open("tasks.json", "w") as f:
                ujson.dump(data, f)
        

        
