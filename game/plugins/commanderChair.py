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
# commanderChair.py -- spams rank events at commanders in commander chairs
# ©2006 Joseph Birr-Pixton aka ctz for Forgotten Hope
import bf2, host, bf2.Timer
from game.gameplayPlugin import base
import game.utilities

chairTemplates = ['gercommradio', 'britcommradio', 'aecdorchester_passenger', 'aecdorchester_de_passenger', 'aecdorchester_france_passenger', 'storch_france_rearspotter', 'storch_trop_rearspotter', 'pipercub_gb_frontspotter', 'pipercub_us_frontspotter', 'sdkfz250_3_commander']
SPAM_TIME = 9

class commanderChair(base):
    def __init__(self):
        self.timer = None
        self.ids = []

    def round_start(self, hooker):
        hooker.register('EnterVehicle', self.enterhook)
        hooker.register('ExitVehicle', self.exithook)
        hooker.register('PlayerDeath', self.deathhook)
        hooker.register('ChangedCommander', self.chcomhook)
    
    def round_end(self, hooker):
        self.ids = []
        if self.timer:
            self.timer.destroy()
            self.timer = None
    
    def deathhook(self, player, soldier):
        self.removeplayer(player)
    
    def chcomhook(self, teamid, old_commander, new_commander):
        if old_commander:
            self.removeplayer(old_commander)
        if new_commander:
            self.removeplayer(new_commander)
    
    def enterhook(self, player, vehicle, *args):
        if vehicle.templateName.lower() not in chairTemplates:
            return
        
        if player.isCommander():
            # set up timer to spam rank events
            if self.timer == None:
                self.timer = bf2.Timer(self.rankevent, SPAM_TIME, 1)
                self.timer.setRecurring(SPAM_TIME)
            self.ids.append(player.index)
            self.rankevent(0) # quick!
    
    def exithook(self, player, vehicle):
        if vehicle.templateName.lower() not in chairTemplates:
            return
        if player.isCommander():
            self.removeplayer(player)
    
    def removeplayer(self, player):
        if player.index in self.ids:
            self.ids.remove(player.index)
        if len(self.ids) == 0:
            if self.timer:
                self.timer.destroy()
                self.timer = None
        
    def rankevent(self, ignore):
        for id in self.ids:
            host.sgl_sendRankEvent(id, 1, 2)
