# PSMB
Since the SMB1 protocol is now deprecated (for security reasons), there's some annoying setting up to be done every time you want to start an SMB server for use with PS2 OPL if you want to keep your server computer safe. This script aims to automate the process as much as possible.

(this script only works on Linux using NetworkManager and requires and already functioning SMB server setup.)

## How it works:
For my setup, I'm using a separate LAN with no access to the internet solely for the SMB sharing with the PS2. This script is intended for a similar use case.

In general terms, this script:
1. Disconnects you from the internet and connects you to the PS2's LAN
2. Checks if everything is set up properly
3. Starts the SMB server
4. (When disconnecting) puts everything to the way it was before starting the SMB server

---

Made this for myself but thought I might as well leave it public in case it helps someone.

Don't expect updates
