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
# artillery.py -- artillery system. this script basically acts as an FDC.
#
#  ©2007 Joseph Birr-Pixton aka ctz for Forgotten Hope
import bf2, host, bf2.Timer, random
from game.gameplayPlugin import base
import game.utilities
import game.stats.constants as constants
import vehicleMetadata

INTERVAL = 2
WATCH_INTERVAL = 1
DEBUG = 0
VOCAL_DEBUG = 0

CAMERA_HEIGHT = 30.0
CAMERA_HEIGHT_LOW = 5.0

TARGET = 'artillery_marker'

class artilleryClient:
    def __init__(self, player, vehicle):
        self.player = player
        self.team = player.getTeam()
        self.vehicle = vehicle
        self.timer = None
        self.just_started = False
        self.current_spot = None
        self.rotations = []
        self.positions = []
        self.spots = []
        # randomly in the interval 160..200 degrees
        self.default_heading = 160.0 + (random.random() * 40.0)
        guntype = self.vehicle.templateName.lower()
        self.info = vehicleMetadata.artillery_info.get(guntype, None)
        if self.info is None:
            game.utilities.rconExec('game.sayall "error: please update vehicleMetadata.py for %s."'%guntype)
        self.nextspot()
    
    def destroy(self):
        if self.timer:
            self.timer.destroy()
            self.timer = None
    
    def interval(self, ignore = None):
        try:
            oldspot = self.current_spot
            if self.current_spot is None or not self.current_spot.isValid():
                self.nextspot()

            # if the spot changed, and the spot is valid:
            if self.current_spot != oldspot and self.current_spot is not None:
                self.handle_spot()
                if not self.info.get('static', True):
                    self.just_started = True
            
            # if the artillery piece is movable (ie an assault gun):
            elif not self.info.get('static', True) and self.current_spot is not None:
                self.handle_spot()
                self.just_started = True
                
            if self.just_started:
                self.set_positions()
                self.just_started = False
        except Exception, e:
            print 'artilleryClient interval exception', e
    
    def set_positions(self):
        for thing, rotation in self.rotations:
            if thing and thing.isValid():
                if thing.getRotation() != rotation:
                    if DEBUG: print 'setting rotation on', thing.templateName, 'to', rotation
                    thing.setRotation(rotation)
        for thing, position in self.positions:
            if thing and thing.isValid():
                if thing.getPosition() != position:
                    if DEBUG: print 'setting position on', thing.templateName, 'to', position
                    thing.setPosition(position)
    
    def nextspot(self, prev = False):
        self.current_spot = self.choosespot(prev)
        if self.current_spot is None:
            self.handle_nospot()
        else:
            self.handle_spot()
        if VOCAL_DEBUG and self.current_spot is not None:
            spottername = '???'
            if hasattr(self.current_spot, 'spotter') and self.current_spot.spotter is not None and self.current_spot.spotter.isValid():
                spottername = self.current_spot.spotter.getName()
        self.player.artillerySpot = self.current_spot
        self.start_timer()
        self.just_started = True
    
    def choosespot(self, prev = False):
        self.spots = [x for x in bf2.objectManager.getObjectsOfTemplate(TARGET) if getattr(x, 'targetTeam', -1) == self.team \
                and x.isValid() and game.utilities.reasonableObject(x)]
                
        if DEBUG: print 'spots', self.spots
        if len(self.spots) == 0: return None
        if self.current_spot is None:
            # choose the first
            return self.spots[0]
        else:
            if len(self.spots) == 1: return self.spots[0]
            if self.current_spot not in self.spots: return self.spots[0]
            # index of this one
            i = self.spots.index(self.current_spot)
            if prev:
                n = -1
            else:
                n = 1
            # next one mod how many
            i = (i + n) % len(self.spots)
            return self.spots[i]
    
    def start_timer(self):
        if self.timer is None:
            self.timer = bf2.Timer(self.interval, INTERVAL, 1)
            self.timer.setRecurring(INTERVAL)
    
    def handle_nospot(self):
        azimuth_obj = game.utilities.findSubObject(self.vehicle, self.info['azimuth'])
        elevation_obj = game.utilities.findSubObject(self.vehicle, self.info['elevation'])
        camera_obj = game.utilities.findSubObject(self.vehicle, self.info['camera'])
        
        if None in (camera_obj, azimuth_obj, elevation_obj):
            print 'cannot find one of', repr(self.info), 'in vehicle', self.vehicle.templateName
            print locals()
            return
        self.rotations = []
        self.positions = []
        self.positions.append((azimuth_obj, azimuth_obj.getParent().getPosition()))
        self.rotations.append((azimuth_obj, (0.0, 0.0, self.default_heading)))
        self.positions.append((elevation_obj, elevation_obj.getParent().getPosition()))
        self.rotations.append((elevation_obj, (0.0, 0.0, self.default_heading)))
        v = self.vehicle.getPosition()
        self.positions.append((camera_obj, (v[0], v[1] + CAMERA_HEIGHT_LOW, v[2])))
        self.rotations.append((camera_obj, (0.0, 90.0, 0.0)))
        if self.info['indicator']:
            targetind_obj = game.utilities.findSubObject(self.vehicle, self.info['indicator'])
            if targetind_obj:
                self.rotations.append((targetind_obj, (0.0, 0.0, 0.0)))
    
    def calc_trajectory(self, gun, target):
        import artillerymath
        return artillerymath.go(self.vehicle, self.info, gun, target)
        
    def handle_spot(self):
        barrel_obj = game.utilities.findSubObject(self.vehicle, self.info['barrel'])
        azimuth_obj = game.utilities.findSubObject(self.vehicle, self.info['azimuth'])
        elevation_obj = game.utilities.findSubObject(self.vehicle, self.info['elevation'])
        camera_obj = game.utilities.findSubObject(self.vehicle, self.info['camera'])
        
        if None in (camera_obj, barrel_obj, azimuth_obj, elevation_obj):
            print 'cannot find one of', repr(self.info), 'in vehicle', self.vehicle.templateName
            print locals()
            return
        
        u = barrel_obj.getPosition()
        v = self.current_spot.getPosition()
        
        rq_el, rq_hd = self.calc_trajectory(u, v)

        # for movable gun, compensate for pitch
        if not self.info.get('static', True):
            yaw, pitch, roll = game.utilities.rootParent(self.vehicle).getRotation()
            rq_el = rq_el - pitch
            if DEBUG: print 'Compensated pitch by %d for vehicle %s' % (pitch, self.vehicle.templateName)
        
        self.rotations = []
        self.positions = [] 
        
        # now prod the gun
        self.rotations.append((azimuth_obj, (0.0, 0.0, rq_hd)))
        self.rotations.append((elevation_obj, (0.0, 0.0, rq_el - self.info['elevation_offset'])))
        
        # calculate camera position
        self.positions.append((camera_obj, (v[0], v[1] + CAMERA_HEIGHT, v[2])))
        if not self.info.get('static', True):
            # camera behaves slightly different on mobile artillery
            self.rotations.append((camera_obj, (0.0, 90.0 - pitch, 0.0 - roll)))
        else:
            self.rotations.append((camera_obj, (rq_hd, 90.0, 0.0)))
        
        if self.info['indicator']:
            targetind_obj = game.utilities.findSubObject(self.vehicle, self.info['indicator'])
            if targetind_obj:
                if len(self.spots) == 0:
                    ang = 0.0
                elif len(self.spots) == 1:
                    ang = 240.0
                else:
                    ang = 120.0
                self.rotations.append((targetind_obj, (0.0, ang, 0.0)))

