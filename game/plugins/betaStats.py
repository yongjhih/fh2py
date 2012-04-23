# -*- coding: iso-8859-15 -*-
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@8:........C@@@
# @@@@@@@@@@@@@@88@@@@@@@@@@@@@@@@@@@@@@88@@@@@@@@@@888@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@O:...........:C@
# @       .@O        O@8         C@@O        o@@@:       cO                   oc       8o   .@@.   @c....:O@@:....:@
# @     .:c8    CO    O8    :o    O8    oO    C@.   :8.   :::.    ..::.     ::Cc    ..:8o    o@:   @o....:8@@:....:@
# @    c@@@O    OO    C8    c@    OO    o8    c@.   :@.   :@@C    O@@@@.   :@@@c    8@@@@@@@@@@@@: @@@@@@@@@O.....:@
# @     ..oO    OO    C8         .@O    o@@@@@@@.   :@.   :@@C    O@@@@.   :@@@c    :C8@@@o O@@ccC @@@@@@@O.......c@
# @       oO    OO    C8         C@O    o.    c8.   :@.   :@@8OOCo8@@@@.   :@@@8@@@@@@O@@@@@@@8C:  @@@@@C.......o@@@
# @    c@@@O    OO    C8    c8    OO    oO    c@.   :@.  o@@@@@@@@@@@@@@@@@@@@@o    8@@@o ..o      @@@C......:C@@@@@
# @    c@@@O    CO    C8    c8    OO    o@.   c@.   :@..o8@@@@@@@@@@@@@@@@Oc@@@c    8@@@o   oo     @C......:O@@@@@@@
# @    c@@@@    ..    88    c8    O@.   .:    c@c    :o@@@@@@@@@@@@@@@@@@@@@@@@Ooc::   Co   o@.    @c....:O@@@@@@@@@
# @    c@@@@@o      o@@8    c@    O@@o    cc  c@@O.  c@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:  Co   o@O    @c....:O8@@@@@@@@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:C@:C:..:C.:.:c.:.@o.............:@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@.:o o.oo o ooCc.oC@c.............:@
# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
#
# betaStats.py -- betatester stats collection
#
#  ©2010 Spit for Forgotten Hope

# httplib is broken.
import bf2, host, bf2.Timer
from game.gameplayPlugin import base
from game.utilities import getCurrentRound
from game.stats import asyncio
import socket, cPickle, time, os, datetime, sys

DEBUG = 0
HOST = ''
PORT = 80
OUTPUT = 'testers-stats.csv'

def path_exists(path):
    # os module is broken. This is ridiculous.
    try:
        f = open(path, 'r')
        f.close()
        return True
    except:
        return False

def csv_reader(file, delimiter, quotechar):
    rows = []
    if len(delimiter) != 1 or len(quotechar) != 1 or type(delimiter) != type('') or type(quotechar) != type(''):
        raise Exception, 'Wrong delimiter or quotechar!'
    for line in file:
        row = line.split('%s%s%s' % (quotechar, delimiter, quotechar))
        row[0] = row[0][1:]
        row[len(row) - 1] = row[len(row) - 1][:-2]
        rows.append(row)
    file.close()
    return rows
        
class csv_writer:
    def __init__(self, file, delimiter, quotechar):
        if len(delimiter) != 1 or len(quotechar) != 1 or type(delimiter) != type('') or type(quotechar) != type(''):
            raise Exception, 'Wrong delimiter or quotechar!'
        self.file = file
        self.delimiter = delimiter
        self.quotechar = quotechar
        
    def writerow(self, row):
        a = self.quotechar + self.delimiter + self.quotechar
        row = a.join(row)
        row = self.quotechar + row + self.quotechar
        self.file.write(row)
        self.file.write('\n')

class betaStats(base):
    def round_start(self, hooker):
        print 'betaStats init\'d'
        # self.a = asyncio.asyncio()
        # self.a.backend_ip = HOST
        # self.a.backend_port = PORT
        
        hooker.register('PlayerConnect', self.onPlayerConnect)
        hooker.register('PlayerDisconnect', self.onPlayerDisconnect)
        
        self.playtime = {}
        self.start_players()
        self.round_start_time = host.timer_getWallTime()
        
    def interval(self):
        try:
            out = self.a.step()
            if out:
                if DEBUG:
                    print 'Backend response:'
                    print out
                return out
        except Exception, e:
            print 'betaStats exception:', e
            return e
    
    def start_players(self):
        for player in bf2.playerManager.getPlayers():
            self.start_time(player)
    
    def start_time(self, player):
        player.betaStats_connectTime = host.timer_getWallTime()
        if DEBUG: print 'Created start time for player %s' % self.get_name(player)
    
    def round_end(self, hooker):
        for player in bf2.playerManager.getPlayers():
            if self.get_name(player) not in self.playtime:
                self.playtime[self.get_name(player)] = (host.timer_getWallTime() - player.betaStats_connectTime)
            else:
                self.playtime[self.get_name(player)] = self.playtime[self.get_name(player)] + (host.timer_getWallTime() - player.betaStats_connectTime)
        if host.timer_getWallTime() - self.round_start_time > 0:
            self.write_data()
            
            # self.send_data()
            # while True:
                # out = self.interval()
                # if out: break
                # time.sleep(0.5)
        else:
            print 'betaStats: Round too short, will not send data to backend'
        
    def write_data(self):
        data = []
        done = []
        if path_exists(OUTPUT):
            reader = csv_reader(open(OUTPUT, 'rb'), delimiter=',', quotechar='"')
            n = 0
            for row in reader:
                n += 1
                if n <= 2: continue # Do not read head
                data.append(row)
        
        writer = csv_writer(open(OUTPUT, 'wb'), delimiter=',', quotechar='"')
        writer.writerow(['Betatester stats file generated:', str(datetime.date.today())])
        writer.writerow(['', ''])
        
        row1len = None
        for player in self.playtime.keys():
            found = 0
            for row in data:
                if row[0] == player:
                    found = 1
                    if row[len(row) - 1] != str(datetime.date.today()):
                        row.append(str(datetime.date.today()))
                    if row1len is None:
                        row1len = len(row)
                    writer.writerow(row)
                    data.remove(row)
                    break
            if not found:
                writer.writerow([player, str(datetime.date.today())])
                if row1len is None:
                    row1len = 2
                
        for row in data:
            for x in range(row1len - len(row)):
                row.append('AWAY')
            writer.writerow(row)
    
    def send_data(self):
        data = cPickle.dumps((self.playtime, getCurrentRound()))
        x = []
        x.append('POST /index/backend HTTP/1.0')
        x.append('host: ' + str(HOST))
        #x.append('Content-type: text/html')
        x.append('Content-Length: ' + str(len(data)))
        x.append('')
        x.append(data)
        x = '\r\n'.join(x)
        if DEBUG:
            print 'Sending:'
            print x
        self.a.set_data(x)
    
    def onPlayerConnect(self, player):
        if DEBUG: print 'Player %s connected' % self.get_name(player)
        self.start_time(player)
        
    def get_name(self, player):
        name = player.getName().split()
        if len(name) == 1:
            return name[0]
        elif len(name) == 2:
            return name[1]
    
    def onPlayerDisconnect(self, player):
        if self.get_name(player) not in self.playtime:
            self.playtime[self.get_name(player)] = (host.timer_getWallTime() - player.betaStats_connectTime)
        else:
            self.playtime[self.get_name(player)] = self.playtime[self.get_name(player)] + (host.timer_getWallTime() - player.betaStats_connectTime)
        if DEBUG: print 'Saved playtime for player %s' % self.get_name(player)
