import os
import time

handlers = dict()
stack = list()

def push(index, name, arg, argtype):
    global stack
    if index > len(stack) - 1:
        stack.append(dict())
    # --
    stack[index] |= {
        name: argtype(arg)
    }

def pop():
    global stack
    out = stack[-1]
    stack.remove(out)
    return out

def register(name, **kwargs):
    def wrapper(fn):
        handlers[name] = {'handler': fn}
        handlers[name] |= kwargs
        return fn
    return wrapper

@register(
    'torch',
    args={
        'state': (str, 'required'),
        'timeout': (int, 'optional')
    }
)
def torch(state, timeout=None):
    os.system(f'termux-torch {state}')
    if not timeout:
        return
    #--
    if state == 'on':
        state = 'off'
    else:
        state = 'on'
    time.sleep(timeout)
    os.system(f'termux-torch {state}')

#--
@register(
    'music',
    args={
        'state': (str, 'required'),
        'uri': (str, 'optional')
    }
)
def music(state, uri=None):
    if uri:
        os.system(f'termux-media-player {state} {uri}')
        time.sleep(10)
    else:
        os.system(f'termux-media-player {state}')

# --
if __name__ == '__main__':
    datafile = 'intents.txt'
    if not os.path.exists(datafile):
        os.system(f'touch {datafile}')
    with open(datafile, 'r') as df:
        intents = [i.strip('\n') for i in df.readlines()]
    #--
    for intent in intents:
        intent = intent.split(' ')
        if intent[0] in handlers:
            handle = handlers[intent[0]]
            stack_index = len(stack)
            args = list(handle['args'].keys())
            for index, arg in enumerate(handle['args']):
                index += 1
                if index >= len(intent):
                    if handle['args'][args[index-1]][1] == 'required':
                        raise RuntimeError('Missing argument: {}, required.'.format(args[index-1]))
                    break
                push(stack_index, args[index-1], intent[index], handle['args'][args[index-1]][0])
            #--
            handle['handler'](**pop())

