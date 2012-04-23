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
# mapLint.py -- map correctness testing
#
#  ©2007 Joseph Birr-Pixton aka ctz for Forgotten Hope
import bf2, host, bf2.Timer, random
from game.gameplayPlugin import base
import game.utilities as u
from game.conParser import ConParser
import game.perMapData

class mapLint(base):
    def __init__(self):
        self.f = None
        self.c = 0
        self.first = False
        
    def startlog(self):
        cm = u.getCurrentRound()
        print 'maplint starting for: %s (%s %d)'%(cm[0].lower(), cm[1].lower(), int(cm[2]))
        self.f = open('mods/fh2/maplint.log', 'a')
        print >>self.f, 'map: %s (%s %d)'%(cm[0].lower(), cm[1].lower(), int(cm[2]))
    
    def log(self, *args):
        if self.f:
            self.c += 1
            print >>self.f, ' '.join(args)
        else:
            print ' '.join(args)
    
    def stoplog(self):
        if self.f:
            print >>self.f, 'finished.', self.c, 'errors.'
            self.c = 0
            self.f.close()
        self.f = None
    
    def start(self):
        if u.rconExec('maplist.configfile') != 'mods/fh2/maplint.con':
            u.rconExec('maplist.clear')
            u.rconExec('maplist.configfile mods/fh2/maplint.con')
            u.rconExec('maplist.load')
            u.rconExec('admin.nextlevel 0')
            self.first = True
            print 'maplint: started'
        print 'maplint: maps:'
        print u.rconExec('maplist.list')
        print 'current', u.rconExec('maplist.currentmap'), 'next', u.rconExec('admin.nextlevel')
        
    def next(self):
        if int(u.rconExec('admin.nextlevel')) == 0 and not self.first:
            u.rconExec('quit')
        else:
            u.rconExec('admin.runnextlevel')
    
    def go(self):
        self.start()
        self.startlog()
        self.checkmap()
        self.checkpermapdata()
        self.stoplog()
        self.next()
    
    def checkpermapdata(self):
        for l in game.perMapData.g_log:
            self.log(l)
    
    def bf2_init(self, hooker):
        hooker.later(5, self.go)
    
    def check_mixed_lockedness(self, t, expect):
        u.active(t)
        subs = []
        for s in u.walkTemplate():
            subs.append(s)
        for s in subs:
            is_pco, is_locked = self.check_lockedness(s)
            if is_pco and is_locked != expect:
                self.log('!!! vehicle error: PCO', s, 'attached to', t, 'has mixed lockedness')

    def check_lockedness(self, t):
        u.active(t)
        if u.isType('PlayerControlObject'):
            locked = int(u.templateProperty('dontclearteamonexit'))
            self.check_mixed_lockedness(t, locked)
            return 1, locked
        return 0, 0

    def is_locked_vehicle(self, t):
        u.active(t)
        is_pco, is_locked = self.check_lockedness(t)
        return is_locked

    def checkmap(self):
        for spawner in bf2.objectManager.getObjectsOfType('dice.hfe.world.ObjectTemplate.ObjectSpawner'):
            u.active(spawner.templateName)
            script = u.printScriptTillItFuckingWorks()
            parser = ConParser()
            parser.run_string(script)
            if len(parser.templates) != 1:
                print 'parse failed for template script', spawner.templateName, ':'
                print script
                continue
            template = parser.templates[0]
            is_locked = int(template.properties.get('objecttemplate.teamonvehicle', [['0']])[0][0])
            assert template.name.lower() == spawner.templateName.lower()
            l = template.properties.get('objecttemplate.setobjecttemplate', [])
            for team, object in l:
                needs_lock = self.is_locked_vehicle(object)
                if is_locked and needs_lock:
                    continue
                
                if needs_lock and not is_locked:
                    self.log('!!! map error: vehicle', object, 'needs locking -- spawner', spawner.templateName, 'is incorrect')
                if is_locked and not needs_lock:
                    self.log('!!! map error: spawner', spawner.templateName, 'is locked but vehicle', object, 'does not support this')