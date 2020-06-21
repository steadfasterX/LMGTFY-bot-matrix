#!/bin/bash
#

if [ "${1,,}" == "-h" ] || [ "${1,,}" == "--h" ] || [ "${1,,}" == "-help" ] || [ "${1,,}" == "--help" ]; then
        echo "${0##*/}: Send a text message to a Matrix chat room as user bot."
        echo "${0##*/}: Utility to send text massage as bot via CLI."
        echo "${0##*/}: In this examples script the room Id is hard-coded."
        echo "${0##*/}: usage: ${0##*/} <text msg to send> ... send the provided text"
        echo "${0##*/}: usage: ${0##*/} ... without arguments program will read message from stdin (Ctrl-D to stop reading)"
        exit 1
fi

# Add tiny-matrix-bot.py to your path or provide full path in the next line.
APP="tiny-matrix-bot.py"
# Put a valid bot Matrix room Id into the next line
ROOM='!YourRoomId:yourhomeserver.org'
TEXT=$(echo "$@" | xargs)
if [ "$TEXT" == "" ]; then
        "$APP" --room "$ROOM" # will read from keyboard
        ( [ "$DEBUG" == "1" ] || [ "${DEBUG,,}" == "true" ] ) && echo "${0##*/}: Message from stdin was passed to room \"$ROOM\"."
else
        "$APP" --room "$ROOM" --message "$TEXT" 
        ( [ "$DEBUG" == "1" ] || [ "${DEBUG,,}" == "true" ] ) && echo "${0##*/}: Text message \"$TEXT\" was passed to room \"$ROOM\"."
fi
