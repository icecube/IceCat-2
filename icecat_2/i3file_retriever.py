import copy
from datetime import timedelta
import base64
import glob
from pathlib import Path
import pickle
import zlib
import os
import multiprocessing

from icecube import (
    dataio,
    icetray,
    gulliver,
    recclasses,
    dataclasses,
    WaveCalibrator
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


class EventFilter:


    def __init__(self, run_id, event_id, output_str):
        self.run_id = run_id
        self.event_id = event_id
        self.output_path = cfg.i3files_dir + output_str

    def filter_func(
        self,
        input_path,
        function=lambda frame:True,
        filter_streams=[icetray.I3Frame.Physics, icetray.I3Frame.DAQ]
    ):
        #print(f"Input path: (len {len(input_path)}) {input_path}")
        tray = I3Tray()
        if isinstance(input_path, str):
            input_path = [input_path]


        def update(frame):
            #print("Now we reached this stage")
            return


        def delete_unnecessary_keys(frame):
            keys = frame.keys()
            for key in keys:
                if key not in cfg.possible_keys:
                    #print(f"Deleting {key}")
                    frame.Delete(key)


        def select_correct_pulses(frame):
            if frame.Has("SplitInIceDSTPulses"):
                frame.Put(
                    "SplitUncleanedInIcePulses",
                    frame.Get("SplitInIceDSTPulses"),
                    frame.Stop
                )
            if frame.Has("SplitInIceDSTPulsesTimeRange"):
                frame.Put(
                    "SplitUncleanedInIcePulsesTimeRange",
                    frame.Get("SplitInIceDSTPulsesTimeRange"),
                    frame.Stop
                )


        def check_filternames(frame):
            filter_mask = frame["FilterMask"]
            passedfilters = []
            passed_HESE = filter_mask["HESEFilter_15"].condition_passed
            passed_GFU = filter_mask["GFUFilter_17"].condition_passed
            if passed_GFU:
                passedfilters.append("neutrino")
            if passed_HESE:
                passedfilters.append("HESE")
            frame.Put(
                cfg.key_passedfilters,
                dataclasses.I3VectorString(passedfilters)
            )


        tray.Add('I3Reader', Filenamelist=input_path)
        tray.Add(
            function,
            streams=filter_streams
        )
        _raw = 'InIceRawData'
        tray.Add(
            'Delete',
            keys=[
                'CalibratedWaveforms',
                'CalibratedWaveformRange',
                'CalibrationErrata',
                'SaturationWindows'
            ],
            If=lambda f: f.Has(_raw)
        )
        tray.Add(
            select_correct_pulses,
            streams=[
                icetray.I3Frame.Physics,
                icetray.I3Frame.DAQ
            ],
        )
        tray.Add(
            check_filternames,
            streams=[icetray.I3Frame.Physics],
        )
        tray.Add(
            delete_unnecessary_keys,
            streams=[
                icetray.I3Frame.Geometry,
                icetray.I3Frame.Calibration,
                icetray.I3Frame.DetectorStatus,
                icetray.I3Frame.Physics,
                icetray.I3Frame.DAQ
            ],
        )
        tray.Add(
            'I3WaveCalibrator',
            Launches=_raw,
            Waveforms="CalibratedWaveforms",
            If=lambda f: f.Has(_raw)
        )
        tray.Add(
            'I3PMTSaturationFlagger',
            If=lambda f: f.Has(_raw)
        )
        tray.Add(
            'I3Writer',
            'writer',
            filename=self.output_path,
            streams=[
                icetray.I3Frame.Geometry,
                icetray.I3Frame.Calibration,
                icetray.I3Frame.DetectorStatus,
                icetray.I3Frame.Physics,
                icetray.I3Frame.DAQ
            ]
        )
        tray.Execute()
    

    def filter_event(
        self, input_path
    ):


        def is_event(frame):

            run_evt_filter = (
                frame.Has("I3EventHeader") and
                frame['I3EventHeader'].run_id == self.run_id and
                frame['I3EventHeader'].event_id == self.event_id
            )
            daq_filter = frame.Stop == icetray.I3Frame.DAQ
            subevent_filter = (
                frame.Has('SplitInIceDSTPulses') and
                ( 
                    frame['FilterMask']["HESEFilter_15"].condition_passed or
                    frame['FilterMask']["GFUFilter_17"].condition_passed
                )
            )
            
            return (
                run_evt_filter and
                (daq_filter or subevent_filter)
            )

        self.filter_func(input_path, is_event)

    
def retrieve_i3file_pass2(
    run_id, event_id, output_str
):

    event_filter = EventFilter(run_id, event_id, output_str)

    gcd = glob.glob(
        f'{cfg.gcd_folders_l2p2b}Level2pass2b*_Run00{run_id}*_GCD.i3.zst'
    )
    if len(gcd) != 1:
        print(
            "WARN: number of GCD files matched for run "
            f"{run_id} is {len(gcd)} which is not 1.. skipping"
        )
        return
    else:
        print(f'INFO: matched GCD file {gcd} for run {run_id}')

    flist = glob.glob(
        f'{cfg.run_folders_l2p2a}Run00{run_id}/Level2*_data_Run00{run_id}_*[0-9].i3.zst'
    )
    if len(flist) == 0:
        flist = glob.glob(
            f'{cfg.run_folders_l2}Run00{run_id}/Level2*_data_Run00{run_id}_*[0-9].i3.zst'
        )
    print(
        f'INFO: number of files to search for {run_id} {event_id}: {len(flist)}'
    )
    #filter_event(
    #    gcd+flist,
    #    cfg.i3files_dir+output_str,
    #    run_id,
    #    event_id
    #)
    n_processors = 16
    flist_distr = [copy.copy(gcd) for i in range(n_processors)]
    #print(flist_distr)
    max_len = 1
    index_distr = 0
    for f in flist:
        #print(f)
        flist_distr[index_distr].append(f)
        #print(index_distr, len(flist_distr[index_distr]))
        if len(flist_distr[index_distr]) > max_len:
            max_len = len(flist_distr[index_distr])
        index_distr += 1
        if index_distr/n_processors == 1 :
            index_distr = 0
    for index_distr, single_list in enumerate(flist_distr):
        #print(f"Final list number {index_distr}: {single_list}")
        if len(single_list) < max_len:
            flist_distr[index_distr].append(flist[-1])
    pool = multiprocessing.Pool(n_processors)
    pool.map(event_filter.filter_event, flist_distr)

#def retrieve_i3file_pass2_multi(
#    run_id: int, event_id: int, output_str: str = ""
#):

def retrieve_old_i3file(
    run_id: int, event_id: int, output_str: str = ""
):
    is_exception = False
    first_physics_passed = True
    if int(run_id) == cfg.run_exception and int(event_id) == cfg.event_exception:
        alert_path = cfg.old_alerts_path_exception + 'Level2pass2_IC86.2013_data_Run00123986_Subrun00000000_00000212_event77999595.i3.zst'
        is_exception = True
        first_physics_passed = False
    #elif int(run_id) == cfg.run_exception_strange_reco and int(event_id) == cfg.event_exception_strange_reco:
    #    alert_path = cfg.old_alerts_path_exception + 'Level2_IC86.2017_data_Run00130684_Subrun00000000_00000260_event80612787.i3.zst'
    #    is_exception = True
    else:
        old_i3files = glob.glob(cfg.old_alerts_path + "*_scanned1024.i3.zst")
        run_evt_path = f"{cfg.old_alerts_path}Run00{run_id}_event{event_id}_scanned1024.i3.zst"
        run_path = f"{cfg.old_alerts_path}Run00{run_id}_scanned1024.i3.zst"
        if int(run_id) == cfg.run_exception_double_event and int(event_id) == cfg.event_exception_double_event:
            run_path = f"{cfg.old_alerts_path}Run00{run_id}_event2_scanned1024.i3.zst"
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
        '''
        if frame.Stop in [
            icetray.I3Frame.Geometry,
            icetray.I3Frame.Calibration,
            icetray.I3Frame.DetectorStatus,
            icetray.I3Frame.DAQ,
            icetray.I3Frame.Physics
        ] and not found_physics:
        '''
        if not found_physics:
            if frame.Stop == icetray.I3Frame.Stream('p'):
                event_header = frame["I3EventHeader"]
                continue
            if frame.Stop == icetray.I3Frame.Physics:
                if is_exception and not first_physics_passed:
                    first_physics_passed = True
                    continue
                if not is_exception:
                    #frame["I3EventHeader"].sub_event_id = 0
                    frame.Delete("I3EventHeader")
                    frame.Put("I3EventHeader",
                              event_header,
                              frame.Stop)
                elif is_exception:
                    if int(run_id) == cfg.run_exception and int(event_id) == cfg.event_exception: frame["I3EventHeader"].sub_event_id = 1
                filter_mask = frame["FilterMask"]
                filternames = []
                passed_HESE = filter_mask["HESEFilter_15"].condition_passed
                passed_GFU = filter_mask["GFUFilter_17"].condition_passed
                if passed_GFU:
                    filternames.append("neutrino")
                if passed_HESE:
                    filternames.append("HESE")
                frame.Put(
                    cfg.key_passedfilters,
                    dataclasses.I3VectorString(filternames)
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
                    element = frame.Get(key_in_frame)
                    frame.Delete(key_in_frame)
                    frame.Put(
                        key_in_frame,
                        element,
                        frame.Stop
                    )
                    inserted_keys.append(key_in_frame)
            #print(frame)
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
                            #print(key, newkey)
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
                        if key == "SplitInIcePulsesTimeRange":
                            newkey = "SplitUncleanedInIcePulsesTimeRange"
                            frame.Put(
                                newkey,
                                frame.Get(key)
                            )
                            frame.Delete(key)

                    filter_mask = frame["FilterMask"]
                    filternames = []
                    passed_HESE = filter_mask["HESEFilter_15"].condition_passed
                    passed_GFU = filter_mask["GFUFilter_17"].condition_passed
                    if passed_GFU:
                        filternames.append("neutrino")
                    if passed_HESE:
                        filternames.append("HESE")
                    frame.Put(
                        cfg.key_passedfilters,
                        dataclasses.I3VectorString(filternames)
                    )

            for frame in frames:

                keys = frame.keys()
                for key in keys:
                    if key not in cfg.possible_keys:
                        #print(f"Deleting {key}")
                        frame.Delete(key)

                if frame.Stop == icetray.I3Frame.DAQ:
                    frame.Put("I3EventHeader", header)
                    frame.Delete("QI3EventHeader")
                i3file.push(frame)
            i3file.close()
            print('Wrote', cfg.i3files_dir+output_str)
