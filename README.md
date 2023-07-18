<p align="center">
    <img width="128" src="turmoid.png" alt="Turmoid project icon">
</p>

```monospace
Food for thought:
You quickly realize you can do anything. That the only limitation to doing everything is time.
So you must choose something instead. To do something, and to do it well.
    - drui9
```

# Android Personal Assistant :: Python
Android personal assistant on termux app

## Dependencies
``` monospace
- Android device, no root
- termux, termux-API
- unix runtime
```

### Details...
- Some functionality is only available if termux is running in foreground.Consider termux-float app extension.
- todo:
```monospace
Triggers:
    - sensors:
        * picked up, put down, shake, flip
    - new message
    - new file created
    - new missed call
    - clipboard copied
    - battery: charger plugged / unplugged
    - bluetooth: connected/disconnected
    - wifi connected/disconnected on/off

Contexts:
    - internet connected/disconnected
    - music playing/stopped
    - location home/away
    - battery low/charged

Actions:
    - message:
        * search, send, new
    - torch:
        * on/off
        * auto on light-sensor & context
    - contacts:
        * list
        * call logs
        * import / export
    - media:
        * camera photo
        * microphone record
        * music play
    - interaction:
        * toast
        * notification
        * fingerprint
        * dialog
        * vibrate
    - tts:
        * speak, voice to text

Integrations:
    - Gmail API - emails
    - Youtube API - Music
    - LLM API - Assistant AI
    - Google speech-recognition
    - Drive API - document storage
```

# snippets
```Python
    # <> session manager
    @contextmanager
    def session(self):
        modpath = self.app.modules['init']['path']
        modules = glob(os.path.join(modpath, '*.py'))
        loader = self.app.modules['init']['loader']
        loader(modules, self.app)
        with self.app.listener(self.notice) as note:
            mods = self.app.modules['loaded']
            for mod in mods:
                md = mods[mod]
                hsh = md['hash']
                nc = f'nc localhost {self.notice}'
                btn1 = ['--button1', 'Start', '--button1-action', f'echo {hsh}-start | {nc}']
                btn2 = ['--button2', 'Stop', '--button2-action', f'echo {hsh}-stop | {nc}']
                btn3 = ['--button3', 'Send', '--button3-action', f'echo $REPLY | {nc}']
                cnt = ['-c', 'Stopped', *btn1, *btn2, *btn3]
                args = ['-t', mod.split('/')[-1], '-i', hsh, '--ongoing', '--alert-once', *cnt]
                self.app.query(['termux-notification', *args])
            yield note
            for mod in mods.values():
                self.app.query(['termux-notification-remove', mod['hash']])
        self.app.shutdown()
    # </>

```

# Note
This project is in early development stage. Contributions and donations are welcome!

