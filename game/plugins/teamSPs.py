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
# teamSPs.py -- team assigned spawnpoints.
#
#  ©2010 Spit aka python-newbie for Forgotten Hope
import bf2, host, bf2.Timer
from game.gameplayPlugin import base
import game.utilities

DEBUG = 0
SPAM_INTERVAL = 20

g_daemon = None

class teamSPsDaemon:
    def __init__(self):
        self.sps_dict = {}
        self.cps_dict = {}
        self.spam_templates = []
        self.registered = False
        self.spam_timer = None
    
    def cp_dict(self):
        try:
            # Build a dictionary ID -> CP
            if not self.cps_dict:
                controlPoints = bf2.objectManager.getObjectsOfType('dice.hfe.world.ObjectTemplate.ControlPoint')
                for cp in controlPoints:
                    cp_name = cp.templateName
                    game.utilities.active(cp_name)
                    cpid = int(game.utilities.templateProperty('controlPointId'))
                    self.cps_dict[cpid] = cp_name
                if DEBUG: print self.cps_dict
        except Exception, e:
            print 'cp_dict exception', e

    def add(self, sps, team):
        # Building a dictionary containing all team assigned SPs and their desired teams:
        for sp in sps:
            self.sps_dict[sp] = team
        if DEBUG: print self.sps_dict
        
    def clear(self):
        self.sps_dict = {}
        self.cps_dict = {}
        self.spam_templates = []
        self.registered = False
        if self.spam_timer is not None:
            self.spam_timer.destroy()
            self.spam_timer = None
    
    def update_sps(self, controlpoint, team):
        if team == 0: return # Do nothing on grey-out
        cp_name = controlpoint.templateName
        game.utilities.active(cp_name)
        id = int(game.utilities.templateProperty('controlPointId'))
        # Now find and list all spawnpoints with this id.
        spawns = []
        for sp in self.sps_dict:
            game.utilities.active(sp)
            if int(game.utilities.templateProperty('setControlPointId')) == id:
                spawns.append(sp)
        
        # Return if this controlpoint has no team-assigned spawnpoints
        if spawns == []:
            if DEBUG: print '%s has no team-spawnpoints, doing nothing'%cp_name
            return
        
        # Check their desired teams and disabe/enable:
        for sp in spawns:
            d_team = self.sps_dict[sp]
            # Should the SP be active now?
            if d_team == team:
                #yes
                game.utilities.active(sp)
                game.utilities.rconExec('ObjectTemplate.setOnlyForAI 0')
                if DEBUG: print 'Enabled %s because team %d captured %s.'%(sp, team, cp_name)
            else:
                #no
                game.utilities.active(sp)
                game.utilities.rconExec('ObjectTemplate.setOnlyForAI 1')
                if DEBUG: print 'Disabled %s because team %d captured the %s.'%(sp, team, cp_name)
                
        
    def getTeam(self, controlpoint):
        controlPoints = bf2.objectManager.getObjectsOfType('dice.hfe.world.ObjectTemplate.ControlPoint')
        for cp in controlPoints:
            if cp.templateName == controlpoint:
                return int(cp.cp_getParam('team'))
                
    def onFlagCapture(self, controlpoint, attacker):
        try:
            global g_daemon
            if int(attacker) == 0: return # Do nothing on grey-out.
            team = int(controlpoint.cp_getParam('team'))
            self.update_sps(controlpoint = controlpoint, team = team)
        except Exception, e:
            print 'onFlagCapture exception', e
            
    def spam(self, sp):
        self.spam_templates.append(sp)
        if self.spam_timer is None:
            self.spam_timer = bf2.Timer(self.spamer, 0, 1)
            self.spam_timer.setRecurring(SPAM_INTERVAL)
            
    def spamer(self, userdata):
        for sp in self.spam_templates:
            game.utilities.sayAll('teamSPs ERROR when dealing with ' + str(sp))
       
class teamSPs(base):
    def __init__(self, sps, team):
        self.sps = sps
        self.team = int(team)
        global g_daemon
        if g_daemon is None:
            g_daemon = teamSPsDaemon()
    
    def update_sps_global(self):
        global g_daemon
        for sp in self.sps:
            try:
                game.utilities.active(sp)
                spid = int(game.utilities.templateProperty('setControlPointId'))
                controlpoint = g_daemon.cps_dict[spid]
                cp_team = g_daemon.getTeam(controlpoint = controlpoint)
                # Should the spawnpoint be active now?
                if cp_team != self.team:
                    #no
                    game.utilities.active(sp)
                    game.utilities.rconExec('ObjectTemplate.setOnlyForAI 1')
                    if DEBUG: print 'Disabled spawnpoint %s because of wrong team owning the CP'%sp
                else:
                    #yes
                    game.utilities.active(sp)
                    game.utilities.rconExec('ObjectTemplate.setOnlyForAI 0')
                    if DEBUG: print 'Controlpoint in right hands, enabled the %s spawnpoint'%sp
            except Exception, e:
                print 'update_sps_global exception', e
                g_daemon.spam(sp)
                
    def round_start(self, hooker):
        try:
            global g_daemon
            g_daemon.cp_dict()
            g_daemon.add(sps = self.sps, team = self.team)
            if not hooker.hasHook('ControlPointChangedOwner', g_daemon.onFlagCapture):
                hooker.register('ControlPointChangedOwner', g_daemon.onFlagCapture)
                if DEBUG: print 'teamSPs hooked'
            else:
                if DEBUG: print 'teamSPs already hooked'
            # Disable spawnpoints in wrong hands at round start:
            self.update_sps_global()
        except Exception, e:
            print 'round_start exception', e
        
    def round_end(self, hooker):
        try:
            global g_daemon
            if g_daemon is not None:
                g_daemon.clear()
        except Exception, e:
            print 'round_end exception', e
            
    def onCPStatusChange(self, cp, t):
        g_daemon.onFlagCapture(cp, t)