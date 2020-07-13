#!/bin/bash

##############################################################################################
# Global vars, Defaults
##############################################################################################

APP="/home/ubuntu/tiny-matrix-bot/tiny-matrix-bot.py"
ROOMDEFAULT='!IroYDdHfsvWNYRnHtY:ebahia.org'
MESSAGEDEFAULT=""

##############################################################################################
# Argument Parsing
##############################################################################################

# argument parsing:
# see: https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash

# saner programming env: these switches turn some bugs into errors
set -o errexit -o pipefail -o noclobber -o nounset

# allow a command to fail with !’s side effect on errexit
# use return value from ${PIPESTATUS[0]}, because ! hosed $?
# shellcheck disable=SC2251
! getopt --test >/dev/null
if [[ ${PIPESTATUS[0]} -ne 4 ]]; then
	echo "I am sorry, \"getopt --test\" failed in this environment. Either not installed or the wrong version. \"getopt --test\" must return 4. Install package getopt first."
	exit 1
fi

OPTIONS=hdfvwcr:m:
LONGOPTS=help,debug,force,verbose,html,code,room:,message:

function usage() {
	echo "${0##*/}: Send a text message to a Matrix chat room as user bot."
	echo "${0##*/}: usage: ${0##*/} [-h|--help] [-r|--room RoomId] [-w|--html] [-c|--code] [-m|--message] <text msg to send> ... send the provided text to a Matrix chat room"
	echo "${0##*/}: usage: ${0##*/} --message \"<text msg to send>\" ... send the provided argument as text"
	echo "${0##*/}: usage: ${0##*/} <text msg to send> ... send the provided arguments as text"
	echo "${0##*/}: usage: ${0##*/} ... without arguments, without message, program will read message from stdin (Ctrl-D to stop reading)"
	echo "${0##*/}: usage: with --room it will send to the specified room, remember bot must have permissions to send to that room"
	echo "${0##*/}: usage: without --room it will send to default bot room"
	echo "${0##*/}: usage: without --html it will send in default text format"
	echo "${0##*/}: usage: without --code it will send in default text format"
	exit 1
}

# regarding ! and PIPESTATUS see above
# temporarily store output to be able to check for errors
# activate quoting/enhanced mode (e.g. by writing out “--options”)
# pass arguments only via   -- "$@"   to separate them correctly
# shellcheck disable=SC2251
! PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
	# e.g. return value is 1
	#  then getopt has complained about wrong arguments to stdout
	exit 2
fi
# read getopt’s output this way to handle the quoting right:
eval set -- "$PARSED"

h=n d=n DEBUG=0 f=n v=n w=n c=n m=n ROOM=$ROOMDEFAULT MESSAGE="$MESSAGEDEFAULT"
# now enjoy the options in order and nicely split until we see --
while true; do
	case "$1" in
	-h | --help)
		h=y
		shift
		usage
		;;
	-d | --debug)
		d=y
		DEBUG=1
		shift
		;;
	-f | --force)
		f=y
		shift
		;;
	-v | --verbose)
		v=y
		shift
		;;
	-w | --html)
		w=y
		shift
		;;
	-c | --code)
		c=y
		shift
		;;
	-r | --room)
		ROOM="$2"
		shift 2
		;;
	-m | --message)
		m=y
		MESSAGE="$2"
		shift 2
		;;
	--)
		shift
		break
		;;
	*)
		echo "Programming error"
		usage
		exit 3
		;;
	esac
done

# This is not our case, comment it out
# handle non-option arguments
#if [[ $# -ne 1 ]]; then
#    echo "$0: A single input file is required."
#    exit 4
#fi

##############################################################################################
# Logic, Main
##############################################################################################

# handle non-option arguments
if [ "${DEBUG,,}" == "true" ]; then DEBUG="1"; fi
[ "$DEBUG" == "1" ] && echo "${0##*/}: \$# == $#"
if [[ $# -ne 0 ]]; then
	[ "$DEBUG" == "1" ] && echo "${0##*/}: Multiple unlabelled arguments found."
	if [ "$m" == "y" ]; then
		echo "${0##*/}: Use either --message <msg> or message text without --message, but not both!"
		exit 5
	fi
	[ "$DEBUG" == "1" ] && echo "${0##*/}: Multiple unlabelled arguments found which are to be interpreted as message text strings."
	MESSAGE=$(echo "$@" | xargs) # concatenate all text strings together to form the total msg
fi

# h=n d=n f=n v=n w=n c=n ROOM="" MESSAGE=""
[ "$DEBUG" == "1" ] && echo "${0##*/}: help: $h, debug: $d, force: $f, verbose: $v, html: $w, code: $c, room: $ROOM, message: $MESSAGE"

ARGUMENTS=""
if [ "$d" == "y" ]; then ARGUMENTS="$ARGUMENTS --debug"; fi
if [ "$w" == "y" ]; then ARGUMENTS="$ARGUMENTS --html"; fi
if [ "$c" == "y" ]; then ARGUMENTS="$ARGUMENTS --code"; fi

if [ "$MESSAGE" == "" ]; then
	if [ -t 0 ]; then
		# echo "stdin is available"
		# let $APP read the MESSAGE from keyboard/stdin
		# Don't double-quote $ARGUMENTS to avoid empty argument for $APP
		# shellcheck disable=SC2086
		"$APP" $ARGUMENTS --room "$ROOM" # will read from keyboard
		[ "$DEBUG" == "1" ] && echo "${0##*/}: Message from stdin was passed to room \"$ROOM\"."
	else
		# echo "stdin is NOT available"
		MESSAGE=$(cat <&0)
		[ "$DEBUG" == "1" ] && echo "${0##*/}: Something is piped into script: \"$MESSAGE\"."
		if [ "$MESSAGE" == "" ]; then
			[ "$DEBUG" == "1" ] && echo "${0##*/}: No message given, no stdin avaiable, pipe empty, no need to do anything. No message sent to room \"$ROOM\"."
		else
			# Don't double-quote $ARGUMENTS to avoid empty argument for $APP
			# shellcheck disable=SC2086
			"$APP" $ARGUMENTS --room "$ROOM" --message "$MESSAGE"
			[ "$DEBUG" == "1" ] && echo "${0##*/}: Text message \"$MESSAGE\" from pipe was passed to room \"$ROOM\"."
		fi
	fi
else
	# Don't double-quote $ARGUMENTS to avoid empty argument for $APP
	# shellcheck disable=SC2086
	"$APP" $ARGUMENTS --room "$ROOM" --message "$MESSAGE"
	[ "$DEBUG" == "1" ] && echo "${0##*/}: Text message \"$MESSAGE\" from argument was passed to room \"$ROOM\"."
fi

# EOF
