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
# gpm_gr.py -- "gold rush" gamemode, based on the awesome enemy territory map of the same name
#  ©2006 Joseph Birr-Pixton aka ctz for Forgotten Hope

import host
import bf2
import math
from game.scoringCommon import addScore, RPL
from bf2 import g_debug
import game.gameplayPlugin, game.utilities

SCORE_RETURN = 10
SCORE_RETURNASSIST = 3
SCORE_DEFEND = 5

KITS = {'axis_pickupgold': 1, 'allied_pickupgold': 2}
WANT_KITS = ['', 'allied_pickupgold', 'axis_pickupgold']

Top = 0
Middle = 1
Bottom = 2

MEDAL_TAKE = (1031406,1)
MEDAL_CAPTURE = (1031619,1)
MEDAL_CAPTUREASSIST = (1031119,1)
MEDAL_RETRIEVE = (1031120,1)

g_controlPoints = [] # cache, as this map won't change
g_plugin = None

def init():
    # events hook
    global g_plugin
    host.registerGameStatusHandler(onGameStatusChanged)
    if host.sgl_getIsAIGame() == 1:
        host.sh_setEnableCommander(1)
    else:
        host.sh_setEnableCommander(1)
        
    host.registerHandler('TimeLimitReached', onTimeLimitReached, 1)
    
    if g_debug: print "gpm_gr.py initialized"
    g_plugin = game.gameplayPlugin.pluginsystem()

def deinit():
    bf2.triggerManager.destroyAllTriggers()
    global g_plugin
    global g_controlPoints
    g_controlPoints = []
    host.unregisterGameStatusHandler(onGameStatusChanged)
    if g_debug: print "gpm_gr.py uninitialized"
    if g_plugin: g_plugin.bf2_deinit()

def onGameStatusChanged(status):
    global g_plugin, g_donehooks
    print 'onGameStatusChanged', status
    global g_controlPoints
    
    if status == bf2.GameStatus.Playing:
        print 'PreGame plugin bf2_init', g_plugin
        try:
            if g_plugin: g_plugin.bf2_init()
        except Exception, e:
            print 'bf2_init exception', e
        
        print 'Playing plugin round_start', g_plugin
        try:
            if g_plugin: g_plugin.round_start()
        except Exception, e:
            print 'round_start exception', e
        
        # add control point triggers
        g_controlPoints = bf2.objectManager.getObjectsOfType('dice.hfe.world.ObjectTemplate.ControlPoint')
        for obj in g_controlPoints:
            radius = float(obj.getTemplateProperty('radius'))
            isHemi = int(obj.cp_getParam('isHemisphere'))
            if isHemi != 0:
                id = bf2.triggerManager.createHemiSphericalTrigger(obj, onCPTrigger, '<<PCO>>', radius, (1, 2, 3))
            else:
                id = bf2.triggerManager.createRadiusTrigger(obj, onCPTrigger, '<<PCO>>', radius, (1, 2, 3))            
            obj.triggerId = id
            obj.lastAttackingTeam = 0
            if obj.cp_getParam('team') > 0:
                obj.flagPosition = Top
            else:
                obj.flagPosition = Bottom
        
        # setup ticket system
        ticketsTeam1 = calcStartTickets(10)
        ticketsTeam2 = calcStartTickets(10)
        
        print 'tickets start at', ticketsTeam1, 'vs', ticketsTeam2
        
        bf2.gameLogic.setTickets(1, ticketsTeam1)
        bf2.gameLogic.setTickets(2, ticketsTeam2)
        
        bf2.gameLogic.setTicketState(1, 0)
        bf2.gameLogic.setTicketState(2, 0)
        bf2.gameLogic.setTicketLimit(1, 1, 0)
        bf2.gameLogic.setTicketLimit(2, 1, 0)
        bf2.gameLogic.setTicketLimit(1, 2, 1)
        bf2.gameLogic.setTicketLimit(2, 2, 1)
        bf2.gameLogic.setTicketLimit(1, 3, 1)
        bf2.gameLogic.setTicketLimit(2, 3, 1)
        bf2.gameLogic.setTicketLimit(1, 4, 1)
        bf2.gameLogic.setTicketLimit(2, 4, 1)
        bf2.gameLogic.setTicketChangePerSecond(1, 0)
        bf2.gameLogic.setTicketChangePerSecond(2, 0)
        
        host.registerHandler('TicketLimitReached', onTicketLimitReached)
        
        # player events
        host.registerHandler('PlayerKilled', onPlayerKilledGR)
        host.registerHandler('PlayerSpawn', onPlayerSpawn)
        host.registerHandler('PickupKit', onPickupKit)
        
        if g_debug: print "Goldrush gamemode initialized."
    else:
        if g_plugin: g_plugin.round_end()
        bf2.triggerManager.destroyAllTriggers()
        g_controlPoints = []

