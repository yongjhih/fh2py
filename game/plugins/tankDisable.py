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
# tankDisable.py -- sometimes disables tank engines when they hit criticalDamage
#  ©2006 Joseph Birr-Pixton aka ctz for Forgotten Hope
import bf2, host, bf2.Timer
import sys, random, traceback
from game.gameplayPlugin import base
import game.utilities
from game.stats.constants import vehicleTypeMap

DEBUG = 0
TIMER_INTERVAL = 5
DO_TANKDISABLE = 0
DO_PLANEDISABLE = 1

def reenablePCOBits(id, bits):
    disabled = 0
    bits = [b.lower() for b in bits]
    id = int(id)
    for i in range(id, id + 100):
        game.utilities.rconExec('object.active id'+str(i))
        info = game.utilities.rconExec('object.info').lower()
        for b in bits:
            if b in info:
                game.utilities.rconExec('object.setIsDisabledRecursive 0')
                disabled += 1
                if disabled == len(bits):
                    return

def disablePCOBits(id, bits, percentage = 0.5):
    # assuming no more than 100 ids per vehicle
    if DEBUG: print 'disablePCOBits:', 'id', id, 'bits', bits, '(%d%%)'%(percentage*100.0)
    id = int(id)
    ppbits = []
    if percentage == 1.0:
        sample = bits
    else:
        sample = random.sample(bits, int(len(bits) * percentage))
    for x in sample:
        ppbits.append('"%s"'%x.lower())
    if DEBUG:
        print 'looking for',ppbits,'under',id
    disabled = 0
    for i in range(id, id + 100):
        game.utilities.rconExec('object.active id'+str(i))
        info = game.utilities.rconExec('object.info').lower()
        for b in ppbits:
            if b in info:
                game.utilities.rconExec('object.setIsDisabledRecursive 1')
                disabled += 1
                if disabled == len(ppbits):
                    return

class PlaneTemplate:
    def __init__(self, name):
        self.name = name
        self.engines = []
        self.criticaldamage = 50
        self.valid = False
        self.probe()

    def probe(self):
        game.utilities.active(self.name)
        if not game.utilities.isType('PlayerControlObject'):
            return
        self.criticaldamage = int(int(game.utilities.templateProperty('armor.criticaldamage')) * 1.5)
        engines = []
        for child in game.utilities.walkTemplate():
            child = child.lower()
            if ('engine' in child or 'motor' in child) and 'physics' in child:
                engines.append(child)
        
        for e in engines:
            game.utilities.active(e)
            if not game.utilities.isType('Engine'): continue
            self.engines += [e]
            
        if DEBUG:
            print 'for plane',self.name
            print 'engines =', self.engines
            print 'crit damage=', self.criticaldamage
        self.valid = True

class TankTemplate:
    def __init__(self, name):
        self.name = name
        self.engine = None
        self.springs = []
        self.criticaldamage = 50
        self.valid = False
        self.probe()
    
    def probe(self):
        # select the root
        game.utilities.active(self.name)
        if not game.utilities.isType('PlayerControlObject'):
            return
        self.criticaldamage = int(int(game.utilities.templateProperty('armor.criticaldamage')) * 1.5)
        engines = []
        for child in game.utilities.walkTemplate():
            if 'Engine' in child or 'Motor' in child:
                engines.append(child)
        
        for e in engines:
            game.utilities.active(e)
            if not game.utilities.isType('Engine'): continue
            self.engine = e
            for s in game.utilities.walkTemplate():
                game.utilities.active(s)
                if game.utilities.isType('Spring'):
                    if game.utilities.templateProperty('networkableinfo').lower() == 'springinfo':
                        self.springs.append(s)
            
        if DEBUG:
            print 'for vehicle',self.name
            print 'engine =', self.engine
            print 'springs =', ', '.join(self.springs)
            print 'crit damage=', self.criticaldamage
        self.valid = True

def is_network_server():
    players = bf2.playerManager.getPlayers()
    if len(players) == 0: return True
    for p in players:
      if p.isValid() and not p.isRemote(): return False
    return True

