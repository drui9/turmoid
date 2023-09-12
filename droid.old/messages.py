import json
from . import droid
from datetime import datetime
from droid.models import Message
from droid.utils import get_sender
from sqlalchemy.orm import Session


@droid.activity(-5)
def unread_count(ctx):
    tts = droid.io.get('text_to_speech')
    with Session(bind=droid.engine) as ses:
        unread = ses.query(Message).filter_by(read=False).count()
        count_str = "messages" if unread > 1 else "message"
        #
        msg = f'You have {unread or "No"} unread {count_str}.'
        droid.logger.info(msg)
        tts['w'].put(msg)

@droid.activity(5, notify=None)
def messages_update(ctx):
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
    # --
    lastmsg = get(['termux-sms-list', '-l', '1'])
    if not lastmsg:
        return
    lastmsg = lastmsg[-1]
    with Session(bind=droid.engine) as session:
        if session.query(Message).get(lastmsg['_id']):
            return # all messages are parsed
        # parse all unsaved
        offset = 0
        limit = 64
        while not droid.events.is_set('terminate'):
            data = get(['termux-sms-list', '-o', str(offset), '-l', str(limit)])
            if not data: # parse complete
                try:
                    session.commit()
                    droid.trigger(ctx['notify'], ctx)
                except Exception as e:
                    droid.logger.exception(e)
                    session.rollback()
                return
            #
            for txt in data:
                if session.query(Message).get(txt['_id']):
                    continue
                # save to database
                msg = Message()
                msg.id = txt['_id']
                msg.type = txt['type']
                msg.read = txt['read']
                msg.time = datetime.fromisoformat(txt['received'])
                msg.body = txt['body']
                msg.sender = get_sender(txt['number'])
                session.add(msg)
            # increment offset
            offset += len(data)
    return
