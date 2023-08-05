from Droid import droid, engine, Android
from Droid.models import Battery, Device
from sqlalchemy.orm import Session

"""
id = Column(Integer, primary_key=True, autoincrement=True)
health = Column(String, nullable=False)
percentage = Column(Integer, nullable=False)
plugged = Column(String, nullable=False)
status = Column(String, nullable=False)
temperature = Column(Float, nullable=False)
current = Column(Integer, nullable=False)
device_id = Column(ForeignKey('Android.id'))
device = relationship('Device', back_populates='battery')
"""

@Android.routine(60)
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
