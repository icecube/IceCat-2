from pathlib import Path

from icecube import dataio, icetray
from skymist.skyscan import SkyScan

import config

cfg = config.config()

filename = "run140314_eventid61338661_i3live_te.i3"
filepath = cfg.i3files_dir + filename
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
    njobs = 100
else:
    reco = "splinempe"
    njobs = 10

print(f"Event is HED: {is_HED}")
print(f"Reco: {reco}, njobs: {njobs}")

skyscan = SkyScan()
skyscan.scan_file(
    Path(filepath),
    reco,
    "fine",
    njobs,
    "latest"
)