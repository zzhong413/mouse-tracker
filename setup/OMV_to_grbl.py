import time
from helpers.gc_streamer import GcodeStreamer

uart = GcodeStreamer(3, 115200)
uart.wakeup()

f = ['G17 G20 G90', 'G00 X1 Y0', 'G00 X1 Y1']
for line in f:
    uart.send_gcode(line)

time.sleep(15)
uart.deinit()
