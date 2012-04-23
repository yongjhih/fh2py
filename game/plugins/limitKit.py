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
# limitKit.py -- does kit limiting
#
#  ©2006 Joseph Birr-Pixton aka ctz for Forgotten Hope
import bf2, host, bf2.Timer, random, math
from game.gameplayPlugin import base, hookProxy
import game.utilities
import spawnwave

g_daemon = None
HUGE_TTS = 600
DEBUG = 0
round_start_time = None

def defaultspawntime(p):
    if p.isManDown():
        return int(game.utilities.rconExec('sv.manDownTime'))
    else:
        return int(game.utilities.rconExec('sv.spawnTime'))

class limitKitDaemon:
    def __init__(self):
        self.limits = []
        self.hooker = None
    
    def add(self, l):
        self.limits.append(l)
        if not self.hooker.hasHook('RemoteCommand', self.rconhook):
            self.hooker.register('RemoteCommand', self.rconhook)
            self.hooker.register('PlayerSpawn', self.spawnhook)
            self.hooker.register('PlayerDeath', self.deathhook)
            if DEBUG: self.hooker.register('ChatMessage', self.debugchathook)
            if DEBUG: print 'limitKitDaemon: hooked'
        if DEBUG: print 'limitKitDaemon: added limit', l
        
    def remove(self, r):
        if r in self.limits:
            self.limits.remove(r)
        else:
            if DEBUG: print 'limitKitDaemon:', r, 'not found in', self.limits
    
    def debugchathook(self, id, text, channel, flags):
        if text != "kitlimit debug": return
        if id == -1: id = 255
        player = bf2.playerManager.getPlayerByIndex(id)
        if player is None or not player.isValid(): return
        i = 0
        for l in self.limits:
            inuse, nplayers, available = l.inUseAvailable()
            game.utilities.sayAll("debug: limit %d: [kit: %s, nco: %d, where: %d.%d, used %d/%d]"%(i, l.kit, l.nco, l.team, l.slot, inuse, available))
            i += 1
    
    def hack_detected(self, player):
        if player.isAIPlayer(): return
        player.getDefaultVehicle().setDamage(0.01)
        game.utilities.sayAll('Kit error detected for %s. Please reselect your kit!'%player.getName())
    
    def spawnhook(self, player, soldier):
        player.deathtime = 0
        try:
            self._spawnhook(player, soldier)
        except Exception, e:
            print 'spawnhook exception', e
        
    def _spawnhook(self, player, soldier):
        if DEBUG: print 'spawnhook', player
        player.__dict__['fh2_kitlim_last_tts'] = None
        selected = player.__dict__.get('fh2_kitlim_selected', None)
        
        # We'd previously not verify their selection if we didn't know it.
        # Now we're more paranoid; you cannot choose a limited kit unless you
        # have sent the right rcon command previously.
        # if selected is None: return
        self.hooker.later(1, self.spawn_after, player)
        
    def spawn_after(self, player):
        selected = player.__dict__.get('fh2_kitlim_selected', None)
        if selected is None: return
        player_team = player.getTeam()
        
        if DEBUG: print 'player on team', player_team, 'selected', selected
        applicable_limit_by_slot = None
        for limit in self.limits:
            if limit.slot == selected and limit.team == player_team:
                applicable_limit_by_slot = limit
                break
        
        if DEBUG: print 'applicable_limit_by_slot', applicable_limit_by_slot
        
        if applicable_limit_by_slot and applicable_limit_by_slot.nco:
            if player.isSquadLeader() or player.isCommander():
                return
            else:
                self.hack_detected(player)
                return
                
        kit = player.getKit()
        if DEBUG: print 'player has kit', kit
        if kit is None: return
        kit = kit.templateName.lower()
        if DEBUG: print 'player has kit tmpl', kit
        applicable_limit_by_kit = None
        for limits in self.limits:
            if limit.team == player_team and limit.kit == kit:
                applicable_limit_by_kit = limit
                break
                
        if DEBUG: print 'applicable_limit_by_kit', applicable_limit_by_kit
        
        if applicable_limit_by_kit and applicable_limit_by_kit.nco:
            if player.isSquadLeader() or player.isCommander():
                return
            else:
                self.hack_detected(player)
                return
        
        if applicable_limit_by_kit != applicable_limit_by_slot:
            if DEBUG: print 'limit by kit != limit by slot ;', applicable_limit_by_kit, 'vs', applicable_limit_by_slot
            self.hack_detected(player)
    
    def deathhook(self, player, soldier):
        player.deathtime = host.timer_getWallTime()
        
        # Spawntime on death:
        player.stod = game.utilities.getSpawnTime(rstime = round_start_time, dt = player.deathtime)
        if player.stod < spawnwave.minTime():
            player.stod = player.stod + int(game.utilities.rconExec('sv.spawntime'))
            
        selected = player.__dict__.get('fh2_kitlim_selected', None)
        if selected is None: return
        player.deathtime = host.timer_getWallTime()
        self.rconhook(player.index, 'selectkit %d'%selected)
    
    def push_tts(self, player, override = None):
        if override is None:
            override = player.getTimeToSpawn()
        player.__dict__['fh2_kitlim_last_tts'] = override
        if DEBUG: print 'pushed tts', player.__dict__['fh2_kitlim_last_tts']
    
    def pop_tts(self, player, needs_short_time = False):
        last_tts = player.__dict__.get('fh2_kitlim_last_tts', None)
        if DEBUG: print 'popping tts', last_tts
        if last_tts is None and not needs_short_time: return
        
        dst = defaultspawntime(player)
        if 'deathtime' in player.__dict__:
            if DEBUG: print 'deathtime is', player.deathtime
            rst = host.timer_getWallTime() - player.deathtime
            if DEBUG: print 'time since death is', rst
            rst = dst - rst
            if DEBUG: print 'remaining spawn time is', rst
        else:
            rst = dst
        
        if rst < 0:
            rst = 0
        if rst > dst:
            rst = dst
        
        rst += 1
        
        # Changing rst to be compatible with spawnwave system - Spit.
        try:
            if not player.isManDown():
                player.is_first_waiting = False
                if (host.timer_getWallTime() - player.deathtime) < player.stod + spawnwave.waveTime():
                    player.is_first_waiting = True
            
                # Change the spawntime only if HUGE_TTS is applied:
                if player.getTimeToSpawn() > 400 and int(game.utilities.rconExec('sv.spawntime')) > spawnwave.minTime():
                    rst = game.utilities.getSpawnTime(rstime = round_start_time, dt = player.command_time)
                    if not player.is_first_waiting:
                        # Not first waiting
                        if rst < (dst - spawnwave.waveTime()):
                            # Spawnwave does not last
                            player.setTimeToSpawn(rst)
                        else:
                            # Spawnave lasts
                            player.setTimeToSpawn(0)
                    else:
                        # First waiting
                        ovv = player.stod - int(game.utilities.rconExec('sv.spawntime'))
                        if ovv < 0:
                            ovv = 0
                        if rst < spawnwave.minTime() and (host.timer_getWallTime() - player.deathtime) < ovv:
                            # Apply minimum time fix only in proper moment.
                            rst = rst + int(game.utilities.rconExec('sv.spawntime'))
                        if (host.timer_getWallTime() - player.deathtime) >= (player.stod - 2):
                            player.setTimeToSpawn(0)
                        else:
                            player.setTimeToSpawn(rst)
                    
                else:
                    player.setTimeToSpawn(rst)
                
        except Exception, e:
            player.setTimeToSpawn(rst)
                
        bf2.gameLogic.sendHudEvent(player, 58, player.index)
        player.__dict__['fh2_kitlim_last_tts'] = None
    
    def rconhook(self, playeridx, command):
        try:
            self._rconhook(playeridx, command)
        except Exception, e:
            print 'rconhook exception', e
    
    def _rconhook(self, playeridx, command):
        if DEBUG: print 'rcon', repr(playeridx), repr(command)
        if not command.startswith('selectkit'): return
        if playeridx == -1: playeridx = 255
        player = bf2.playerManager.getPlayerByIndex(playeridx)
        player.command_time = host.timer_getWallTime()
        if not player.isValid(): return
        player_team = player.getTeam()
        if ' ' not in command: return
        verb, arg = command.split()
        selected_slot = int(arg)
        
        # switch team handler
        if selected_slot == 99:
            if player.__dict__.get('fh2_kitlim_selected', None) is not None:
                selected_slot = player.__dict__['fh2_kitlim_selected']
            else:
                if DEBUG: print 'resetting slot to 2 because', player.__dict__['fh2_kitlim_selected']
                selected_slot = 2
        
        player.__dict__['fh2_kitlim_selected'] = selected_slot
        
        applicable_limit = None
        for limit in self.limits:
            if limit.slot == selected_slot and limit.team == player_team:
                applicable_limit = limit
                break
        if applicable_limit is None: return self.pop_tts(player, True)
        if DEBUG: print 'limitKit.rconhook: applicable_limit', applicable_limit
        
        if applicable_limit.nco:
            if player.isCommander() or \
               (player.isSquadLeader() and game.utilities.nrInSquad(player.getTeam(), player.getSquadId()) >= 2):
                self.pop_tts(player, True)
            else:
                if player.isAlive():
                    # selected while spawned in
                    bf2.gameLogic.sendHudEvent(player, 57, player.index)
                    self.push_tts(player, HUGE_TTS)
                else:
                    # at spawn time
                    bf2.gameLogic.sendHudEvent(player, 57, player.index)
                    self.push_tts(player)
                    player.setTimeToSpawn(HUGE_TTS)
            return
                
        in_use, nplayers, desired_in_use = applicable_limit.inUseAvailable()
        
        if DEBUG: print 'limitKit.rconhook: desired_in_use', desired_in_use, 'really in_use', in_use
        if desired_in_use < in_use:
            if player.isAlive():
                # selected while spawned in
                bf2.gameLogic.sendHudEvent(player, 57, player.index)
                self.push_tts(player, HUGE_TTS)
            else:
                # at spawn time
                bf2.gameLogic.sendHudEvent(player, 57, player.index)
                self.push_tts(player)
                player.setTimeToSpawn(HUGE_TTS)
        else:
            self.pop_tts(player, True)
    
