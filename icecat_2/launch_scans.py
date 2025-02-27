from pathlib import Path

from icecube import dataio, icetray
from skymist.skyscan import SkyScan

import config
cfg = config.config()


#Run = 134535, evt = 41069485
#Run = 122605, evt = 60656774
#run = 134552, evt = 68615710

# 123986, EventID: 77999595

#filename = "run118973_eventid25391094_old_te.i3"
#filename = "run130684_eventid80612787_old_te.i3"
#filename = "run125929_eventid11025256_old_te.i3"
filename = "run123986_eventid77999595_old_te.i3"
filepath = cfg.i3files_dir + filename
#filepath = '/data/user/gsommani/IceCat-2/output/'+filename
#filepath = '/data/ana/realtime/alert_catalog_v2/input_files/Level2_IC86.2017_data_Run00130684_Subrun00000000_00000260_event80612787.i3.zst'
#filepath = '/data/ana/realtime/alert_catalog_v2/input_files/Level2pass2_IC86.2013_data_Run00123986_Subrun00000000_00000212_event77999595.i3.zst'
#filepath = '/data/ana/realtime/alert_catalog_v2/input_files/Level2_IC86.2017_data_Run00129933_Subrun00000000_00000091_event32926212.i3.zst'
i3file = dataio.I3File(filepath)

is_HED = False
for frame in i3file:
    if frame.Stop == icetray.I3Frame.Physics:
        if frame.Has("Streams"):
            streams = frame.Get("Streams")
            print(streams)
            if "HESE" in streams:
                is_HED = True
        else:
            raise ValueError("The i3 file has not Streams in it!")
        if frame.Has("OnlineL2_SplineMPE_TruncatedEnergy_ORIG_Muon"):
            te_orig = frame.Get("OnlineL2_SplineMPE_TruncatedEnergy_ORIG_Muon")
            te_orig_value = te_orig.energy
            print(f"te_orig: {te_orig_value} GeV")
            if te_orig_value >= 50000:
                is_HED = True
        else:
            raise ValueError("The i3 file has not TE ORIG in it!")

if is_HED:
    reco = "millipede_wilks"
    njobs = 1000
else:
    reco = "splinempe"
    #reco = "splinempe_pointed"
    njobs = 100

print(f"Event is HED: {is_HED}")
print(f"Reco: {reco}, njobs: {njobs}")

#reco = 'millipede_original'
#njobs = 2000
#reco = 'splinempe_pointed'
#njobs=100
skyscan = SkyScan()
skyscan.scan_file(
    Path(filepath),
    reco,
    "fine",
    #"pointed",
    njobs,
    "latest",
    additional_tag='icecat_test'
)
