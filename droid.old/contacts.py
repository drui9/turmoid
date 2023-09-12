import json
from . import droid
from sqlalchemy.orm import Session
from droid.models import Contact, Message, CallLog


@droid.activity(4)
def contacts_update(ctx):
    def get(cmd):
        proc = droid.termux.query(cmd)
        body = list()
        #
        proc.wait()
        procname = cmd
        if isinstance(cmd, list):
            procname = cmd[0]
        #
        droid.logger.debug(f'Process({procname}, status={proc.returncode})')
        while line := proc.stdout.readline():
            body.append(line.strip(b'\n'))
        body = b''.join(body)
        try:
            return json.loads(body.decode('utf8'))
        except json.decoder.JSONDecodeError:
            pass
        return body
    #
    contacts = get('termux-contact-list')
    with Session(bind=droid.engine) as session:
        for contact in contacts:
            if droid.stopped():
                return
            #
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
