# Android Personal Assistant :: Python
Android personal assistant that runs on devices that support termux.


## `Dependencies`
``` monospace
- apt install git #`including ssh-key registration` - todo
- apt install ssh #`duplex ssh-key login & "android" defined in ssh-config`
- apt install unzip
- apt install python3
- termux, termux-API
- apt install screen
- unix runtime
```

### `Generating build certificates`
```
Generating self-signed certificates:
1. openssl genrsa -out private.key 4096
2. openssl req -new -key private.key -out signreq.csr
3. openssl x509 -req -days 365 -in signreq.csr -signkey private.key -out certificate.pem
==
(step 2) Notice -> Common Name (e.g. server FQDN or YOUR name) = server_hostname
```

### `Notes`
- Commands starting with `data =` have a valid output on success.
- Some API calls have high latency due to termux implementation.
- Some functionality is only available if termux is running in foreground or running in Termux:Float.

## `Brain storming...`
Start Droid with default home-app. Home-apps can be added in /apps.
