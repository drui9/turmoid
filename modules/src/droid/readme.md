# Turmoid: Personal Assistant
Technology changes repidly. As of today, we have a linux terminal emulator for android named `termux`, that comes with a ton of features out of the box.
The following modules are available in the emulator, to perform different functions including my favorite: The ability to play disk media using `termux-media-player play song.mp3`.
```monospace
termux-am
termux-am-socket
termux-api-start
termux-api-stop
termux-audio-info
termux-backup
termux-battery-status
termux-brightness
termux-call-log
termux-camera-info
termux-camera-photo
termux-change-repo
termux-clipboard-get
termux-clipboard-set
termux-contact-list
termux-dialog
termux-download
termux-fingerprint
termux-fix-shebang
termux-info
termux-infrared-frequencies
termux-infrared-transmit
termux-job-scheduler
termux-keystore
termux-location
termux-media-player
termux-media-scan
termux-microphone-record
termux-nfc
termux-notification
termux-notification-channel
termux-notification-list
termux-notification-remove
termux-open
termux-open-url
termux-reload-settings
termux-reset
termux-restore
termux-saf-create
termux-saf-dirs
termux-saf-ls
termux-saf-managedir
termux-saf-mkdir
termux-saf-read
termux-saf-rm
termux-saf-stat
termux-saf-write
termux-sensor
termux-setup-package-manager
termux-setup-storage
termux-share
termux-sms-inbox
termux-sms-list
termux-sms-send
termux-speech-to-text
termux-storage-get
termux-telephony-call
termux-telephony-cellinfo
termux-telephony-deviceinfo
termux-toast
termux-torch
termux-tts-engines
termux-tts-speak
termux-usb
termux-vibrate
termux-volume
termux-wake-lock
termux-wake-unlock
termux-wallpaper
termux-wifi-connectioninfo
termux-wifi-enable
termux-wifi-scaninfo
```
- The android personal assistant features:
    * Make it easier to backup messages, callogs, contacts, and disk contents including:
    * Git assistant: git push to my phone IP, sync with github when online
    * Encrypt, backup & stream media i.e (photo, video, music & files) to cloud
    * Text to speech and speech to text using android builtin tts
    * Voice commands including:
        - send messages
        - flashlight on/off
        - play, pause, like e.t.c for media files
        - schedule tasks like alarm, backups, reminders e.t.c
        - Change android lock & homescreen wallpaper using timer, or voice command.
        - Schedule or command phone-calls

The possibilities are endless. I can only hope to cover the best features.

## Installation: difficulty( Easy, apk installation priors )
You need to install termux (fdroid builds as google-play builds are deprecated). Among other things, you need:
- Termux android emulator (fdroid)
- Termux-api (fdroid)
- Run: apt update && apt upgrade on termux, then `apt install termux-api`
- You should be able to call a basic command: `termux-torch on` and have your flashlight turn on after successful installation.

## Project considerations
Termux can run a number of popular programming languages including python, lua, rust, JavaScript on NodeJS, C/C++ using clang, and many more I've not used yet.
With the recent advancements in AI and Language Learning Models (LLM), insane functionality can be added including AI responses that include actions that act on the device.

### Unstable stage
This project is still in it's early development stages. Previous attempt was made using python, and I faced the following challenges:
- Some termux services hanged indefinitely when called inside python processes.

As a result, I'm redoing this attempt using Lua programming language: a light-weight, fast interpreted language I fell in love with.
Hopefully, my love for lua suffices to bring this project to life.
Contributions are welcome.
```monospace
{ for the art of code }
[ author: "drui9" ]
```
