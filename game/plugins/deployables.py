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
# deployables.py -- support for deployable vehicles
#
#  ©2007 Joseph Birr-Pixton aka ctz for Forgotten Hope
import bf2, host, bf2.Timer, random
from game.gameplayPlugin import base
import game.utilities

import vehicleMetadata

REQUEST_OBJECT = 'deploy_marker'
REQUEST_DISTANCE = 10.0
REQUEST_RADIUS = 0.0
REQUEST_DELAY = 2
PLAYER_TAG = 'hasOutstandingDeployed'
PLAYER_LASTPOS = 'lastDeploymentPosition'
PLAYER_LASTDIFF = 1.0

class deployables(base):
    def __init__(self):
        self.hooker = None
        
    def _check_stats(self, player, weaponname):
        weaponname = weaponname.lower()
        for template, count in player.score.bulletsFired:
            if template.lower() == weaponname:
                if count:
                    self._check_requests(player, weaponname)
    
    def _clean(self, player, weaponname):
        if not hasattr(player, PLAYER_LASTPOS):
            return False
        template = vehicleMetadata.deployables[weaponname]['template']
        old_objects = bf2.objectManager.getObjectsOfTemplate(template)
        for o in old_objects:
            if o and o.isValid() and game.utilities.reasonableObject(o):
                if game.utilities.vectorDistance(getattr(player, PLAYER_LASTPOS), o.getPosition()) < PLAYER_LASTDIFF:
                    if o.hasArmor:
                        if len(o.getOccupyingPlayers()):
                            # cannot destroy if someone is occupying.
                            return False
                        else:
                            o.setDamage(0)
                            return True
                    else:
                        # BF2-BUG: some valid pcos in fail to get armor properties, seems to be early in a round.
                        #          nothing we can do here, so disallow the spawn :(
                        return False
        return False
    
    def _serve_request(self, req, player, weaponname):
        req.served = True
        if getattr(player, PLAYER_TAG, False):
            if not self._clean(player, weaponname):
               return
        pos = game.utilities.xform(req.getPosition(), [0.0, vehicleMetadata.deployables[weaponname].get('offset', 0.0) - REQUEST_RADIUS, 0.0])
        rot = req.getRotation()
        if 'flatten' in vehicleMetadata.deployables[weaponname]:
            rot = game.utilities.layFlat(rot)
        game.utilities.createObject(vehicleMetadata.deployables[weaponname]['template'], pos, rot)
        setattr(player, PLAYER_TAG, True)
        setattr(player, PLAYER_LASTPOS, pos)
        
    def _check_requests(self, player, weaponname):
        reqs = bf2.objectManager.getObjectsOfTemplate(REQUEST_OBJECT)
        for r in reqs:
            if r and r.isValid() and game.utilities.reasonableObject(r):
                if hasattr(r, 'served'):
                    continue
                if game.utilities.vectorDistance(player.getDefaultVehicle().getPosition(), r.getPosition()) < REQUEST_DISTANCE:
                    self.hooker.later(REQUEST_DELAY, self._serve_request, r, player, weaponname)
                else:
                    continue
    
    def weaponhook(self, player, wfrom, wto):
        if wfrom and wfrom.templateName.lower() in vehicleMetadata.deployables:
            self._check_stats(player, wfrom.templateName)
    
    def vehiclehook(self, player, vehicle, *args):
        if vehicle and vehicle.templateName.lower() in [x['template'] for x in vehicleMetadata.deployables.values()]:
            setattr(player, PLAYER_TAG, False)
            
    def spawnhook(self, player, soldier):
        if player:
            setattr(player, PLAYER_TAG, False)
            setattr(player, PLAYER_LASTPOS, (0.0, 0.0, 0.0))
    
    def round_start(self, hooker):
        self.hooker = hooker
        hooker.register('PlayerChangeWeapon', self.weaponhook)
        hooker.register('EnterVehicle', self.vehiclehook)
        hooker.register('PlayerSpawn', self.spawnhook)
    
    def round_end(self, hooker):
        self.hooker = None
