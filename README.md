# Android Personal Assistant
Android personal assistant that runs on pc/server and syncronizes with device using termux ssh

## `Completed API calls:`
```python
termux.query(['termux-torch', 'off'])
data = termux.query(['termux-audio-info', '-h'])
data = termux.query(['termux-audio-info'])
data = termux.query(['termux-open', 'file.txt'])
data = termux.query(['termux-open', '--send', 'file.txt'])
data = termux.query(['termux-fix-shebang', 'file.txt'])
data = termux.query(['termux-battery-status'])
data = termux.query(['termux-sensor', '-s', 'ACCELEROMETER', '-n', '5'])
data = termux.query(['termux-toast', '-g', 'top', '-b', 'white', '-c', 'black', '"Hello world"'])
data = termux.query(['termux-vibrate', '-f'])
data = termux.query(['termux-sms-list', '-o', '0'])
data = termux.query(['termux-sms-send', '-n', '144', 'bal'])
data = termux.query(['termux-info'])
data = termux.query(['termux-camera-info'])
data = termux.query(['termux-camera-photo', '-c', '1', 'photo.jpg'])
# pair
termux.query(['termux-notification', '-t', '"Test Notification"', '--id', 'one', '-c', '"Hello termux!"', '--action', '"termux\\-toast done"'])
termux.query(['termux-notification-remove', 'one'])
data = termux.query(['termux-wifi-connectioninfo'])
# pair
termux.query(['termux-clipboard-set', 'text'])
data = termux.query(['termux-clipboard-get'])
termux.query(['termux-wake-unlock'])
termux.query(['termux-wake-lock'])
# pair
termux.query(['termux-volume', 'music', '15'])
data = termux.query(['termux-volume'])
data = termux.query(['termux-wallpaper', '-u', 'https://avatars.githubusercontent.com/u/85512138\\?v\\=4'])
termux.query(['termux-brightness', 'auto'])
data = termux.query(['termux-telephony-deviceinfo'])
data = termux.query(['termux-telephony-call', '100'])
data = termux.query(['termux-media-player', 'help'])
data = termux.query(['termux-share', '-h'])
data = termux.query(['termux-contact-list'])
data = termux.query(['termux-location', '-p', 'gps', '-r', 'last'])
data = termux.query(['termux-call-log', '-l', '1'])
data = termux.query(['termux-fingerprint', '-t', '"Authorize?"', '-d', '"Test authorization"'])
data = termux.query(['termux-dialog', 'speech', '-t', '"Speak a command"'])
termux.query(['termux-tts-speak', '-p', '0.9', '-r', '1.0', '"Calling mum in a minute!"'])
# pair
data = termux.query(['termux-microphone-record', '-d', '-f', 'sound.m4a']) # record with defaults
data = termux.query(['termux-microphone-record', '-q']) # stop recording
```

## `Notes`
- Commands starting with `data =` have a valid output on success.
- Some API calls have high latency due to termux implementation.
- Some functionality is only available if termux is running in foreground, such as when using Termux:Float.

## Algorithms
```
"""strategy
input = [5,2,3,7]
sorted = [2,3,5,7]
pick min sleep time = 2
initialize sleep-total = 2

repeat:
	function(sleep-total, sorted)
		do work at (sleeptime total % interval) == 0
		get wait-time to next work = next time - this time
		sleep(wait-time)
		sleeptime total += wait-time
```
