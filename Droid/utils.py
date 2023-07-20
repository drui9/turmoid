from contextlib import contextmanager
from Droid.termux import Termux
from Droid import termux
import json
import os

# -- start --
@Termux.arg('-h')
def termux_audio_info(cmd :str):
	"""Get information about audio capabilities."""
	if '-h' in cmd:
		return termux.execute(cmd)
	return json.loads(termux.execute(cmd))

@Termux.arg('-h --send --view --chooser --content-type *')
def termux_open(cmd :str):
	"""Open a file or URL in an external app"""
	return termux.execute(cmd)

@Termux.arg('-h *')
def termux_fix_shebang(cmd :str):
	"""Rewrite shebangs in specified files for running under Termux"""
	return termux.execute(cmd)

@Termux.arg('-h')
def termux_battery_status(cmd :str):
	"""Get the status of the device battery."""
	if '-h' in cmd:
		return termux.execute(cmd)
	return json.loads(termux.execute(cmd))


@Termux.arg('-h -a -c -l -s -n *')
def termux_sensor(cmd :str):
	"""Get the status of the device battery."""
	if '-h' in cmd or '-c' in cmd:
		return termux.execute(cmd)
	@contextmanager
	def resource_guard():
		yield
		termux.execute('termux-sensor -c')
	if '-n' in cmd:
		try:
			out = list()
			part = int(cmd.split('-n')[-1].strip().split(' ')[0])
			with resource_guard():
				for _ in range(part):
					resp = termux.execute(cmd.replace(str(part), str(1)))
					out.append(json.loads(resp))
			return out
		except Exception as e:
			return str(e)
	return json.loads(termux.execute(cmd))

@Termux.arg('-h -b -c -g -s *')
def termux_toast(cmd :str):
	return termux.execute(cmd)

@Termux.arg('on off')
def termux_torch(cmd :str):
	return termux.execute(cmd)

@Termux.arg('-h -f -d *')
def termux_vibrate(cmd :str):
	return termux.execute(cmd)

@Termux.arg('-h -l -o -t -c -f *')
def termux_sms_list(cmd :str):
	if '-h' in cmd:
		return termux.execute(cmd)
	return json.loads(termux.execute(cmd))

@Termux.arg('-h -n *')
def termux_sms_send(cmd :str):
	return termux.execute(cmd)

@Termux.arg('-h')
def termux_info(cmd :str):
	return termux.execute(cmd)

@Termux.arg('-h')
def termux_camera_info(cmd :str):
	if '-h' in cmd:
		return termux.execute(cmd)
	return json.loads(termux.execute(cmd))

@Termux.arg('-h -c *')
def termux_camera_photo(cmd :str):
	if '-h' in cmd:
		return termux.execute(cmd)
	parts = cmd.split(' ')
	for pt in parts:
		if '.jpg' in pt:
			termux.execute(cmd)
			return os.path.join(termux.cwd, pt)

@Termux.arg('-h --alert-once -c --content --group -i --id --image-path -t --title --vibrate --on-delete --ongoing --priority --action *')
def termux_notification(cmd :str):
	cmd = cmd.replace('\\-', '-')
	return termux.execute(cmd)

@Termux.arg('-h *')
def termux_notification_remove(cmd :str):
	return termux.execute(cmd)

@Termux.arg('-h')
def termux_wifi_connectioninfo(cmd :str):
	if '-h' in cmd:
		return termux.execute(cmd)
	return json.loads(termux.execute(cmd))

@Termux.arg('-h')
def termux_clipboard_get(cmd :str):
	return termux.execute(cmd)

@Termux.arg('-h *')
def termux_clipboard_set(cmd :str):
	return termux.execute(cmd)

@Termux.arg()
def termux_wake_lock(cmd :str):
	return termux.execute(cmd)

@Termux.arg('on off')
def termux_torch(cmd :str):
	return termux.execute(cmd)

@Termux.arg()
def termux_wake_unlock(cmd :str):
	return termux.execute(cmd)

@Termux.arg('alarm music notification ring system call *')
def termux_volume(cmd :str):
	if len(cmd.split(' ')) != 1:
		return termux.execute(cmd)
	return json.loads(termux.execute(cmd))

@Termux.arg('-f -u -l *')
def termux_wallpaper(cmd :str):
	return termux.execute(cmd)

@Termux.arg('auto *')
def termux_brightness(cmd :str):
	return termux.execute(cmd)

@Termux.arg('-h')
def termux_telephony_deviceinfo(cmd :str):
	if '-h' in cmd:
		return termux.execute(cmd)
	return json.loads(termux.execute(cmd))

@Termux.arg('-h *')
def termux_telephony_call(cmd :str):
	return termux.execute(cmd)

@Termux.arg('help info play pause stop')
def termux_media_player(cmd :str):
	return termux.execute(cmd)

@Termux.arg('-h -a -c -d -t *')
def termux_share(cmd :str):
	return termux.execute(cmd)

@Termux.arg('-h')
def termux_contact_list(cmd :str):
	return json.loads(termux.execute(cmd))

@Termux.arg('-h -p -r *')
def termux_location(cmd :str):
	if '-h' in cmd:
		return termux.execute(cmd)
	return json.loads(termux.execute(cmd))

@Termux.arg('-h -l -o *')
def termux_call_log(cmd :str):
	if '-h' in cmd:
		return termux.execute(cmd)
	return json.loads(termux.execute(cmd))

@Termux.arg('-h -t -d -s *')
def termux_fingerprint(cmd :str):
	if '-h' in cmd:
		return termux.execute(cmd)
	return json.loads(termux.execute(cmd))

@Termux.arg('-h -l -t *')
def termux_dialog(cmd :str):
	if '-h' in cmd or '-l' in cmd:
		return termux.execute(cmd)
	return json.loads(termux.execute(cmd))

@Termux.arg('-h -e -l -n -v -p -r -s *')
def termux_tts_speak(cmd :str):
	return termux.execute(cmd)

@Termux.arg('-h -d -f -l -e -b -r -c -i -q *')
def termux_microphone_record(cmd :str):
	return termux.execute(cmd)
