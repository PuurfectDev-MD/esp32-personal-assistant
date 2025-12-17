
class AssistantPage:
     def __init__(self, client, led):
         client = self.client
         led  = 
         
         display.draw_text(270, 210, "Muted", arcadepix, WHITE)
         print("AI OFf")
         mutemic = Sprite("images/micmute84-106.raw", 84, 106, display, 120, 80)
         mutemic.draw()
         assistant_module.assistant_led(0)
         client.publish(b"jarvis/control", b"sleep")
         #draw_ui
         # setup assistant button
        
         
    def handle_touch(self, x, y):
        #blah blah
        
    
    


    