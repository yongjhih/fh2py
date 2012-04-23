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
# artilleryReload.py -- destroys artillery after 40 seconds from the time it starts firing
#
#  ©2007 Joseph Birr-Pixton aka ctz for Forgotten Hope
import bf2, host, bf2.Timer, random
from game.gameplayPlugin import base
import game.utilities

INTERVAL = 40
DEBUG = 0

axis_artillery = ('commander_artillery_axis', 'commander_mortar_axis', 'commander_smoke_axis')
allied_artillery = ('commander_artillery_allied', 'commander_mortar_allied', 'commander_smoke_allied')

artillery_templates = {1: axis_artillery, 2: allied_artillery}

class artilleryReload(base):
    def __init__(self):
        self.pending = [False, False, False]
    
    def _killarty(self, team):
        self.pending[team] = False
        templates = artillery_templates[team]
        for x in templates:
            if DEBUG: print 'artilleryReload: destroying all objects of template', x
            for object in bf2.objectManager.getObjectsOfTemplate(x):
                if object.hasArmor and object.isPlayerControlObject:
                    if DEBUG: print 'artilleryReload: destroying a', object.templateName
                    try:
                        object.setDamage(0)
                    except:
                        pass
            
    def killarty(self, team):
        if DEBUG: print 'artilleryReload: killarty', team
        try:
            self._killarty(team)
        except Exception, e:
            print 'artilleryReload killarty exception', e
    
    def _killhook(self, weapon, attacker):
        tn = bf2.objectManager.getRootParent(weapon).templateName.lower()
        if attacker is None or not attacker.isValid():
            return
        team = attacker.getTeam()
        if DEBUG: print 'artilleryReload tn', tn
        if tn in axis_artillery or tn in allied_artillery:
            if self.pending[team]: return
            self.pending[team] = True
            self.hooker.later(INTERVAL, self.killarty, team)
            if DEBUG: print 'artilleryReload starting timer for', INTERVAL, 'seconds'
    
    def killhook(self, victim, attacker, weapon, assists, victim_obj):
        try:
            if weapon is None or attacker is None:
                return
            self._killhook(weapon, attacker)
        except Exception, e:
            print 'artilleryReload killhook exception', e
    
    def round_start(self, hooker):
        hooker.register('PlayerKilled', self.killhook)
        if DEBUG: print 'artilleryReload: hooked'
        self.hooker = hooker
        self.pending = [False, False, False]
