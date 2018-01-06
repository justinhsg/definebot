import os
if(os.path.exists('./config.py')):
    from config import *
else:
    username = os.environ['username']
    client_id = os.environ['client_id']
    token = os.environ['token']
import sys
import irc.bot
import requests

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)
        #for personal reference -- list of events: "error","join","kick","mode","part","ping","privmsg","privnotice","pubmsg","pubnotice","quit","invite","pong","action","topic","nick"
    
    def on_welcome(self, c, e):
        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_pubmsg(self, c, e):
        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            self.do_command(e, cmd)
        return

    def do_command(self, e, cmd):
        c = self.connection
        if cmd == "ping":
            message = "pong"            
            c.privmsg(self.channel, message)
        elif cmd == "donate":
            message = "Donate to HelpHopeLive here: https://unofficialkernal.github.io/controllersforcharity/"
            c.privmsg(self.channel, message)
        elif cmd == "discord":
            message = "Want to join the CFC community? Join our discord server here: https://discord.gg/atDpjQM"
            c.privmsg(self.channel,message)
        elif cmd == "members":
            message = "Get to know our CFC members here: https://unofficialkernal.github.io/controllersforcharity/team.html"
            c.privmsg(self.channel,message)
        elif cmd == "total":
            message = "Total so far: TBA"
            c.privmsg(self.channel,message)
def main():
    if len(sys.argv) != 2:
        sys.exit(1)

    channel = sys.argv[1]
    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()
