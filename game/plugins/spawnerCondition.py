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
# spawnerCondition.py -- activates/deactivates ObjectSpawners basing on given CP ownership
#
#  ©2011 Spit for Forgotten Hope

import bf2, host, bf2.Timer, random
from game.gameplayPlugin import base
import game.utilities

DEBUG = 0

class spawnerCondition(base):
    def __init__(self, spawner, team, template, taken = [], not_taken = []):
        self.spawner = spawner
        if type(taken) == type(''):
            self.taken = [game.utilities.getNamedCP(taken)]
        else:
            self.taken = [game.utilities.getNamedCP(x) for x in taken]
        if type(not_taken) == type(''):
            self.not_taken = [game.utilities.getNamedCP(not_taken)]
        else:
            self.not_taken = [game.utilities.getNamedCP(x) for x in not_taken]
        self.team = team
        self.template = template
        
    def round_start(self, hooker):
        hooker.register('ControlPointChangedOwner', self.onCPStatusChange)
        
        self.go()
        
    def onCPStatusChange(self, cp, top):
        if cp not in self.taken and cp not in self.not_taken: return
        self.go()
            
    def go(self):
        if self.check_condition():
            self.set_template(self.template)
        else:
            self.set_template('idontexist')
    
    def check_condition(self):
        for cp in self.taken:
            if int(cp.cp_getParam('team')) != self.team:
                return False
        if self.not_taken:
            n = 0
            for cp in self.not_taken:
                if int(cp.cp_getParam('team')) == self.team:
                    n += 1
            return not len(self.not_taken) == n
        else:
            return True
        
    def set_template(self, template):
        a = game.utilities.rconExec('objecttemplate.activesafe objectspawner %s' % self.spawner)
        b = game.utilities.rconExec('objecttemplate.setobjecttemplate %d %s' % (self.team, template))
        if a:
            print 'spawnerCondition (%s): %s' % (self.spawner, a)
        if b:
            print 'spawnerCondition (%s): %s' % (self.spawner, b)
        if DEBUG: print 'spawnerCondition: set template %s for team %d on spawner %s' % (template, self.team, self.spawner)
