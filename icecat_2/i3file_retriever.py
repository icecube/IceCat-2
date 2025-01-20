from datetime import timedelta
import base64
import glob
from pathlib import Path
import pickle
import zlib
import os

from icecube import (
    dataio,
    icetray,
    gulliver,
    recclasses,
    dataclasses
)
from icecube.icetray import I3Tray
from icecube.frame_object_diff.segments import uncompress

from skymist import i3live

import config

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
        

def retrieve_old_i3file(
    run_id: int, event_id: int, output_str: str = ""
):
    is_exception = False
    if int(run_id) == cfg.run_exception and int(event_id) == cfg.event_exception:
        alert_path = cfg.old_alerts_path_exception + 'Level2pass2_IC86.2013_data_Run00123986_Subrun00000000_00000212_event77999595.i3.zst'
        is_exception = True
        first_physics_passed = False
    else:
        old_i3files = glob.glob(cfg.old_alerts_path + "*_scanned1024.i3.zst")
        run_evt_path = f"{cfg.old_alerts_path}Run00{run_id}_event{event_id}_scanned1024.i3.zst"
        run_path = f"{cfg.old_alerts_path}Run00{run_id}_scanned1024.i3.zst"
        if run_evt_path in old_i3files:
            alert_path = run_evt_path
        elif run_path in old_i3files:
            alert_path = run_path
        else:
            raise ValueError(
                f"Run {run_id} event {event_id} not in {cfg.old_alerts_path}"
            )
    input_i3file = dataio.I3File(alert_path)
    output_i3file = dataio.I3File(cfg.i3files_dir+output_str, 'w')
    found_physics = False
    inserted_keys = []
    for frame in input_i3file:
        if not found_physics: print(frame.Stop)
        if frame.Stop in [
            icetray.I3Frame.Geometry,
            icetray.I3Frame.Calibration,
            icetray.I3Frame.DetectorStatus,
            icetray.I3Frame.DAQ,
            icetray.I3Frame.Physics
        ] and not found_physics:
            if frame.Stop == icetray.I3Frame.Physics:
                if is_exception and not first_physics_passed:
                    first_physics_passed = True
                    continue
                frame["I3EventHeader"].sub_event_id = 0
                filter_mask = frame["FilterMask"]
                streams = []
                passed_HESE = filter_mask["HESEFilter_15"].condition_passed
                passed_GFU = filter_mask["GFUFilter_17"].condition_passed
                if passed_GFU:
                    streams.append("neutrino")
                if passed_HESE:
                    streams.append("HESE")
                frame.Put(
                    "Streams",
                    dataclasses.I3VectorString(streams)
                )
                found_physics = True
            for key_in_frame in frame.keys():
                if key_in_frame.split("/")[0] == "__old__":
                    new_key_in_frame = key_in_frame.split("/")[-1]
                    if new_key_in_frame == "SplitInIceDSTPulses":
                        new_key_in_frame = "SplitUncleanedInIcePulses"
                    if new_key_in_frame == "SplitInIceDSTPulsesTimeRange":
                        new_key_in_frame = "SplitUncleanedInIcePulsesTimeRange"
                    if new_key_in_frame in cfg.possible_keys and not frame.Has(new_key_in_frame):
                        if not new_key_in_frame in inserted_keys:
                            frame.Put(
                                new_key_in_frame,
                                frame.Get(key_in_frame),
                                frame.Stop
                            )
                            inserted_keys.append(new_key_in_frame)
                    frame.Delete(key_in_frame)
                elif key_in_frame not in cfg.possible_keys:
                    frame.Delete(key_in_frame)
                elif key_in_frame not in inserted_keys:
                    if new_key_in_frame == "SplitInIceDSTPulses":
                        new_key_in_frame = "SplitUncleanedInIcePulses"
                    if new_key_in_frame == "SplitInIceDSTPulsesTimeRange":
                        new_key_in_frame = "SplitUncleanedInIcePulsesTimeRange"
                    element = frame.Get(key_in_frame)
                    frame.Delete(key_in_frame)
                    frame.Put(
                        key_in_frame,
                        element,
                        frame.Stop
                    )
                    inserted_keys.append(key_in_frame)
            print(frame)
            output_i3file.push(frame)
    output_i3file.close()
    print('Wrote', cfg.i3files_dir+output_str)


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
            timestamp = event["value"]["data"]["eventtime"].split('+')[0]
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
            streams = event['value']['streams']
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
                        if key == "SplitInIcePulses":
                            newkey = "SplitUncleanedInIcePulses"
                            frame.Put(
                                newkey,
                                frame.Get(key)
                            )
                            frame.Delete(key)

                    frame.Put(
                        "Streams",
                        dataclasses.I3VectorString(streams)
                    )

            for frame in frames:
                if frame.Stop == icetray.I3Frame.DAQ:
                    frame.Put("I3EventHeader", header)
                    frame.Delete("QI3EventHeader")
                i3file.push(frame)
            i3file.close()
            print('Wrote', cfg.i3files_dir+output_str)
