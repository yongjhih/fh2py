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
# aiFixups.py -- fixes for things bots cannot understand
#
# !!! NOTE
# *** I'd really like to have implemented player-specific bot names here, but Player.setName is not
# *** updated on clients (remote or local), and therefore is utterly useless! Thanks DICE!
#
#  ©2006 Joseph Birr-Pixton aka ctz for Forgotten Hope

import bf2, host, bf2.Timer, random
from game.gameplayPlugin import base
import game.utilities

MAX_SPAWNER_DELAY = 5000

class aiFixups(base):
    def bf2_init(self, hooker):
        if host.sgl_getIsAIGame() != 1:
            print 'aiFixups: not an ai game, doing nothing'
            return
        self.go()
    
    def go(self):
        u = game.utilities
        r = u.rconExec
        
        mapname, gamemode, mapsize = u.getCurrentRound()
        
        # turn off fire.onlyFireWhenProne = 1
        #for gun in 'pzb39 mg34bipod boys breda30 mg42bipod'.split():
         #   u.active(gun)
         #   if u.templateProperty('fire.onlyFireWhenProne') == '1':
         #       r('ObjectTemplate.fire.onlyFireWhenProne 0')
	   
	    # turn off ammo.autoReload = 1
        if gamemode != 'gpm_coop':
            for gun in 'm1garand'.split():
                u.active(gun)
                if u.templateProperty('ammo.autoReload') == '1':
                    r('ObjectTemplate.ammo.autoReload 0')
        
        # armor.canBeRepairedWhenWreck = 1 and armor.canBeDestroyed = 0 causes crash
        for pco in bf2.objectManager.getObjectsOfType('dice.hfe.world.ObjectTemplate.PlayerControlObject'):
            u.active(pco.templateName)
            if u.templateProperty('armor.canBeDestroyed') == '0':
                r('ObjectTemplate.armor.canBeDestroyed 1')
            if u.templateProperty('armor.canBeRepairedWhenWreck') == '1':
                r('ObjectTemplate.armor.canBeRepairedWhenWreck 0')
        
        # fix spawners with huge spawntimes 
        # original values are min 90, max 120
        for spw in bf2.objectManager.getObjectsOfType('dice.hfe.world.ObjectTemplate.ObjectSpawner'):
            u.active(spw.templateName)
            try:
                if int(u.templateProperty('minSpawnDelay')) > MAX_SPAWNER_DELAY:
                    r('ObjectTemplate.minSpawnDelay 350')
            except Exception, e: print 'e:', e
            try:
                if int(u.templateProperty('maxSpawnDelay')) > MAX_SPAWNER_DELAY:
                    r('ObjectTemplate.maxSpawnDelay 500')
            except Exception, e: print 'e:', e
        