class artilleryWatcher:
    def __init__(self):
        self.timer = None
        self.players = []
        self.targettingDevices = [x.lower() for x, y in constants.weaponTypeMap.iteritems() if y == constants.WEAPON_TYPE_TARGETING] + vehicleMetadata.targetting_pcos.values()
        if DEBUG: print 'targettingDevices are', self.targettingDevices
    
    def watch(self, player):
        if len(self.players) == 0:
            self.start_timer()
        if player not in self.players:
            self.players.append(player)
    
    def unwatch(self, player):
        if player in self.players:
            self.players.remove(player)
        if len(self.players) == 0:
            self.end_timer()
    
    def start_timer(self):
        if DEBUG: print 'artilleryWatcher: starting timer'
        self.timer = bf2.Timer(self.interval, WATCH_INTERVAL, 1)
        self.timer.setRecurring(WATCH_INTERVAL)
    
    def end_timer(self):
        if self.timer is not None:
            if DEBUG: print 'artilleryWatcher: ending timer'
            self.timer.destroy()
            self.timer = None
    
    def get_count(self, player):
        c = 0
        if DEBUG: print player.score.bulletsFired
        for template, count in player.score.bulletsFired:
            if template.lower() in self.targettingDevices:
                c += count
        if DEBUG: print player.getName(), 'total targets placed:', c
        return c
    
    def interval(self, ignore = None):
        try:
            self._interval()
        except Exception, e:
            print 'artilleryWatcher interval exception', e
    
    def _interval(self):
        for p in self.players:
            countnow = self.get_count(p)
            ltc = getattr(p, 'lastTargettingCount', countnow)
            p.lastTargettingCount = countnow
            if countnow > ltc:
                # weapon was fired during the last interval. look for new targets and label them with this player and his current team
                for s in bf2.objectManager.getObjectsOfTemplate(TARGET):
                    if s and s.isValid() and not hasattr(s, 'spotter') and game.utilities.reasonableObject(s):
                        s.spotter = p
                        s.targetTeam = p.getTeam()
                        bf2.gameLogic.sendGameEvent(p, 10, 4)
                        if DEBUG: print 'artillery: assigning new spot to', p.getName()
                        break # only one target per player per interval
    
    def destroy(self):
        self.end_timer()
        self.players = []