class tankDisable(base):
    def __init__(self):
        self.active = False
        self.timer = None
        self.tanks = {}
        self.planes = {}
        self.dealtwith = {}
    
    def bf2_init(self, hooker):
        if DO_TANKDISABLE:
            for t in vehicleTypeMap:
                if vehicleTypeMap[t] == 0 or vehicleTypeMap[t] == 1 or vehicleTypeMap[t] == 2:
                    self.tanks[t] = TankTemplate(t)
        if DO_PLANEDISABLE:
            for t in vehicleTypeMap:
                if vehicleTypeMap[t] == 3:
                    self.planes[t] = PlaneTemplate(t)

    def round_start(self, hooker):
        print 'tankDisable round_start'
        self.active = True
        self.timer = bf2.Timer(self.interval, TIMER_INTERVAL, 1)
        self.timer.setRecurring(TIMER_INTERVAL)
        if not is_network_server():
            hooker.register('VehicleDestroyed', self.destroyedhook)
        self.dealtwith = {}
    
    def destroyedhook(self, object, attacker):
        if object.templateName.lower() == 'damagetrigger':
            if DEBUG: print 'got damagetrigger'
            self.interval(None)
    
    def round_end(self, hooker):
        if self.active:
            if self.timer:
                self.timer.destroy()
            self.active = False
            self.dealtwith = {}
    
    def interval(self, userdata):
        if not self.active:
            return
        try:
            if DEBUG: print 'dealthwith', self.dealtwith
            for pcoid, inf in self.dealtwith.items():
                object, info = inf
                if object.isValid() and object.getDamage() > info.criticaldamage:
                    if DEBUG: print 'reenabling a', info.name
                    if info.__class__ == TankTemplate:
                        if DEBUG: print 'is a tank'
                        reenablePCOBits(pcoid, info.springs)
                    else:
                        if DEBUG: print 'is a plane'
                        reenablePCOBits(pcoid, info.engines)
                    del self.dealtwith[pcoid]
                elif not object.isValid():
                    del self.dealtwith[pcoid]
        except Exception, e:
            print 'tankDisable interval reenable function failed', e
            
        try:
            checkthese = {}
            for p in bf2.playerManager.getPlayers():
                vehicle = p.getVehicle()
                vehicle = bf2.objectManager.getRootParent(vehicle)
                vln = vehicle.templateName.lower()
                if DEBUG: print p.getName(), 'is in a', vehicle.templateName
                if vln not in self.tanks and vln not in self.planes: continue
                if DEBUG: print '... which is a tank or plane'
                checkthese[vln] = 1
            
            if DEBUG: print len(checkthese.keys()), 'different tanks in use'
            for thing in checkthese.keys():
                if thing in self.tanks:
                    info = self.tanks[thing]
                    if not info.valid: continue
                    ids = []
                    for i in game.utilities.listObjectsOfTemplate(thing):
                        ids.append(i)
                    for pcoid, object in zip(ids, bf2.objectManager.getObjectsOfTemplate(thing)):
                        if pcoid in self.dealtwith: continue
                        if object.hasArmor and object.isPlayerControlObject and object.getDamage() <= info.criticaldamage and not object.getIsWreck():
                            self.dealtwith[pcoid] = (object, info)
                            disablePCOBits(pcoid, info.springs)
                elif thing in self.planes:
                    info = self.planes[thing]
                    if not info.valid: continue
                    ids = []
                    for i in game.utilities.listObjectsOfTemplate(thing):
                        ids.append(i)
                    for pcoid, object in zip(ids, bf2.objectManager.getObjectsOfTemplate(thing)):
                        if pcoid in self.dealtwith: continue
                        if object.hasArmor and object.isPlayerControlObject and object.getDamage() <= info.criticaldamage and not object.getIsWreck():
                            self.dealtwith[pcoid] = (object, info)
                            disablePCOBits(pcoid, info.engines, 1.0)
        except Exception, e:
            print 'tankDisable interval disable function failed', e
