import json
import socket
import subprocess
from datetime import timedelta
from contextlib import contextmanager


def get_duration(duration :str) -> timedelta:
    """Get call-log duration from string of format mm:ss"""
    duration = duration[-5:].split(':')
    total_time = (int(duration[0]) * 60) + int(duration[1])
    return timedelta(seconds=total_time)

def get_sender(value : str) -> str:
    """Returns the identity of the sender of a message"""
    num = value.replace(' ','').replace('-','')
    try:
        _ = int(num)
    except ValueError:
        return value
    return num[-9:]

def to_sock(sock, data :dict) -> int:
    """Send Dict[data] to Socket[sock]"""
    if not isinstance(sock, socket.socket):
        raise RuntimeError(f'Non-socket destination! {type(sock)}')
    headersize = 128
    data = json.dumps(data)
    header = str(len(data)).ljust(headersize)
    out = header + data
    return sock.send(out.encode('utf8')) == len(out)

def from_sock(sock) -> dict:
    """Receive and unpack Dict[data] from Socket[sock]"""
    if not isinstance(sock, socket.socket):
        raise RuntimeError(f'Non-socket destination! {type(sock)}')
    if not sock:
        return
    headersize = 128
    header = sock.recv(headersize).decode('utf8').strip()
    if not header:
        return
    header = int(header)
    return json.loads(sock.recv(header).decode('utf8'))

@contextmanager
def termux_get(args : str|list) -> subprocess.Popen:
    """returns a subprocess object executing *args"""
    sp = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    yield sp
    sp.terminate()
    sp.wait()
