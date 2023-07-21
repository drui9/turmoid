import loguru
import threading
from Droid import engine, termux
from sqlalchemy.orm import Session
from Droid.models import Device, Battery
from contextlib import contextmanager
from Droid.text import tts_data


class Android:
	def __init__(self):
		self.session = Session(bind=engine)
		self.logger = loguru.logger
		self.device = None

	def update_android_data(self):
		# load battery info
		battery = Battery()
		batt_info = termux.query(['termux-battery-status'])
		battery.health = batt_info['health']
		battery.percentage = batt_info['percentage']
		battery.plugged = batt_info['plugged']
		battery.status = batt_info['status']
		battery.temperature = batt_info['temperature']
		battery.current = batt_info['current']
		self.device.battery = battery
		self.session.add(battery)
		self.session.commit()

	@contextmanager
	def authorize(self):
		user = termux.query(['whoami'])
		devices = self.session.query(Device).filter_by(user=user).all()
		if not devices:
			# load device info
			device = Device()
			device.user = user
			data = termux.query(['termux-info'])
			device.version = data['Android version']
			device.termux_version = data['TERMUX_VERSION']
			device.manufacturer = data['Manufacturer']
			device.model = data['Model']
			self.session.add(device)
			self.session.commit()
		elif len(devices) > 1:
			prompt = list()
			for dev in devices:
				prompt.append(str(dev))
			choice = termux.query(['termux-dialog', 'radio', '-t', '"Choose an Android session"', '-v', f'"{",".join(prompt)}"'.replace(',', '\\,')])['index']
			device = devices[choice]
		else:
			device = devices[0]
		# prepare user interaction
		if not device.set_admin:
			termux.query(['termux-tts-speak', '-p', '0.9', '-r', '1.0', f'"{tts_data[2]}"'])
			nickname = termux.query(['termux-dialog', 'speech', '-t', '"Nickname please?"'])
			if nickname['code'] != 0 or not (nametext := nickname['text']):
				termux.query(['termux-tts-speak', '-p', '0.9', '-r', '1.0', f'"{tts_data[4]}"'])
			else:
				device.admin = nametext
				name_confirm = tts_data[3].format(device.admin)
				termux.query(['termux-tts-speak', '-p', '0.9', '-r', '1.0', f'"{name_confirm}"'])
			device.set_admin = True
			self.session.add(device)
			self.session.commit()
		# set device for use in other methods
		self.device = device
		#
		updater = threading.Thread(target=self.update_android_data)
		updater.name = 'Android:watch'
		updater.daemon = True
		updater.start()
		yield
		return

	def start(self):
		termux.query(['termux-tts-speak', '-p', '0.9', '-r', '1.0', f'"{tts_data[1]}"'])
		with self.authorize():
			return
