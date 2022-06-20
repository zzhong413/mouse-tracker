import pickle
import numpy as np

def from_file(fname):
    """
    G-code files are modified versions of https://github.com/grbl/grbl/wiki/G-Code-Examples.
    """
    f = open(fname, 'r')
    gc = f.read().split('\n')
    f.close()
    return gc

def circle(feed, cyc, r):
    """
    Generate list of g-code for rotary motion.

    Parameters
    ----------
    feed : int
        Feed rate in inch/min.
    cyc : int
        Number of repeats.
    r : int
        Radius.

    Returns
    -------
    g : list
        List of G-code.

    """
    g = []
    g.append('G17 G20 G90 G94') # inches
    g.append('G00 X' + str(-r) + ' Y0')
    for c in range(cyc):
        g.append('G02 X0 Y' + str(r) + ' I' + str(r) + ' J0 F' + str(feed))
        g.append('X' + str(r) + ' Y0 I0 J' + str(-r))
        g.append('X0 Y' + str(-r) + ' I' + str(-r) + ' J0')
        g.append('X' + str(-r) + ' Y0 I0 J' + str(r))
    g.append('G00 X0 Y0') 
    return g

def fake_mouse(nickname, bo, cyc):
    """
    Generate list of g-code from trajectory files in Rosenberg-2021 paper.

    Parameters
    ----------
    nickname : str
        Mouse.
    bo : int
        Bout.
    cyc : int
        Number of repeats.

    Returns
    -------
    g : list
        List of G-code.

    """
    import sys
    module_path = 'D://mouse-tracker//mouse-tracker//tests//rosenberg-2021//' 
    if module_path not in sys.path:
        sys.path.append(module_path)

    with open(module_path+nickname+'-tf', 'rb') as f:
        tf = pickle.load(f)
    tr = tf.ke[bo]
    tr = tr[~np.isnan(tr).any(axis=1)] * 22.5 # 1 unit = 22.5 inches (length of maze), but length of gantry is 16
    tr = tr - np.amin(tr, axis=0) # normalize
    _, ymax = np.amax(tr, axis=0)
    
    if ymax >= 12:
        print('bad trajectory') # cnc x-axis length <= 12
        return ['']
    sf = 0.2 # in small gantry, 1 "inch" = 5 inches
    af = 10 # sampling rate

    tr = tr * sf
    spd = np.diff(tr, axis=0) * 30 * 60 # speed (inch/min); frame rate 30 Hz
    spd[:, 0] = np.convolve(spd[:, 0], np.ones(af)/af, mode='same') # average speed every af frames
    spd[:, 1] = np.convolve(spd[:, 1], np.ones(af)/af, mode='same')
    tr[:, 0] = tr[:, 0]/22.5*16
    feeds = []
    g = []
    g.append('G17 G20 G90 G94') # inches
    for c in range(cyc):
        g.append('G00 X' + str(tr[0, 1]) + ' Y' + str(tr[0, 0]))
        for step in range(0, len(tr)-1, af):
            feed = np.linalg.norm(spd[step, :])
            g.append('G01 X' + str(tr[step+1, 1]) + ' Y' + str(tr[step+1, 0]) + ' F' + str(feed))
            # g.append('G00 X' + str(tr[step+1, 1]) + ' Y' + str(tr[step+1, 0]))
            feeds.append(feed)
        g.append('G00 X0 Y0')
    return g, feeds

    
    
