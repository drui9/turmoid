<img width="96" src="turmoid.png" alt="Turmoid project icon">
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

# Note
This project is in early development stage. Contributions and donation requests are welcome!