class artillery(base):
    def __init__(self):
        self.clients = []
        self.watcher = None
    
    def find_client(self, player = None, vehicle = None):
        if player:
            for x in self.clients:
                if x.player == player: return x
        if vehicle:
            for x in self.clients:
                if x.vehicle == vehicle: return x
        return None
    
    def rconhook(self, playeridx, command):
        if not command.startswith('nextspot') and \
           not command.startswith('prevspot'): return
        if playeridx == -1: playeridx = 255
        player = bf2.playerManager.getPlayerByIndex(playeridx)
        if not player.isValid(): return
        client = self.find_client(player = player)
        if client is None: return
        client.nextspot(command.startswith('prevspot'))
    
    def enterhook(self, player, vehicle, freeweapon):
        try:
            self.watcher.unwatch(player)
            if player is None or vehicle is None:
                return
            if vehicle.templateName.lower() in vehicleMetadata.artillery:
                if DEBUG: print 'new artilleryClient', player.getName(), 'in a', vehicle.templateName
                self.clients.append(artilleryClient(player, vehicle))
            if vehicle.templateName.lower() in vehicleMetadata.targetting_pcos.keys():
                if DEBUG: print 'artillery:', player.getName(), 'entered targeting PCO'
                self.watcher.watch(player)
        except Exception, e:
            print 'artillery enterhook exception', e
    
    def exithook(self, player, vehicle):
        try:
            if player is None or vehicle is None:
                return
            self.weaponhook(player, None, player.getPrimaryWeapon())
            if vehicle.templateName.lower() in vehicleMetadata.artillery:
                o = self.find_client(player, vehicle)
                if DEBUG: print 'destroying artilleryClient', player.getName(), 'in a', vehicle.templateName
                if o is None: return
                o.destroy()
                self.clients.remove(o)
            if vehicle.templateName.lower() in vehicleMetadata.targetting_pcos.keys():
                if DEBUG: print 'artillery:', player.getName(), 'exited targeting PCO'
                self.hooker.later(1, self.watcher.unwatch, player)
        except Exception, e:
            print 'artillery exithook exception', e

    def weaponhook(self, player, wfrom, wto):
        try:
            if wto is not None and constants.getWeaponType(wto.templateName) == constants.WEAPON_TYPE_TARGETING:
                if DEBUG: print 'artillery:', player.getName(), 'switched to targeting device'
                self.watcher.unwatch(player)
                self.watcher.watch(player)
            if wfrom is not None and constants.getWeaponType(wfrom.templateName) == constants.WEAPON_TYPE_TARGETING:
                if DEBUG: print 'artillery:', player.getName(), 'switched from targeting device'
                self.hooker.later(1, self.watcher.unwatch, player)
        except Exception, e:
            print 'artillery weaponhook exception', e
    
    def killedhook(self, player, *args):
        if self.watcher: self.watcher.unwatch(player)
    
    def round_start(self, hooker):
        hooker.register('EnterVehicle', self.enterhook)
        hooker.register('ExitVehicle', self.exithook)
        hooker.register('RemoteCommand', self.rconhook)
        hooker.register('PlayerChangeWeapon', self.weaponhook)
        hooker.register('PlayerDeath', self.killedhook)
        if DEBUG: print 'artillery: hooked'
        for x in self.clients:
            x.destroy()
        self.clients = []
        self.watcher = artilleryWatcher()
        self.hooker = hooker
    
    def round_end(self, hooker):
        if DEBUG: print 'artillery: round_end'
        for x in self.clients:
            x.destroy()
        self.clients = []
        if self.watcher:
            self.watcher.destroy()
            self.watcher = None
