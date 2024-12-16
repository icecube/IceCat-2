from icecube import dataio
from icecube.realtime_tools import converter, live

topic = 'neutrino'
start = '2024-02-29 15:48:21'
stop = '2024-02-29 15:48:22'
output = "/home/gsommani/mytrial.i3"

events = live.get_events_data(topic, start, stop)
print('I3Live returned {:d} events.'.format(len(events)))

# write frames to .i3 file
i3file = dataio.I3File(output, 'w')
for event in events:
	frames = event['value']['data']['frames']
	for key, frame in frames.items():
		i3file.push(frame)
i3file.close()
print('Wrote', output)