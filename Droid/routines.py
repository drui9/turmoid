import os
import ssl
import json
import zipfile
from hashlib import md5
from datetime import datetime
from Droid import droid, engine
from sqlalchemy.orm import Session
from socket import socket, AF_INET, SOCK_STREAM
from Droid.utilfuncs import get_duration, get_sender
from Droid.models import Battery, Device, Contact, Message, CallLog

#
@droid.routine(-1)
def parse_call_log():
	ok, data = droid.termux.query(['termux-call-log', '-l', '1'])
	if not ok:
		raise data # data == error
	lastcall = data[-1]
	with Session(bind=engine) as session:
		if session.query(CallLog).get(datetime.fromisoformat(lastcall['date'])):
			return # all messages are parsed
		# parse all unsaved
		droid.logger.info('Loading contacts.')
		offset = 0
		while droid.active.is_set():
			ok, data = droid.termux.query(['termux-call-log', '-o', str(offset)])
			if not ok:
				raise data
			elif not data:
				break
			#
			done = False
			for log in data:
				date = datetime.fromisoformat(log['date'])
				if session.query(CallLog).get(date):
					done = True
					break
				# save to database
				call = CallLog()
				call.id = date
				call.type = log['type']
				call.number = log['phone_number']
				call.duration = get_duration(log['duration'])
				session.add(call)
			if done:
				break
		if not droid.active.is_set():
			return
		try:
			session.commit()
		except Exception as e:
			droid.logger.exception(e)
			session.rollback()
			raise

@droid.routine(-1)
def parse_messages():
	ok, data = droid.termux.query(['termux-sms-list', '-l', '1'])
	if not ok:
		raise data # data == error
	lastmsg = data[-1]
	with Session(bind=engine) as session:
		if session.query(Message).get(lastmsg['_id']):
			return # all messages are parsed
		# parse all unsaved
		droid.logger.info('Loading new messages...')
		offset = 0
		while droid.active.is_set():
			ok, data = droid.termux.query(['termux-sms-list', '-o', str(offset)])
			if not ok:
				raise data
			elif not data: # parse complete
				break
			#
			done = False
			for txt in data:
				if session.query(Message).get(txt['_id']):
					done = True
					break
				# save to database
				msg = Message()
				msg.id = txt['_id']
				msg.type = txt['type']
				msg.read = txt['read']
				msg.time = datetime.fromisoformat(txt['received'])
				msg.body = txt['body']
				msg.sender = get_sender(txt['number'])
				session.add(msg)
			if done:
				break
			# increment offset
			offset += len(data)
		if not droid.active.is_set():
			return
		try:
			session.commit()
		except Exception as e:
			droid.logger.exception(e)
			session.rollback()
			raise

@droid.routine(-1)
def parse_contacts():
	contacts = droid.get('termux-contact-list')
	with Session(bind=engine) as session:
		for contact in contacts:
			num = contact['number'].replace(' ','').replace('-','')
			name = contact['name'].strip()
			#
			cont = session.query(Contact).get(int(num))
			if not cont:
				cont = Contact()
				cont.id = int(num)
				cont.name = name
				cont.number = num
			#
			sender = num[-9:]
			txts = session.query(Message).filter_by(sender=sender).all()
			for msg in txts:
				msg.contact = cont
			#
			logs = session.query(CallLog).filter_by(number=num).all()
			for log in logs:
				log.contact = cont
			session.add(cont)
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
			raise RuntimeError(404)
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
	while not droid.terminate.is_set():
		if droid.need_fore.wait(timeout=10):
			callid = str(datetime.utcnow().timestamp())
			ok, err = droid.termux.query(['termux-clipboard-set', callid])
			if not ok:
				droid.logger.critical(f'Set clipboard failed! {str(err)}')
				continue
			data = droid.get('termux-clipboard-get')
			if data == callid:
				droid.foreground.set()
				droid.need_fore.clear()
			else: # todo: request foreground through notification
				droid.foreground.clear()
				msg = 'Termux foreground request.'
				params = ['-g', 'top', '-b', 'white', '-c', 'black']
				droid.termux.query(['termux-toast', *params,  f'"{msg}"'])
	# exit notice
	droid.logger.info('Foreground manager exited.')

@droid.routine(0)
def update_manager():
	TLS_PORT = 9090
	sock = socket(AF_INET, SOCK_STREAM)
	try:
		sock.bind(('0.0.0.0', TLS_PORT))
	except OSError as e: # could not bind addr
		droid.logger.critical(str(e))
		return droid.terminate.set()
	sock.listen(1)
	#
	ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
	ssl_ctx.load_cert_chain('droid/crypt/certificate.pem', keyfile='droid/crypt/private.key')  # noqa: E501
	ssock = ssl_ctx.wrap_socket(sock, server_side=True)
	ssock.settimeout(5)
	#
	while not droid.terminate.is_set():
		try:
			conn, addr = ssock.accept()
			conn.settimeout(10)
		except TimeoutError:
			continue
		# get files
		with zipfile.ZipFile('droid/droid.zip') as zf:
			files = zf.namelist()
		out = dict()
		basedir = 'droid'
		for file in files:
			fpath = os.path.join(basedir, file)
			with open(fpath, 'rb') as ffile:
				out.update({file: md5(ffile.read()).hexdigest()})
		#
		try:
			# send diff
			conn.send(json.dumps(out).encode('utf8'))
			# todo: accept update zipfile
			while True:
				try:
					true_diff = conn.recv()
					if not true_diff:
						break
					#
					try:
						true_diff = json.loads(true_diff.decode('utf8'))
						droid.logger.debug(true_diff)
						# todo: sync with true_diff
						conn.send(json.dumps({'ok': True}).encode('utf8'))
					except Exception as e:
						droid.logger.info(f'Update failed: {e}')
						break
					# receive update zipfile
					break
				except TimeoutError:
					continue
			# close
			conn.close()
		except Exception as e:
			droid.logger.critical(e)
	droid.logger.info('Update manager exited.')

@droid.routine(-1)
def text_to_speech(**kwargs):
	pass
