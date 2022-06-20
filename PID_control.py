import sensor, image, time, mjpeg
from pid import PID

from helpers.gc_streamer import GcodeStreamer
import helpers.camera as cam

def setup(max_rate, accel):
    # setup sensor
    cam.wakeup()

    # initialize grbl
    uart = GcodeStreamer(3, 115200)
    uart.wakeup()
    uart.send_gcode('G17 G21 G90') # XY plane selection, programming in millimeters (mm), absolute coordinates
    uart.send_gcode('$110=' + str(max_rate))
    uart.send_gcode('$111=' + str(max_rate))
    uart.send_gcode('$120=' + str(accel))
    uart.send_gcode('$121=' + str(accel))
    return uart

def control_loop(params, uart):
    m = mjpeg.Mjpeg("example.mjpeg")
    led1 = cam.set_LED('P7')

    clock = time.clock()
    thresholds = [(0, 24, -128, 127, -128, 127)]
    rx, ry = 160, 120 # desired output for QVGA
    sf = 1 # scaling factor = n unit length in grbl per pixel length

    # initialize pid
    pidx = PID(p=params[2], i=params[3], d=params[4], imax=90)
    pidy = PID(p=params[5], i=params[6], d=params[7], imax=90)

    params = [str(x) for x in params]
    fname = '_'.join(params)
    fname = '/' + fname + '.txt'
    f = open(fname, 'w')
    t = time.ticks_ms()

    fps = 0
    count = 0
    cum_err_x = 0
    cum_err_y = 0

    while(True):
        clock.tick()
        t0 = time.ticks_ms()
        [x0, y0, z0] = uart.get_mpos()
        # [x0, y0, z0] = uart.wait_until_Idle()
        cx, cy, img = cam.tracking(thresholds, pixels_threshold=75, area_threshold=75)
        m.add_frame(img)

        # get control signal from error
        ux = pidx.get_pid(cx-rx, 1)
        uy = pidy.get_pid(ry-cy, 1)
        if abs(ux)<=60 and abs(uy)<=60 and (abs(ux)>=7.5 or abs(uy)>=7.5):
            uart.send_gcode('G00' + ' X' + str(x0+ux*sf) + ' Y' + str(y0+uy*sf))
        else:
            print(ux, uy)
        t1 = time.ticks_ms()
        f.write(str(cx-rx) + ' ' + str(cy-ry) + ' ' + str(time.ticks_diff(t1, t)) + ', ')
        cum_err_x += abs(cx-rx)
        cum_err_y += abs(cy-ry)
        # print(time.ticks_diff(t1, t0))
        fps += clock.fps()
        count += 1
        if time.ticks_diff(t1, t) >= 60*1000:
            break

    print(fps/count)
    f.close()
    led1.off()
    m.close(clock.fps())
    return cum_err_x, cum_err_y, count

def main():
    params = ['220524', 0, 1.2, 0, 0.05, 1.2, 0, 0.05, 8000, 750]
    uart = setup(params[8], params[9])
    control_loop(params, uart)

main()
