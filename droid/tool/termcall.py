from json import loads, JSONDecodeError
from droid import Dru

# -- start --
@Dru.command('-h')
def termux_audio_info(output):
	"""Get information about audio capabilities."""
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Dru.command('-h --send --view --chooser --content-type *')
def termux_open(output):
	"""Open a file or URL in an external app"""
	return output

@Dru.command('-h *')
def termux_fix_shebang(output):
	"""Rewrite shebangs in specified files for running under Dru"""
	return output

@Dru.command('-h')
def termux_battery_status(output):
	"""Get the status of the device battery."""
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Dru.command('-h -b -c -g -s *')
def termux_toast(output):
	return output

@Dru.command('on off')
def termux_torch(output):
	return output

@Dru.command('-h -f -d *')
def termux_vibrate(output):
	return output

@Dru.command('-h -l -o -t -c -f *')
def termux_sms_list(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Dru.command('-h -n *')
def termux_sms_send(output):
	return output

@Dru.command('-h')
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

@Dru.command('-h')
def termux_camera_info(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Dru.command('-h -c *')
def termux_camera_photo(output):
	if output:
		return output
	parts = output.split(' ')
	for pt in parts:
		if '.jpg' in pt:
			return pt

@Dru.command('-h --alert-once -c --content --group -i --id --image-path -t --title\
						--vibrate --on-delete --ongoing --priority --action *')
def termux_notification(output):
	return output

@Dru.command('-h *')
def termux_notification_remove(output):
	return output

@Dru.command('-h')
def termux_wifi_connectioninfo(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Dru.command('-h')
def termux_clipboard_get(output):
	return output

@Dru.command('-h *')
def termux_clipboard_set(output):
	return output

@Dru.command()
def termux_wake_lock(output):
	return output

@Dru.command()
def termux_wake_unlock(output):
	return output

@Dru.command('alarm music notification ring system call *')
def termux_volume(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Dru.command('-f -u -l *')
def termux_wallpaper(output):
	return output

@Dru.command('auto *')
def termux_brightness(output):
	return output

@Dru.command('-h')
def termux_telephony_deviceinfo(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Dru.command('-h *')
def termux_telephony_call(output):
	return output

@Dru.command('help info play pause stop *')
def termux_media_player(output):
	return output

@Dru.command('-h -a -c -d *')
def termux_share(output):
	return output

@Dru.command('-h')
def termux_contact_list(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Dru.command('-h -p -r *')
def termux_location(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Dru.command('-h -l -o *')
def termux_call_log(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Dru.command('-h -t -d -s *')
def termux_fingerprint(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Dru.command('-h -l -t -v -i -d -r -m -n -p *')
def termux_dialog(output):
	try:
		return loads(output)
	except JSONDecodeError:
		pass
	return output

@Dru.command('-h -e -l -n -v -p -r -s *')
def termux_tts_speak(output):
	return output

@Dru.command('-h -d -f -l -e -b -r -c -i -q *')
def termux_microphone_record(output):
	return output

