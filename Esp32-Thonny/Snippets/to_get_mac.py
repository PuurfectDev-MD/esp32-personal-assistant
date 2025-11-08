import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("My MAC:", wlan.config('mac'))



#CAMERA mac = b'4\x86]B\xf8\xcc'

#main board mac =  b'D\x17\x93|]\x08'