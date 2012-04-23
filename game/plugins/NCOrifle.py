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
# NCOrifle.py -- Support for squadleaders being able to choose between smg and rifle.
#
#  ©2010 Spit for Forgotten Hope

import host, bf2
from game.gameplayPlugin import base
from game.utilities import rconExec, getCurrentRound
from NCOrifleData import NCO_kits

DEBUG = 0

class NCOrifle(base):
    def round_start(self, hooker):
        self.watched_players = []
        self.choices = {}
        self.spawned = []
        self.spawned_dict = {}
        
        if not hooker.hasHook('RemoteCommand', self.onRemoteCommand):
            hooker.register('RemoteCommand', self.onRemoteCommand)
            hooker.register('PlayerSpawn', self.onPlayerSpawn)
            hooker.register('PickupKit', self.onPickupKit)
            if DEBUG: print 'NCOrifle: hooks registered'
        else:
            if DEBUG: print 'NCOrifle: hooks already registered'
        
    def onRemoteCommand(self, playerid, cmd):
        if not (cmd == 'ncosmg' or cmd == 'ncorifle' or cmd.startswith('selectkit')): return
        if playerid == -1: playerid = 255
        player = bf2.playerManager.getPlayerByIndex(playerid)
        if DEBUG: print 'NCOrifle: player %s executed rcon command "%s"' % (player.getName(), cmd)
        
        if cmd.startswith('selectkit'):
            if cmd.endswith('6'):
                self.addPlayer(player)
            else:
                self.removePlayer(player)
                
        if cmd == 'ncorifle':
            self.choices[player] = 'rifle'
            if DEBUG: print 'NCOrifle: player %s has chosen a rifle to spawn with' % player.getName()            
        elif cmd == 'ncosmg':
            self.choices[player] = 'smg'
            if DEBUG: print 'NCOrifle: player %s has chosen an smg to spawn with' % player.getName()
        
    def onPickupKit(self, player, kit):
        if player not in self.spawned: return
        def_kit = self.getData(player)
        if def_kit is None: return
        if DEBUG: print 'Setting NCO kit back to default for team %d' % player.getTeam()
        self.setKit(def_kit, player.getTeam(), self.spawned_dict[player])
        self.spawned.remove(player)
        self.spawned_dict[player] = None
    
    def onPlayerSpawn(self, player, soldier):
        try:
            self._onPlayerSpawn(player, soldier)
        except Exception, e:
            print 'NCOrifle exception', e
            
    def getData(self, player):
        map, gamemode, size = getCurrentRound()
        if map in NCO_kits.keys():
            def_kit1, def_kit2 = NCO_kits[map]
            exec('def_kit = def_kit%d' % player.getTeam())
            return def_kit
        else:
            print 'NCOrifle: Can\'t find NCO kit info for map %s. Update NCOrifleData.py or provide custom map info via mapdata.py' % map
            return None
    
    def _onPlayerSpawn(self, player, soldier):
        if player not in self.watched_players: return
        def_kit = None
        
        def_kit = self.getData(player)
        
        if def_kit is None: return
        
        if player not in self.choices.keys():
            self.setKit(def_kit, player.getTeam(), soldier.templateName)
        elif self.choices[player] == 'smg':
            self.setKit(def_kit, player.getTeam(), soldier.templateName)
        
        elif self.choices[player] == 'rifle':
            if DEBUG: print 'NCOrifle: player %s wants to spawn with a modified NCO kit...' % player.getName()
            kit = def_kit + '_rifle'
            self.setKit(kit, player.getTeam(), soldier.templateName)
        
        if player in self.spawned: return
        self.spawned.append(player)
        self.spawned_dict[player] = soldier.templateName
        
    def setKit(self, kit, team, soldier):
        rconExec('gameLogic.setKit %d 6 "%s" "%s"' % (team, kit, soldier))
        if DEBUG: print 'NCOrifle: Set NCO kit for team %d to %s, %s' % (team, kit, soldier)
    
    def addPlayer(self, player):
        if player not in self.watched_players:
            self.watched_players.append(player)
            if DEBUG: print 'NCOrifle: added player %s to watched players list' % player.getName()
        
    def removePlayer(self, player):
        if player in self.watched_players:
            self.watched_players.remove(player)
            if DEBUG: print 'NCOrifle: removed player %s from watched players list' % player.getName()
