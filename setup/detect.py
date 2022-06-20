"""
Open camera, find blob, and mark blob. 
This is a modified version of OpenMV example single_color_rgb565_blob_tracking.py.
"""

import time, mjpeg
import helpers.camera as cam

# led1 = cam.set_LED('P7')
# Color Tracking Thresholds (L Min, L Max, A Min, A Max, B Min, B Max)
# Tune thresold using threshold editor in tools >> machine vision
thresholds = [(0, 16, -128, 127, -128, 127)]
cam.wakeup()
clock = time.clock()
f = open('/results.txt', 'w') 
t1 = time.ticks_ms()

while(True):
    clock.tick()
    cx, cy, img = cam.tracking(thresholds, pixels_threshold=100, area_threshold=100)
    f.write(str(cx) + ' ' + str(cy) + ', ')
    print("FPS:", clock.fps())

    t2 = time.ticks_ms()
    if time.ticks_diff(t2, t1) >= 100*1000:
        break

f.close()
# led1.off()
