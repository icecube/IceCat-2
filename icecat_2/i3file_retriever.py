from datetime import timedelta
import base64
from pathlib import Path
import pickle
import zlib
import os

from icecube import (
    dataio,
    icetray,
    gulliver,
    recclasses,
)
from icecube.icetray import I3Tray
from icecube.frame_object_diff.segments import uncompress

from skymist import i3live

from . import config

cfg = config.config()

class GCD_Handler:
    

    def __init__(self):
        self.base_filename = ""
        self.base_geo = None
        self.base_cal = None
        self.base_det = None


    def get_base_gcd_frames(self, base_filename: str):
        self.base_filename = base_filename
        base_path = cfg.baseline_gcd_path + self.base_filename
        i3baseline = dataio.I3File(base_path)
        for baseframe in i3baseline:
            if baseframe.Stop == icetray.I3Frame.Geometry:
                self.base_geo = baseframe.Get("I3Geometry")
            elif baseframe.Stop == icetray.I3Frame.Calibration:
                self.base_cal = baseframe.Get("I3Calibration")
            elif baseframe.Stop == icetray.I3Frame.DetectorStatus:
                self.base_det = baseframe.Get("I3DetectorStatus")
        return

        
    def prepare_geometry(self, frame):
        diff_geo = frame.Get("I3GeometryDiff")
        self.get_base_gcd_frames(diff_geo.base_filename)
        frame.Put(
            "I3Geometry",
            diff_geo.unpack(self.base_geo),
            icetray.I3Frame.Geometry
        )
        frame.Delete("I3GeometryDiff")
        return frame


    def prepare_calibration(self, frame):
        diff_cal = frame.Get("I3CalibrationDiff")
        frame.Put(
            "I3Calibration",
            diff_cal.unpack(self.base_cal),
            icetray.I3Frame.Calibration
        )
        frame.Delete("I3CalibrationDiff")
        return frame


    def prepare_detector_status(self, frame):
        diff_det = frame.Get("I3DetectorStatusDiff")
        frame.Put(
            "I3DetectorStatus",
            diff_det.unpack(self.base_det),
            icetray.I3Frame.DetectorStatus
        )
        frame.Delete("I3DetectorStatusDiff")
        return frame


    def prepare_GCD_from_diff(self, frame):
        if frame.Stop == icetray.I3Frame.Geometry:
            self.prepare_geometry(frame)
        elif frame.Stop == icetray.I3Frame.Calibration:
            self.prepare_calibration(frame)
        elif frame.Stop == icetray.I3Frame.DetectorStatus:
            self.prepare_detector_status(frame)
        return frame
        

#def retrieve_old_i3file(
#    run_id: int, event_id: int output_str: str = ""
#):

def retrieve_i3file(run_id: int, event_id: int, output_str: str = ""):

    live_skymist = i3live.I3Live()
    events_run = live_skymist.events_from_run(run_number=run_id)
    n_ev = len(events_run)
    if n_ev == 0:
        raise RuntimeError(
            f"I3Live has no events for {run_id}. Either the run number is wrong or it predates the inception of the realtime system."
        )
    
    first_evt = events_run[0]["value"]["data"]["event_id"]
    last_evt = events_run[-1]["value"]["data"]["event_id"]
    
    for event in events_run:
        pending_event_id = int(event["value"]["data"]["event_id"])
        #print('pending_event_id: ', pending_event_id)
        #print('event_id: ', event_id)
        #print('Time: ', event["time"])
        if pending_event_id == event_id:
            timestamp = event["time"]
            try:
                start = live_skymist.parse_date(timestamp) - timedelta(seconds=30)
                stop = live_skymist.parse_date(timestamp) + timedelta(seconds=30)
                print('Time between '+str(start)+' and '+str(stop))
            except ValueError as e:
                LOGGER.error(e)
    
    events = live_skymist.get_records(start, stop, with_data=True)
    print('I3Live returned {:d} events.'.format(len(events)))
    for event in events:
        if event["value"]["data"]["event_id"] == event_id:
            # write frames to .i3 file
            i3file = dataio.I3File(cfg.i3files_dir+output_str, 'w')
            gcd_handler = GCD_Handler()
            frames = []
            text_frames = event['value']['data']['frames']
            for frame_type, frame_content in text_frames:
                frame = pickle.loads(zlib.decompress(base64.b64decode(frame_content)),
                                     encoding='bytes')
                print(frame)
                if frame.Stop == icetray.I3Frame.Physics:
                    header = frame["I3EventHeader"]
                frames.append(frame)

                if frame.Stop in [
                    icetray.I3Frame.Geometry,
                    icetray.I3Frame.Calibration,
                    icetray.I3Frame.DetectorStatus,
                ]:
                    print("Bananaaaaaa")
                    frame = gcd_handler.prepare_GCD_from_diff(frame)
                
                elif frame.Stop == icetray.I3Frame.Physics:
                    keys = frame.keys()
                    for key in keys:
                        ## These lines uniformy the OnlineL2 key since it can be written in two different ways
                        if key[:2] == "l2":
                            l2_name = key.split("online_")[-1]
                            newkey = "OnlineL2_" + l2_name
                            print(key, newkey)
                            frame.Put(
                                newkey,
                                frame.Get(key)
                            )
                            frame.Delete(key)
                        ## I3RecoPulseSeriesMapMask can be "SplitUncleanedInIcePulses" or "SplitInIcePulses"
                        ## These lines uniformy the key (needed for truncated energy orig retrieval)
                        if key == "SplitUncleanedInIcePulses":
                            newkey = "SplitInIcePulses"
                            frame.Put(
                                newkey,
                                frame.Get(key)
                            )
                            frame.Delete(key)

            for frame in frames:
                if frame.Stop == icetray.I3Frame.DAQ:
                    frame.Put("I3EventHeader", header)
                    frame.Delete("QI3EventHeader")
                i3file.push(frame)
            i3file.close()
            print('Wrote', cfg.i3files_dir+output_str)
