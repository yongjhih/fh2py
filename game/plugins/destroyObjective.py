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
# destroyObjective.py -- toggles CP ownership when a given number of named templates are destroyed
#
#  ©2007 Joseph Birr-Pixton aka ctz for Forgotten Hope
import bf2, host, bf2.Timer, random
from game.gameplayPlugin import base
import game.utilities, game.scoringCommon

INTERVAL = 20

g_markers = None

class markers:
    def __init__(self):
        self.templates = []
        self.timer = bf2.Timer(self.interval, 1, 1)
        self.timer.setRecurring(INTERVAL)
        
    def add(self, templates):
        # only unique templates
        for t in templates:
            if t not in self.templates:
                self.templates.append(t)
    
    def interval(self, data):
        try:
            for t in self.templates:
                objects = host.omgr_getObjectsOfTemplate(t)
                for obj in objects:
                    if obj.isValid() and game.utilities.reasonableObject(obj) and not obj.getIsWreck():
                        pos = obj.getPosition()
                        game.utilities.createObject('objective_marker', pos)
        except Exception, e:
            print 'destroyObjective interval exception', e

    def stop(self):
        if self.timer is not None:
            self.timer.destroy()
            self.timer = None

class destroyObjective(base):
    def __init__(self, controlpoint, template, refcount):
        self.cp = controlpoint.lower()
        if type('') == type(template):
            self.templates = [template.lower()]
        else:
            self.templates = [t.lower() for t in template]
        self.ref = self.orig_refcount = refcount
        print self.cp, 'will be toggled once', self.ref, self.templates, 'are destroyed'
    
    def round_start(self, hooker):
        self.ref = self.orig_refcount
        hooker.register('VehicleDestroyed', self.destroyedhook)
        
        global g_markers
        if g_markers is None:
            g_markers = markers()
        g_markers.add(self.templates)
        
        # Find ControlPoint Object by name
        cps = bf2.objectManager.getObjectsOfType('dice.hfe.world.ObjectTemplate.ControlPoint')
        for x in cps:
            if x.templateName.lower() == self.cp:
                self.cp_obj = x
    
    def round_end(self, hooker):
        global g_markers
        if g_markers is not None:
            g_markers.stop()
            g_markers = None
    
    def destroyedhook(self, object, attacker):
        if object.templateName.lower() in self.templates:
            self.ref -= 1
            # Give objective points
            if attacker is not None and attacker.isValid():
                if attacker.getTeam() != self.cp_obj.cp_getParam('team'):
                    game.scoringCommon.addScore(attacker, 2, game.scoringCommon.RPL)
                    attacker.stats.destroyedObjectives += 2
                    bf2.gameLogic.sendGameEvent(attacker, 10, 5)
            if self.ref == 0:
                t = self.cp_obj.cp_getParam('team')
                t = [0, 2, 1][t]
                game.utilities.cp_setTeam(self.cp_obj, t)
                        