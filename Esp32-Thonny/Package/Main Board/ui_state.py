
current_page = "home"
current_page_obj = None

def set_page(name, obj):
    global current_page, current_page_obj
    current_page = name
    current_page_obj = obj