def calcStartTickets(mapDefaultTickets):
    return int(mapDefaultTickets * (bf2.serverSettings.getTicketRatio() / 100.0))

def onTimeLimitReached(value):
    team1tickets = bf2.gameLogic.getTickets(1)
    team2tickets = bf2.gameLogic.getTickets(2)
    
    winner = 0
    victoryType = 0
    if team1tickets > team2tickets:
        winner = 1
        victoryType = 3
    elif team2tickets > team1tickets:
        winner = 2
        victoryType = 3
    
    host.sgl_endGame(winner, victoryType)

class KitInfo:
    def __init__(self):
        self.holders = []
        self.disabled = False
    
    def add_holder(self, player):
        self.holders.append(player)
    
    def award_holders(self, capturer):
        for h in self.holders:
            if h != capturer:
                bf2.gameLogic.sendMedalEvent(h, *MEDAL_CAPTUREASSIST)
                addScore(p, SCORE_RETURNASSIST, RPL)

def process_kit(kit):
    if type(kit.token) == type(KitInfo()):
        return
    else:
        kit.token = KitInfo()

# called when tickets reach a predetermined limit (negativ value means that the tickets have become less than the limit)
def onTicketLimitReached(team, limitId):
    if (limitId == -1):
        if (team == 1):
            winner = 2
        elif (team == 2):
            winner = 1
        
        bf2.gameLogic.setTicketState(1, 0)
        bf2.gameLogic.setTicketState(2, 0)
        
        host.sgl_endGame(winner, 3)

def onPickupKit(player, kit):
    try:
        return _onPickupKit(player, kit)
    except Exception, e:
        print 'onPickupKit failed:', e
        
def _onPickupKit(player, kit):
    team = player.getTeam()
    wantkit = WANT_KITS[team]
    if kit: process_kit(kit)
    if kit is not None and kit.templateName.lower() == wantkit and not kit.token.disabled:
        bf2.gameLogic.sendMedalEvent(player, *MEDAL_TAKE)
        kit.token.add_holder(player)
        game.utilities.sayTeam("%s took some gold from you! Get it back!"%player.getName(), [0, 2, 1][player.getTeam()])
        game.utilities.sayTeam("%s took some enemy gold! Protect him!"%player.getName(), player.getTeam())

# called when someone enters or exits cp radius
def onCPTrigger(triggerId, cp, vehicle, enter, userData):
    try:
        return _onCPTrigger(triggerId, cp, vehicle, enter, userData)
    except Exception, e:
        print 'onCPTrigger failed:', e
        
def _onCPTrigger(triggerId, cp, vehicle, enter, userData):
    if not cp.isValid(): return
    
    # only do stuff for uncaps
    if cp.cp_getParam('unableToChangeTeam') == 0:
        return
    
    cpowner = cp.cp_getParam('team')
    if vehicle and enter:
        for p in vehicle.getOccupyingPlayers():
            if p.getTeam() != cpowner: continue
            kit = p.getKit()
            wantkit = WANT_KITS[p.getTeam()]
            if kit is not None and kit.templateName.lower() == wantkit and not kit.token.disabled:
                kit.token.disabled = True
                kit.token.award_holders(p)
                p.score.cpCaptures += 1
                addScore(p, SCORE_RETURN, RPL)
                bf2.gameLogic.sendMedalEvent(p, *MEDAL_CAPTURE)
                game.utilities.sayTeam("%s captured some of your gold!"%p.getName(), [0, 2, 1][p.getTeam()])
                game.utilities.sayTeam("%s captured some enemy gold!"%p.getName(), p.getTeam())
                if cpowner == 2:
                    bf2.gameLogic.setTickets(1, bf2.gameLogic.getTickets(1) - 1)
                else:
                    bf2.gameLogic.setTickets(2, bf2.gameLogic.getTickets(2) - 1)

def onPlayerKilledGR(victim, attacker, weapon, assists, object):
    if not victim: 
        return
    team = victim.getTeam()
    bf2.gameLogic.setTickets(team, bf2.gameLogic.getTickets(team) + 1)
    
    kit = victim.getKit()
    if kit is not None and kit.templateName.lower() == KITNAME:
        addScore(attacker, SCORE_DEFEND, RPL)
        bf2.gameLogic.sendMedalEvent(attacker, *MEDAL_RETRIEVE)

def onPlayerSpawn(player, soldier):
    pass

