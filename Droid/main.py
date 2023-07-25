import time
import loguru
import threading
from Droid import engine, termux
from sqlalchemy.orm import Session
from Droid.models import Device, Battery
from contextlib import contextmanager


class Android:
	def __init__(self):
		self.logger = loguru.logger
		self.user = None


	@contextmanager
	def authorize(self, session):
		user = termux.query(['whoami'])
		self.logger.info(f'Initializing user: {user}')
		cmd = 'termux-notification -t "Termux:Float" --id "auth" -c'
		msg = 'Keep termux open untill auth completes!'
		termux.query([*cmd.split(' '), f'"{msg}"'])
		device = session.query(Device).filter_by(user=user).first()
		if not device:
			# run authorization
			cmd = 'termux-fingerprint -t "Droid"'
			msg = 'Touch fingerprint sensor to continue.'
			auth = termux.query([*cmd.split(' '), '-d', f'"{msg}"'])
			if auth['auth_result'] != 'AUTH_RESULT_SUCCESS':
				yield
				return
			# update notification
			cmd = 'termux-notification -t "Droid:running" --id "auth" -c'
			msg = 'Close this notification to shut down.'
			termux.query([*cmd.split(' '), f'"{msg}"'])
			# load device info
			device = Device()
			device.user = user
			data = termux.query(['termux-info'])
			device.version = data['Android version']
			device.termux_version = data['TERMUX_VERSION']
			device.manufacturer = data['Manufacturer']
			device.model = data['Model']
			session.add(device)
			session.commit()
			self.logger.info(f'Device [{device.model}:{device.version}] registered.')
		#
		self.logger.info('Acquiring wake-lock')
		termux.query(['termux-wake-lock'])
		yield user
		# cleanup
		self.logger.info('Releasing wake-lock')
		termux.query(['termux-wake-unlock'])
		return

	def start(self):
		with Session(bind=engine) as session:
			with self.authorize(session) as user:
				if not user:
					self.logger.critical('authorization failed!')
					return
				self.user = user
				self.logger.info('Auth success.')
				# todo: launch shutdown watchdog
				time.sleep(10)
				return
