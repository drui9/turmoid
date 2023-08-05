from Droid import droid, engine
from sqlalchemy.orm import Session
from Droid.models import Battery, Device, Contact
"""
"""
@droid.routine(120)
def parse_messages():
	texts = droid.get('termux-sms-list')
	droid.logger.critical(len(texts))

@droid.routine(-1)
def parse_contacts():
	contacts = droid.get('termux-contact-list')
	with Session(bind=engine) as session:
		for contact in contacts:
			num = contact['number'].replace(' ','').replace('-','')
			name = contact['name'].strip()
			#
			cont = Contact()
			cont.id = num[-8:]
			cont.name = name
			cont.number = num
			if not session.query(Contact).get(cont.id):
				session.add(cont)
				# todo: organize call logs and sms with contact = 'unknown'
		try:
			session.commit()
		except Exception as e:
			droid.logger.exception(e)
			session.rollback()
			raise

@droid.routine(-1)
def check_battery():
	battinfo = droid.get('termux-battery-status')
	droid.logger.debug('Checking battery status.')
	with Session(bind=engine) as session:
		device = session.query(Device).filter_by(user=droid.user).first()
		if not device:
			raise RuntimeError('No device found!')
		batt = session.query(Battery).filter_by(device=device).first()
		if not batt:
			batt = Battery()
		batt.health = battinfo['health']
		batt.percentage = battinfo['percentage']
		batt.plugged = battinfo['plugged']
		batt.status = battinfo['status']
		batt.temperature = battinfo['temperature']
		batt.current = battinfo['current']
		batt.device = device
		try:
			session.add(batt)
			session.commit()
			droid.logger.debug(batt)
		except Exception as e:
			session.rollback()
			droid.logger.exception(e)
			raise e

@droid.routine(0)
def termux_foreground():
	while droid.termux.ready():
		if droid.need_fore.wait(timeout=10):
			callid = str(hash(droid))
			ok, err = droid.termux.query(['termux-clipboard-set', callid])
			if not ok:
				droid.logger.critical(f'Set clipboard failed! {str(err)}')
				continue
			data = droid.get('termux-clipboard-get')
			if data == callid:
				droid.foreground.set()
				droid.need_fore.clear()
			else:
				msg = 'Please open termux!'
				params = ['-g', 'top', '-b', 'white', '-c', 'black']
				droid.termux.query(['termux-toast', *params,  f'"{msg}"'])
