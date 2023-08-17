from json import loads, JSONDecodeError
from Droid.termux import Termux
from Droid import droid
import os

# -- start --
@Termux.arg('-h')
def termux_audio_info(output):
	"""Get information about audio capabilities."""
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Termux.arg('-h --send --view --chooser --content-type *')
def termux_open(output):
	"""Open a file or URL in an external app"""
	return output

@Termux.arg('-h *')
def termux_fix_shebang(output):
	"""Rewrite shebangs in specified files for running under Termux"""
	return output

@Termux.arg('-h')
def termux_battery_status(output):
	"""Get the status of the device battery."""
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output


@Termux.arg('-h -a -c -l -s -n *')
def termux_sensor(output):
	"""Get information about types of sensors as well as live data."""
	raise NotImplementedError()

@Termux.arg('-h -b -c -g -s *')
def termux_toast(output):
	return output

@Termux.arg('on off')
def termux_torch(output):
	return output

@Termux.arg('-h -f -d *')
def termux_vibrate(output):
	return output

@Termux.arg('-h -l -o -t -c -f *')
def termux_sms_list(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Termux.arg('-h -n *')
def termux_sms_send(output):
	return output

@Termux.arg('-h')
def termux_info(output):
	def parse_info(info):
		parsed = dict()
		info = info.split('\n')
		for index, value in enumerate(info):
			if 'TERMUX_VERSION' in value:
				parsed.update({'TERMUX_VERSION': value.split('=')[-1].strip()})
			elif 'upgradable from' in value:
				if not parsed.get('upgrade'):
					parsed.update({'upgrade': list()})
				parsed['upgrade'].append(value)
			elif 'Android version' in value:
				parsed.update({'Android version': info[index + 1]})
			elif 'Device manufacturer:' in value:
				parsed.update({'Manufacturer': info[index + 1]})
			elif 'Device model' in value:
				parsed.update({'Model': info[index + 1]})
		del info
		return parsed
	#
	if not output:
		raise RuntimeError('termux-info got empty response!')
	return parse_info(output)

@Termux.arg('-h')
def termux_camera_info(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Termux.arg('-h -c *')
def termux_camera_photo(output):
	if output:
		return output
	parts = output.split(' ')
	for pt in parts:
		if '.jpg' in pt:
			return os.path.join(droid.termux.cwd, pt)

@Termux.arg('-h --alert-once -c --content --group -i --id --image-path -t --title\
						--vibrate --on-delete --ongoing --priority --action *')
def termux_notification(output):
	return output

@Termux.arg('-h *')
def termux_notification_remove(output):
	return output

@Termux.arg('-h')
def termux_wifi_connectioninfo(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Termux.arg('-h')
def termux_clipboard_get(output):
	return output

@Termux.arg('-h *')
def termux_clipboard_set(output):
	return output

@Termux.arg()
def termux_wake_lock(output):
	return output

@Termux.arg()
def termux_wake_unlock(output):
	return output

@Termux.arg('alarm music notification ring system call *')
def termux_volume(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Termux.arg('-f -u -l *')
def termux_wallpaper(output):
	return output

@Termux.arg('auto *')
def termux_brightness(output):
	return output

@Termux.arg('-h')
def termux_telephony_deviceinfo(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Termux.arg('-h *')
def termux_telephony_call(output):
	return output

@Termux.arg('help info play pause stop')
def termux_media_player(output):
	return output

@Termux.arg('-h -a -c -d *')
def termux_share(output):
	return output

@Termux.arg('-h')
def termux_contact_list(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Termux.arg('-h -p -r *')
def termux_location(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Termux.arg('-h -l -o *')
def termux_call_log(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Termux.arg('-h -t -d -s *')
def termux_fingerprint(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Termux.arg('-h -l -t -v -i -d -r -m -n -p *')
def termux_dialog(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Termux.arg('-h -e -l -n -v -p -r -s *')
def termux_tts_speak(output):
	return output

@Termux.arg('-h -d -f -l -e -b -r -c -i -q *')
def termux_microphone_record(output):
	return output
