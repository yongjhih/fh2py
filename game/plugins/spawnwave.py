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
# spawnwave.py -- bf42 style spawnwaves
#
#  ©2010 Spit aka python-newbie for Forgotten Hope
import bf2, host, bf2.Timer, random
from game.gameplayPlugin import base
import game.utilities

DEBUG = 0

WAVE_TIME = 7   # Seconds that wave lasts.
MIN_TIME = 10   # Minimum time to spawn.

HUGE_TTS = 600  # That number should be equal to HUGE_TTS in limiKit.py
MAX_TTS = 400   # sv.spawntime has to be < 200

def waveTime(none = None):
    return WAVE_TIME
    
def minTime(none = None):
    return MIN_TIME

class spawnwave(base):
    def __init__(self):
        pass
    
    def onPlayerDisconnect(self, player):
        if player.timer is not None:
            player.timer.destroy()
            player.timer = None
            if DEBUG: print 'Player disconnected, timer destroyed and cleared'
            
    def system_active(self):
        return int(game.utilities.rconExec('sv.spawntime')) > MIN_TIME
    
    def onPlayerConnect(self, player):
        if not self.system_active(): return
        player.timeToSpawn = game.utilities.getSpawnTime(rstime = self.round_start_time, dt = host.timer_getWallTime())
        if player.timeToSpawn:
            if player.timeToSpawn < MIN_TIME:
                player.timeToSpawn = player.timeToSpawn + int(game.utilities.rconExec('sv.spawntime'))
            player.setTimeToSpawn(player.timeToSpawn)
            player.timer = bf2.Timer(self.interval, player.timeToSpawn + WAVE_TIME, 1, player)
            player.timer.setRecurring(int(game.utilities.rconExec('sv.spawntime')))
    
    def interval(self, player):
        if player.getTimeToSpawn() < MAX_TTS: # Make sure we don't override HUGE_TTS when unavailable kit is selceted.
            if WAVE_TIME < int(game.utilities.rconExec('sv.spawntime')):
                player.timeToSpawn = game.utilities.getSpawnTime(rstime = self.round_start_time, dt = host.timer_getWallTime())
            else:
                player.timeToSpawn = 0
            player.setTimeToSpawn(player.timeToSpawn)
        else:
            player.setTimeToSpawn(HUGE_TTS)
    
    def onPlayerSpawn(self, player, soldier):
        if player.timer is not None:
            player.timer.destroy()
            player.timer = None
            if DEBUG: print 'Player spawned, timer destroyed and cleared'
        player.timeToSpawn = None
    
    def onPlayerDeath(self, player, soldier):
        try:
            if not player.isAlive() and self.system_active():    # A bit paranoid, but its better to be sure.
                player.timer = None
                player.timeOfDeath = host.timer_getWallTime()
                if DEBUG: print 'Time of death:', player.timeOfDeath
                player.timeToSpawn = game.utilities.getSpawnTime(rstime = self.round_start_time, dt = player.timeOfDeath)
                if player.timeToSpawn:
                    if player.getTimeToSpawn() < MAX_TTS: # Make sure we don't override HUGE_TTS when unavailable kit is selceted.
                        if player.timeToSpawn < MIN_TIME:
                            player.timeToSpawn = player.timeToSpawn + int(game.utilities.rconExec('sv.spawntime'))
                        player.setTimeToSpawn(player.timeToSpawn)
                    player.timer = bf2.Timer(self.interval, player.timeToSpawn + WAVE_TIME, 1, player)
                    player.timer.setRecurring(int(game.utilities.rconExec('sv.spawntime')))
        except Exception, e:
            print 'onPlayerDeath exception', e
    
    def round_start(self, hooker):
        try:
            host.registerHandler('PlayerDeath', self.onPlayerDeath)
            host.registerHandler('PlayerSpawn', self.onPlayerSpawn)
            host.registerHandler('PlayerConnect', self.onPlayerConnect)
            host.registerHandler('PlayerDisconnect', self.onPlayerDisconnect)
            if DEBUG: print 'Spawnwave hooked'
            
            self.round_start_time = host.timer_getWallTime()
            if DEBUG: print 'Spawnwave round_start time is', self.round_start_time
        except Exception, e:
            print 'round_start exception', e
        
    def round_end(self, hooker):
        try:
            self.round_start_time = None
        except Exception, e:
            print 'round_end exception', e