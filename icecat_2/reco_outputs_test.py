import numpy as np
from icecube import dataio, icetray
from skymist.skyscan import SkyScan

import config
cfg = config.config()

def launch_reco_output(run,evtid,reco_algo,scan_id):

    led_hed=False
    angular_error_floor=None
    if(reco_algo=='splinempe'):
        if(run>=140033):
            led_hed==True
        else:
            angular_error_floor=0.2

    api = SkyScan()
    api.plot(
        scan_id=scan_id,
        led_hed=led_hed,
        systematics=False,
        plot_4fgl=True,
        angular_error_floor=angular_error_floor,
        llh_map=False,
    )


launch_reco_output(118973,22324184,'millipede_wilks','ee7cf20a89d4482e82eba3219c357282')
launch_reco_output(130220,11599241,'millipede_wilks','ba6217144c074010bba752f41b8f3446')
launch_reco_output(133644,43767651,'millipede_wilks','4a547f18be5e42b3b5a340148d3eb575')
