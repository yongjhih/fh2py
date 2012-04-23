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
# randomiseSpawner.py -- randomises what spawners actually spawn, with some limitations
#  ©2006 Joseph Birr-Pixton aka ctz for Forgotten Hope
import bf2, host, bf2.Timer
import sys, random
from game.gameplayPlugin import base
import game.utilities

TIMER_INTERVAL = 120
g_timer = None
g_instances = []

def interval(userdata):
    global g_instances
    for g in g_instances:
        g.interval(userdata)

class randomiseSpawner(base):
    def __init__(self, spawner = None, team1 = None, team2 = None):
        self.spawner = spawner.lower()
        self.alternates_team1 = team1
        self.alternates_team2 = team2
        self.active = False

    def round_start(self, hooker):
        global g_timer, g_instances
        print 'randomiseSpawner bf2_init'
        if self.spawner is None: return
        game.utilities.rconExec('ObjectTemplate.ActiveSafe ObjectSpawner ' + self.spawner)
        if self.spawner == game.utilities.rconExec('ObjectTemplate.name').lower():
            self.active = True
            g_instances.append(self)
            if not g_timer:
                g_timer = bf2.Timer(interval, TIMER_INTERVAL, 1)
                g_timer.setRecurring(TIMER_INTERVAL)
            self.calculateAlternates()
        else:
            print >>sys.stderr, 'randomiseSpawner: failed to set', self.spawner, 'as active'
    
    def round_end(self, hooker):
        global g_timer, g_instances
        if self.active:
            g_instances.remove(self)
            self.active = False
            if g_timer and len(g_instances) == 0:
                g_timer.destroy()
                g_timer = None
    
    def calcAlternate(self, source):
        if source is not None:
            if type(source) in (tuple, list):
                return source
            elif type(source) is str:
                return source.split()
            elif type(source) is dict:
                field = []
                for template, weight in source.items():
                    for x in range(weight):
                        field.append(template)
                return field
            else:
                print >>sys.stderr, 'randomiseSpawner: bad type for alternatives list %s' % type(source)
    
    def calculateAlternates(self):
        print 'calculateAlternates'
        self.alternates_team1 = self.calcAlternate(self.alternates_team1)
        print 'calculateAlternates1', self.alternates_team1
        self.alternates_team2 = self.calcAlternate(self.alternates_team2)
        print 'calculateAlternates2', self.alternates_team2
    
    def interval(self, userdata):
        if not self.active:
            self.round_end(None)
            return
        game.utilities.rconExec('ObjectTemplate.ActiveSafe ObjectSpawner ' + self.spawner)
        for alternates, idx in zip([self.alternates_team1, self.alternates_team2], [1, 2]):
            if alternates is not None:
                choice = random.choice(alternates)
                game.utilities.rconExec('ObjectTemplate.setObjectTemplate %d %s' % (idx, choice))
                print 'set', self.spawner, idx, 'to', choice
