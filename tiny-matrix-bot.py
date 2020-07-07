#!/usr/bin/env python3

# Don't change tabbing, spacing, or formating as file is automatically linted with autopep8 --aggressive
# Ignore long lines
# pylama:format=pep8:linters=pep8:ignore=E501

import os
import re
import sys
import logging
import traceback
import argparse
import subprocess
import configparser
from time import sleep
from matrix_client.client import MatrixClient


class TinyMatrixtBot():
    """This class implements a tiny Matrix bot.
    It also can be used to send messages from the CLI as proxy for the bot.
    """

    def __init__(self, pargs):
        root_path = os.path.dirname(os.path.realpath(__file__))
        self.config = configparser.ConfigParser()
        if "CONFIG" in os.environ:
            config_path = os.environ["CONFIG"]
        else:
            config_path = os.path.join(root_path, "tiny-matrix-bot.cfg")
        self.config.read(config_path)
        self.base_url = self.config.get("tiny-matrix-bot", "base_url")
        self.token = self.config.get("tiny-matrix-bot", "token")
        self.connect()
        logger.debug("arguments {}".format(pargs))
        logger.debug("client rooms {}".format(self.client.rooms))

        if pargs.room:
            if pargs.room not in self.client.rooms:
                logger.info(
                    "Provided room argument is not in client rooms. Exiting ...")
                sys.exit(1)
            if pargs.message:
                text = pargs.message
                logger.debug("Provided message argument \"{}\".".format(text))
            else:
                text = sys.stdin.read()  # read message from stdin
            logger.debug("sending message to {}".format(pargs.room))
            if pargs.code:
                logger.debug("sending message in format {}".format("code"))
                self.client.rooms[pargs.room].send_html(
                    "<pre><code>" + text + "</code></pre>")
            elif pargs.html:
                logger.debug("sending message in format {}".format("html"))
                self.client.rooms[pargs.room].send_html(text)
            else:
                logger.debug("sending message in format {}".format("text"))
                self.client.rooms[pargs.room].send_text(text)
            logger.debug("message sent, now exiting")
            sys.exit(0)
        run_path = self.config.get(
            "tiny-matrix-bot", "run_path",
            fallback=os.path.join(root_path, "run"))
        os.chdir(run_path)
        scripts_path = self.config.get(
            "tiny-matrix-bot", "scripts_path",
            fallback=os.path.join(root_path, "scripts"))
        enabled_scripts = self.config.get(
            "tiny-matrix-bot", "enabled_scripts", fallback=None)
        self.scripts = self.load_scripts(scripts_path, enabled_scripts)
        self.inviter = self.config.get(
            "tiny-matrix-bot", "inviter", fallback=None)
        self.client.add_invite_listener(self.on_invite)
        self.client.add_leave_listener(self.on_leave)
        for room_id in self.client.rooms:
            self.join_room(room_id)
        self.client.start_listener_thread(
            exception_handler=lambda e: self.connect())
        while True:
            sleep(0.5)

    def connect(self):
        try:
            # downgraded this from info to debug, because if this program is used by other
            # automated scripts for sending messages then this extra output is
            # undesirable
            logger.debug("connecting to {}".format(self.base_url))
            self.client = MatrixClient(self.base_url, token=self.token)
            # same here, downgrade from info to debug, to avoid output for normal use
            # cases in other automated scripts
            logger.debug("connection established")
        except Exception:
            logger.warning(
                "connection to {} failed".format(self.base_url) +
                ", retrying in 5 seconds...")
            sleep(5)
            self.connect()

    def load_scripts(self, path, enabled):
        scripts = []
        for script_name in os.listdir(path):
            script_path = os.path.join(path, script_name)
            if enabled:
                if script_name not in enabled:
                    logger.debug(
                        "script {} is not enabled".format(script_name))
                    continue
            if (not os.access(script_path, os.R_OK) or
                    not os.access(script_path, os.X_OK)):
                logger.debug("script {} is not executable".format(script_name))
                continue
            # the .copy() is extremely important, leaving it out is a major bug
            # as variables from the config file will then be constantly
            # overwritten!
            script_env = os.environ.copy()
            script_env["CONFIG"] = "1"
            logger.debug("script {} with script_env {}".format(
                script_name, script_env))
            script_regex = subprocess.Popen(
                [script_path],
                env=script_env,
                stdout=subprocess.PIPE,
                universal_newlines=True
            ).communicate()[0].strip()
            if not script_regex:
                logger.debug("script {} has no regex".format(script_name))
                continue
            del script_env["CONFIG"]
            if self.config.has_section(script_name):
                for key, value in self.config.items(script_name):
                    script_env["__" + key] = value
                    logger.debug(
                        "add key-value pair key {} to script_env".format(key))
                    logger.debug(
                        "add key-value pair value {} to script_env".format(value))
            script = {
                "name": script_name,
                "path": script_path,
                "regex": script_regex,
                "env": script_env
            }
            scripts.append(script)
            logger.info("script {}".format(script["name"]))
            logger.debug("all scripts {}".format(scripts))
        return scripts

    def on_invite(self, room_id, state):
        sender = "someone"
        for event in state["events"]:
            if event["type"] != "m.room.join_rules":
                continue
            sender = event["sender"]
            break
        logger.info("invited to {} by {}".format(room_id, sender))
        if self.inviter:
            if not re.search(self.inviter, sender):
                logger.info(
                    "{} is not inviter, ignoring invite"
                    .format(sender))
                return
        self.join_room(room_id)

    def join_room(self, room_id):
        logger.info("join {}".format(room_id))
        room = self.client.join_room(room_id)
        room.add_listener(self.on_room_event)

    def on_leave(self, room_id, state):
        sender = "someone"
        for event in state["timeline"]["events"]:
            if not event["membership"]:
                continue
            sender = event["sender"]
        logger.info("kicked from {} by {}".format(room_id, sender))

    def on_room_event(self, room, event):
        if event["sender"] == self.client.user_id:
            logger.debug(
                "event from sender (itself) {}".format(event["sender"]))
            return
        # ignore encrypted messages, but log them in debug mode
        if event["type"] == "m.room.encrypted":
            logger.debug(
                "event type (m.room.encrypted) {}".format(event["type"]))
            logger.debug("sender_key (m.content.sender_key) {}".format(
                event["content"]["sender_key"]))
            logger.debug("ciphertext (m.content.ciphertext) {}".format(
                event["content"]["ciphertext"]))
            return
        if event["type"] != "m.room.message":
            logger.debug(
                "event of type (!=room.message) {}".format(event["type"]))
            return
        # only plain text messages are processed, everything else is ignored
        if event["content"]["msgtype"] != "m.text":
            logger.debug("event of msgtype (!=m.text) {}".format(
                event["content"]["msgtype"]))
            return
        args = event["content"]["body"].strip()
        logger.debug("args {}".format(args))
        for script in self.scripts:
            # multiple scripts can match regex, multiple scripts can be kicked
            # off
            if not re.search(script["regex"], args, re.IGNORECASE):
                continue
            self.run_script(room, event, script, args)

    def run_script(self, room, event, script, args):
        script["env"]["__room_id"] = event["room_id"]
        script["env"]["__sender"] = event["sender"]
        if "__whitelist" in script["env"]:
            if not re.search(script["env"]["__whitelist"],
                             event["room_id"] + event["sender"]):
                logger.debug(
                    "script {} not whitelisted".format(script["name"]))
                return
        if "__blacklist" in script["env"]:
            if re.search(script["env"]["__blacklist"],
                         event["room_id"] + event["sender"]):
                logger.debug("script {} blacklisted".format(script["name"]))
                return
        logger.debug("script {} run with env {}".format(
            [script["name"], args], script["env"]))
        run = subprocess.Popen(
            [script["path"], args],
            env=script["env"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        # output = run.communicate()[0].strip()
        output, std_err = run.communicate()
        output = output.strip()
        std_err = std_err.strip()
        if run.returncode != 0:
            logger.debug("script {} exited with return code {} and " +
                         "stderr as \"{}\" and stdout as \"{}\"".format(
                             script["name"], run.returncode, std_err, output))
            output = "*** Error: script " + script["name"] + " returned error code " + str(
                run.returncode) + ". ***\n" + std_err + "\n" + output
            # return # don't return on error, also print any available output
        sleep(0.1)
        # higher up programs or scripts have two options:
        # Text with a single or a double linebreak (i.e. one empty line) stays together
        # in a single messages, allowing one to write longer messages and structure
        # them clearly with separating whitespace (an empty line).
        # When two empty lines are found, the text is split up in multiple messages.
        # That allows a single call to a script to generate multiple independent messages.
        # In short, everything with 1 or 2 linebreaks stays together, wherever there are 3
        # linebreaks the text is split into 2 or multiple messages.
        for p in output.split("\n\n\n"):
            for line in p.split("\n"):
                logger.debug(
                    "script {} output {}".format(
                        script["name"], line))
            # strip again to get get rid of leading/trailing newlines and whitespaces
            # left over from previous split
            if p.strip() != "":
                if pargs.code:
                    room.send_html("<pre><code>" + p.strip() + "</code></pre>")
                elif ("__format" in script["env"]) and (script["env"]["__format"] == "code"):
                    room.send_html("<pre><code>" + p.strip() + "</code></pre>")
                elif pargs.html:
                    room.send_html(p.strip())
                elif ("__format" in script["env"]) and (script["env"]["__format"] == "html"):
                    room.send_html(p.strip())
                else:
                    room.send_text(p.strip())
                sleep(0.1)


if __name__ == "__main__":
    logging.basicConfig()  # initialize root logger, a must
    if "DEBUG" in os.environ:
        logging.getLogger().setLevel(logging.DEBUG)  # set log level on root logger
    else:
        logging.getLogger().setLevel(logging.INFO)  # set log level on root logger

    # Construct the argument parser
    ap = argparse.ArgumentParser(
        description="This program implements a simple Matrix bot.")
    # Add the arguments to the parser
    ap.add_argument("-d", "--debug", required=False,
                    action="store_true", help="Print debug information")
    ap.add_argument("-r", "--room", required=False,
                    help="Don't run bot. Just send a message to this bot-room. If --message is provided use that as message, if not provided read message from stdin.")
    ap.add_argument("-m", "--message", required=False,
                    help="Don't run bot. Just send this message to the specified bot-room. If not specified, message will be read from stdin.")
    # -h already used for --help, -w for "web"
    ap.add_argument("-w", "--html", required=False,
                    action="store_true", help="Send message(s) as format \"HTML\". If not specified, message will be sent as format \"TEXT\".")
    ap.add_argument("-c", "--code", required=False,
                    action="store_true", help="Send message(s) as format \"CODE\". If not specified, message will be sent as format \"TEXT\". If both --html and --code are specified then --code takes priority.")
    pargs = ap.parse_args()
    if pargs.debug:
        logging.getLogger().setLevel(logging.DEBUG)  # set log level on root logger
        logging.getLogger().info("Debug is turned on.")
    logger = logging.getLogger("tiny-matrix-bot")
    if pargs.message and (not pargs.room):
        logger.error(
            "If you provide a message you must also provide a room as destination for the message.")
        sys.exit(2)

    try:
        TinyMatrixtBot(pargs)
    except Exception:
        traceback.print_exc(file=sys.stdout)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
