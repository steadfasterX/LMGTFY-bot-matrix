# tiny-matrix-bot plus

![tiny-matrix-bot icon](tmb-150.png)

This is a simple [Matrix](https://matrix.org) bot based on [matrix-python-sdk](https://github.com/matrix-org/matrix-python-sdk) with no support and no warranty. It was forked from [4nd3r/tiny-matrix-bot](https://github.com/4nd3r/tiny-matrix-bot).

It is easy to understand, little code, and easy to set up and extend to your personal needs. It is meant for small private Matrix homeservers that are run by individuals for their friends. It is not performant and hence not suitable for industrial size roll-out. 

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

## Debugging

Run something similar to
```
systemctl stop tiny-matrix-bot # stop server in case it is running
cd tiny-matrix-bot # go to your installation directory
./tiny-matrix-bot.py --debug # observe debug output
```

## Example bot commands provided

- help: to list available bot commands
- ping: trivial example to have the bot respond
- pong: like ping, but pong
- hello: gives you a friendly compliment
- motd: gives you the Linux Message Of The Day
- ddg: search the web with DuckDuckGo search
- web: surf the web, get a web page (JavaScript not supported)
- rss: read RSS feeds
- twitter: read latest user tweets from Twitter (does not always work as info is scraped from web)
- tesla: chat with your Tesla car (dummy)
- totp: get 2FA Two-factor-authentication TOTP PIN via bot message
- hn: read Hacker News, fetches front page headlines from Hacker News
- mn: read Messari News, fetches the latest news articles from Messari
- date: gives date and time
- btc: gives Bitcoin BTC price info
- eth: gives Ethereum price info
- s2f: print Bitcoin Stock-to-flow price info

## Additional bot commands provided to Matrix or system administrators

With these commands a system administrator can maintain his Matrix installation and keep a watchful eye on his server all through the Matrix bot. Set the permissions accordingly in the config file to avoid unauthorized use of these bot commands!

- disks: see how full your disks or mountpoints are
- cputemp: monitor the CPU temperatures
- restart: restart the bot itself, or Matrix services
- check: check status, health status, updates, etc. of bot, Matrix and the operating system
- update: update operating sytem
- firewall: list the firewall settings and configuration
- date: gives date and time of server
- platform: gives hardware and operating system platform information
- ps: print current CPU, RAM and Disk utilization of server
- top: gives 5 top CPU and RAM consuming processes
- alert: shows if any CPU, RAM, or Disk thresholds have been exceeded (best to combine with a cron job, and have the cron job send the bot message to Matrix admin rooms)

