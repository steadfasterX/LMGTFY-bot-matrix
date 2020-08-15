# tiny-matrix-bot plus

![tiny-matrix-bot icon](tmb-150.png)

This is a simple [Matrix](https://matrix.org) bot based on [matrix-python-sdk](https://github.com/matrix-org/matrix-python-sdk) with no support and no warranty. It was forked from [4nd3r/tiny-matrix-bot](https://github.com/4nd3r/tiny-matrix-bot).

It is easy to understand, little code, and easy to set up and extend to your personal needs. It is meant for small private Matrix homeservers that are run by individuals for their friends. It is not performant and hence not suitable for industrial size roll-out. 

## Future

In mid-July 2020 the project was moved to this new [repository](https://github.com/8go/matrix-eno-bot) and renamed to `matrix-eno-bot`. The reason for this move was that `tiny-matrix-bot plus` is based on [matrix-python-sdk](https://github.com/matrix-org/matrix-python-sdk). Since `matrix-python-sdk` is no longer actively supported and end-to-end-encryption comes out of the box in `matrix-nio`, the switch to the Matrix SDK [matrix-nio](https://github.com/poljar/matrix-nio) and `nio-template` was made. 

#### This bot, i.e. [this repo](https://github.com/8go/tiny-matrix-bot), will *not* be maintained. A maintained bot with similar functionality (but a bit more complexity) will be at [matrix-eno-bot](https://github.com/8go/matrix-eno-bot).

Even though unmaintained the `tiny-matrix bot plus` still is meaningful for beginners as-is. It is smaller and simpler than `matrix-eno-bot`. An easier entry point for people who just want a simple bot. But if end-to-end-encryption is a strict requirement, then head right over to [matrix-eno-bot](https://github.com/8go/matrix-eno-bot).

## Installation and Setup

```
sudo apt install python3 python3-requests
git clone https://github.com/8go/tiny-matrix-bot
git clone https://github.com/matrix-org/matrix-python-sdk
cd tiny-matrix-bot
ln -s ../matrix-python-sdk/matrix_client
cp tiny-matrix-bot.cfg.sample tiny-matrix-bot.cfg
vim tiny-matrix-bot.cfg # adjust the config file, add token, etc.
cp tiny-matrix-bot.service /etc/systemd/system
vim /etc/systemd/system/tiny-matrix-bot.service # adjust service to your setup
systemctl enable tiny-matrix-bot
systemctl start tiny-matrix-bot
systemctl stop tiny-matrix-bot
```

## Usage

- intended audience/users: 
  - small homeserver set up for a few friends
  - tinkerers who want to learn how a bot works
  - people who want to play around with Python code and Matrix
- create a Matrix account for the bot, name it `bot` for example
- configure the bot software
- create the bot service and start the bot or the bot service
- log in to the before created Matrix `bot` account e.g. via Riot web page
- manually send invite from `bot` account to a friend (or to yourself)
- once invite is accepted, reset the bot service (so that the new room will be added to bot service)
  - if you as admin already have a room with the bot, you can reset the bot by sending it `restart bot` as a message in your Matrix bot room
- have the newly joined invitee send a `hello` command to the bot for a first test
- do not encrypt any of the bot rooms, bot does not know how to handle encrypted rooms

## Debugging

Run something similar to
```
systemctl stop tiny-matrix-bot # stop server in case it is running
cd tiny-matrix-bot # go to your installation directory
./tiny-matrix-bot.py --debug # observe debug output
```

## Bot as personal assistent: Example bot commands provided

- help: to list available bot commands
- ping: trivial example to have the bot respond
- pong: like ping, but pong
- hello: gives you a friendly compliment
- motd: gives you the Linux Message Of The Day
- ddg: search the web with DuckDuckGo search
- web: surf the web, get a web page (JavaScript not supported)
- tides: get today's low and high tides of your favorite beach
- weather: get the weather forecast for your favorite city
- rss: read RSS feeds
- twitter: read latest user tweets from Twitter (does not always work as info is scraped from web, lately this web service seems to be down all the time)
- tesla: chat with your Tesla car (dummy)
- totp: get 2FA Two-factor-authentication TOTP PIN via bot message
- hn: read Hacker News, fetches front page headlines from Hacker News
- mn: read Messari News, fetches the latest news articles from Messari
- date: gives date and time
- btc: gives Bitcoin BTC price info
- eth: gives Ethereum price info
- s2f: print Bitcoin Stock-to-flow price info

## Bot as Admin tool: Additional bot commands provided to Matrix or system administrators

With these commands a system administrator can maintain his Matrix installation and keep a watchful eye on his server all through the Matrix bot. Set the permissions accordingly in the config file to avoid unauthorized use of these bot commands!

- disks: see how full your disks or mountpoints are
- cputemp: monitor the CPU temperatures
- restart: restart the bot itself, or Matrix services
- check: check status, health status, updates, etc. of bot, Matrix and the operating system
- update: update operating sytem
- wake: wake up other PCs on the network via wake-on-LAN
- firewall: list the firewall settings and configuration
- date: gives date and time of server
- platform: gives hardware and operating system platform information
- ps: print current CPU, RAM and Disk utilization of server
- top: gives 5 top CPU and RAM consuming processes
- users: list users that are registered on homeserver
- alert: shows if any CPU, RAM, or Disk thresholds have been exceeded (best to combine with a cron job, and have the cron job send the bot message to Matrix admin rooms)

## Other Features

- bot can also be used as an CLI app to send messages to rooms where bot is a member
- when sending messages, 3 message formats are supported:
  - text: by default
  - html: like using `/html ...` in a chat
  - code: for sending code snippets or script outputs, like `/html <pre><code> ... </code></pre>`
- sample scripts are mostly in `bash` and some in `python3`
- it can be used very easily for monitoring the system. An admin can set up a cron job that runs every 15 minutes, e.g. to check CPU temperature, or to check a log file for signs of an intrusion (e.g. SSH or Web Server log files). If anything abnormal is found by the cron job, the cron job fires off a bot message to the admin. 

## Final Thoughts

- Enjoy and have fun with it, it is cool, and easily extensible. Adjust it to your needs!
- Pull Requests for bug fixes are welcome! If you want to make a Pull Requests for enhancements then you better make it on [matrix-eno-bot](https://github.com/8go/matrix-eno-bot).