class limitInfo:
    def __init__(self, team, slot, kit, limit):
        assert team in [1, 2]
        self.team = team
        self.slot = slot
        self.kit = kit.lower()
        self.limit = limit
        self.nco = False
    
    def __repr__(self):
        return '<limitInfo ' + repr(self.__dict__) + '>'
    
    def __str__(self):
        return repr(self)
    
    def inUseAvailable(self):
        in_use = 0
        nplayers = 0
        players = bf2.playerManager.getPlayers()
        for p in players:
            if p.isValid() and p.getTeam() == self.team:
                kit = p.getKit()
                if p.isConnected(): nplayers += 1
                if p.isAlive() and kit is not None:
                    kit = kit.templateName.lower()
                    if kit == self.kit:
                        in_use += 1
        return in_use, nplayers, int(nplayers * self.limit)

class limitKit(base):
    def __init__(self, team, slot, kit, limit):
        # `team' is the team number (1 or 2)
        # `slot' is the _zero_ indexed kit slot
        # `kit' is the template name of the kit
        # `limit' is the number of kits allowed per connected player on the team
        self.info = limitInfo(team, slot, kit, limit)
        
    def round_start(self, hooker):
        global g_daemon
        if bf2.gameLogic.isAIGame(): return
        if g_daemon is None:
            g_daemon = limitKitDaemon()
        g_daemon.hooker = hooker
        g_daemon.add(self.info)
    
    def round_end(self, hooker):
        global g_daemon
        if bf2.gameLogic.isAIGame(): return
        if g_daemon is not None:
            g_daemon.remove(self.info)

class limitKitNCO(base):
    def __init__(self):
        self.info1 = limitInfo(1, 6, '', 0)
        self.info1.nco = True
        self.info2 = limitInfo(2, 6, '', 0)
        self.info2.nco = True
    
    def round_start(self, hooker):
        global g_daemon
        if bf2.gameLogic.isAIGame(): return
        if g_daemon is None:
            g_daemon = limitKitDaemon()
        g_daemon.hooker = hooker
        g_daemon.add(self.info1)
        g_daemon.add(self.info2)
        global round_start_time
        round_start_time = host.timer_getWallTime()
    
    def round_end(self, hooker):
        global g_daemon
        if bf2.gameLogic.isAIGame(): return
        if g_daemon is not None:
            g_daemon.remove(self.info1)
            g_daemon.remove(self.info2)
        
