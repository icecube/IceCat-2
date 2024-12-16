import sys
sys.path.append("/home/gsommani/newskymist/src/")
from datetime import timedelta

from icecube import dataio
from icecube.realtime_tools import live

from skymist import i3live

topic = "neutrino"

def retrieve_i3file(
    run_id: int, event_id: int, output: str = "",
) -> None:

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
    
    events = live.get_events_data(topic, start, stop)
    print('I3Live returned {:d} events.'.format(len(events)))
    for event in events:
        if event["value"]["data"]["event_id"] == event_id:
            # write frames to .i3 file
            i3file = dataio.I3File(output, 'w')
            frames = event['value']['data']['frames']
            for key, frame in frames.items():
                i3file.push(frame)
            i3file.close()
            print('Wrote', output)
