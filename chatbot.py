import os
if(os.path.exists('./config.py')):
    from config import *
else:
    username = os.environ['username']
    client_id = os.environ['client_id']
    token = os.environ['token']
    channel = os.environ['channel']
import sys
import irc.bot
import requests
from collections import deque
from time import time, sleep
import threading

class TwitchBot(irc.bot.SingleServerIRCBot):
    dequesize = 15
    cooldown = 10.0
    messageCooldown = deque(maxlen = dequesize)
    timeZero = 0.0
    allowLoop = True
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
        timeZero = time()
        loopThread = threading.Thread(target = self.start_timer)
        loopThread.start()
        
    def on_pubmsg(self, c, e):
        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            self.do_command(e, cmd)
        return

    def do_command(self, e, cmd):
        c = self.connection
        message = ""
        if cmd == "donate":
            message = "Donate to HelpHopeLive here: https://unofficialkernal.github.io/controllersforcharity/"
        elif cmd == "discord":
            message = "Want to join the CFC community? Join our discord server here: https://discord.gg/atDpjQM"
        elif cmd == "members":
            message = "Get to know our CFC members here: https://unofficialkernal.github.io/controllersforcharity/team.html"
        elif cmd == "total":
            message = "Total so far: TBA"
        elif cmd == "cooldown":
            message = ""
            for i in self.messageCooldown:
                message = message + str(i) + ", "
            message = message[:-2]
        if (cmd == "stoptimer" and self.allowLoop == True):
            self.allowLoop = False
            message = "Stopping Timer..."
        if (cmd == "starttimer" and self.allowLoop == False):
            message = "Starting Timer..."
            self.allowLoop = True
            loopThread = threading.Thread(target = self.start_timer)
            loopThread.start()
        if(message != ""):
            self.send_message(message)
        return
            
    def send_message(self, message):
        c = self.connection
        currentTime = time() - self.timeZero
        if(len(self.messageCooldown) < self.dequesize):
            try:
                c.privmsg(self.channel, message)
                self.messageCooldown.append(currentTime)
            except:
                print("Couldn't send message \"{}\"".format(message))
        else:
            if ((currentTime - self.messageCooldown[0]) >= self.cooldown):
                try:
                    c.privmsg(self.channel, message)
                    self.messageCooldown.append(currentTime)
                except:
                    print("Couldn't send message \"{}\"".format(message))
            else:
                print("Message not sent due to cooldown")
        return
                
    def start_timer(self):
        while(True):
            if(self.allowLoop):
                sleep(15 * 60)
                self.send_message("This message is sent every 15 minutes!")
            else:
                break
        return
            
def main():
    if len(sys.argv) != 1:
        sys.exit(1)
    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()
