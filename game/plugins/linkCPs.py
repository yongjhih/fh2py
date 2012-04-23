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
# linkCPs.py -- links cps together
#
#  ©2007 Joseph Birr-Pixton aka ctz for Forgotten Hope
import bf2, host, bf2.Timer, random
from game.gameplayPlugin import base
import game.utilities

DEBUG = 0

class linkCPs(base):
    def __init__(self, target, source, invert = 0, never_owned_by = 0, default_zero = 0):
        if type(source) == type(''):
            source = (source,)
        self.target = target.lower()
        self.sources = [k.lower() for k in source]
        self.invert = invert
        self.never_owned_by = never_owned_by
        self.default_zero = default_zero
        if DEBUG: print 'linkCPs: target = %r, sources = %r, invert = %d'%(self.target, self.sources, self.invert)
        
    def round_start(self, hooker):
        hooker.register('ControlPointChangedOwner', self.cpchanged)
    
    def cpchanged(self, cpchanging, top):
        if not top: return
        if cpchanging.templateName.lower() not in self.sources: return
        team = cpchanging.cp_getParam('team')
        if team == -1: return
        if DEBUG: print 'linkCPs: cpchanged', cpchanging.templateName, 'to', team
        
        if DEBUG: print 'linkCPs: cpchanged for source', cpchanging.templateName.lower(), 'in', self.sources
        target = game.utilities.getNamedCP(self.target)
        if target is None:
            if DEBUG: print 'linkCPs:', 'cannot find target cp', self.target
            return
        
        inverter = (-1, 2, 1)
        
        for src in self.sources:
            cp = game.utilities.getNamedCP(src)
            if cp is None:
                if DEBUG: print 'linkCPs:', 'cannot find source cp', src, '-- disregarding'
                continue
            ownerteam = cp.cp_getParam('team')
            if cp.templateName == cpchanging.templateName: continue
            if DEBUG: print 'linkCPs: in set, cp', src, 'belongs to', ownerteam
            if ownerteam != team:
                if DEBUG: print 'linkCPs: set', self.sources, 'not same owner'
                if self.default_zero:
                    if DEBUG: print 'linkCPs: defaulting to zero'
                    game.utilities.cp_setTeam(target, -1, 0)
                return
        
        if self.invert: team = inverter[team]
        if team == self.never_owned_by: team = -1
        if target.cp_getParam('team') != team:
            if DEBUG: print 'linkCPs: setting target', self.target, 'team', team
            game.utilities.cp_setTeam(target, team, 0)
            
    def onCPStatusChange(self, cp, t):
        # It is only an alias
        self.cpchanged(cp, t)
    