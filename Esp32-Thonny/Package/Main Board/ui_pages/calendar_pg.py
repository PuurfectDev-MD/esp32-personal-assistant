import ui_module
import setup
from setup import display, rtc, font, font2, rtc_power, spi, touch, colors, arcadepix, bally, Sprite
import ujson


WHITE   = 0xFFFF
BLACK   = 0x0000
RED     = 0xF800
GREEN   = 0x07E0


offset= 15
cols = 4  # Number of columns
rows = 3  # Number of rows
rect_width = (display.width- offset) // cols  
rect_height = display.height // rows


max_width_text = rect_width
Hpriority_c = 27
mid_priority_c = 26
low_priority_c = 25

priority_colors = {
    "High": Hpriority_c,
    "Mid": mid_priority_c,
    "Low": low_priority_c
}


class CalendarPage:
    def __init__ (self):
        display.clear()
        schedule = "SCHEDULE"
        
        for i in range(len(schedule)):
            display.draw_text(5, 45 + (i*22), schedule[i], setup.espresso_dolce , WHITE)
        
        draw_schedule_cells()
        
    
    def handle_touch(self, x, y):
        print(f"x :{x} , y :{y}")
        
    

def draw_schedule_cells():

    with open("tasks.json", "r") as f:
        data = ujson.load(f)
        
    tasks = data["tasks"]

    task_number = len(tasks)
    print(f"task_number  = {task_number}")
    task_slot_used = 0
    non_task_color = 9

    for row in range(rows): 
        for col in range(cols):  
            x = col * rect_width  
            y = row * rect_height  

            # Skip the very first slot
            if row == 0 and col == 0:
                continue

            if task_slot_used < task_number:   # Only for actual tasks
                task = tasks[task_slot_used]
                priority = task.get("priority", "Low")   
                cell_color = priority_colors.get(priority, low_priority_c)  

                # Draw cell background first
                display.fill_rectangle(x+17, y, rect_width - 1, rect_height - 1,
                                       colors[cell_color])

                

                # Draw task text
                text = task["task"]
                time_start = task["time"]
                time_end = task["time_end"]

                if len(text) * 7 > max_width_text:
                    chars_fit = max_width_text // 7
                    text = text[:chars_fit - 3] + "..."

                display.draw_text(x+20, y+60, text, arcadepix, BLACK, colors[cell_color])
                display.draw_text(x+20, y+5, "Time", arcadepix, BLACK, colors[cell_color])
                display.draw_text(x+20, y+20, f"{time_start} to", arcadepix, BLACK, colors[cell_color])
                display.draw_text(x+20, y+30, time_end, arcadepix, BLACK, colors[cell_color])
                
                # Draw alarm clock sprite **once per task cell**
                alarm_sprite = Sprite("images/clock12-12.raw", 12, 12, display, x+52, y+2)
                alarm_sprite.draw()

                # Draw status circle
                if get_task_status(task_slot_used):
                    display.fill_circle(x+82, y+7, 5, GREEN)
                else:
                    display.fill_circle(x+82, y+7, 5, BLACK)

             
                task_slot_used += 1

            else:  # Fill empty cells
                display.fill_rectangle(x+17, y, rect_width - 1, rect_height - 1,
                                       colors[non_task_color])




def get_task_status(task_number):
    with open("tasks.json", "r") as f:     
        data = ujson.load(f)
        
    tasks = data["tasks"]
    task = tasks[task_number]
    status = task.get("completed").upper()
    
    if status == "YES":
        return True
    else:
        return False

        
    
    


