"""
Send G-code to gantry from computer.
This is a modified version of https://github.com/grbl/grbl/blob/master/doc/script/simple_stream.py.
"""

import serial
import time
import tests.trajectory as tj

# f = tj.from_file('D://mouse-tracker//mouse-tracker//tests//linear.gcode')
# f = tj.circle(100, 3, 1)
f, feeds = tj.fake_mouse('B1', 100, 1)

# Wake up grbl
s = serial.Serial('COM5',115200)
s.write(bytes('\r\n\r\n', 'UTF-8'))
time.sleep(10)   # Wait for grbl to initialize
s.flushInput()  # Flush startup text in serial input

# Stream g-code to grbl
for line in f:
    l = line.strip() # Strip all EOL characters for consistency
    print('Sending: ' + l)
    s.write(bytes(l + '\n', 'UTF-8')) # Send g-code block to grbl
    grbl_out = str(s.readline()) # Wait for grbl response with carriage return
    print(' : ' + grbl_out.strip())

# Wait here until grbl is finished to close serial port and file.
input("  Press <Enter> to exit and disable grbl.")

# Close serial port
s.close()
