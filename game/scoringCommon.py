# common scoring 

import host
import bf2
import game.utilities
from game.stats.constants import *

SCORE_KILL_BASE = 1
SCORE_TEAMKILL = -4
SCORE_TEAMKILL_MINE = -2
SCORE_SUICIDE = -1
SCORE_REVIVE = 2
SCORE_TEAMDAMAGE = -1
SCORE_TEAMVEHICLEDAMAGE = -1

IGNORE_MINEFLAG_DIST = 10.0

SCORE_KILLASSIST_DRIVER = 1
SCORE_KILLASSIST_PASSENGER = 0
SCORE_KILLASSIST_TARGETER = 2
SCORE_KILLASSIST_DAMAGE = 1
SCORE_KILLASSIST_SQUAD = 1

REPAIR_POINT_LIMIT = 75
HEAL_POINT_LIMIT = 100
GIVEAMMO_POINT_LIMIT = 100
TEAMDAMAGE_POINT_LIMIT = 25
TEAMVEHICLEDAMAGE_POINT_LIMIT = 50

MIN_TAXI_DIST = 200
SCORE_TAXI = 1

# sub score
NORMAL = 0
SKILL = 1
RPL = 2
CMND = 3

SCORE_DEBUG = 0
g_debug = SCORE_DEBUG

VEHICLE_TYPE_weights = {
    VEHICLE_TYPE_HEAVYARMOR:  6,
    VEHICLE_TYPE_NAVAL:       6,
    VEHICLE_TYPE_MEDIUMARMOR: 4,
    VEHICLE_TYPE_AIR:         4,
    VEHICLE_TYPE_ARTILLERY:   4,
    VEHICLE_TYPE_RADIO:       3,
    VEHICLE_TYPE_LIGHTARMOR:  2,
    VEHICLE_TYPE_ANTIAIR:     2,
    VEHICLE_TYPE_APC:         2,
    VEHICLE_TYPE_ARMOREDCAR:  2,
    VEHICLE_TYPE_ATGUN:       2,
    VEHICLE_TYPE_TRANSPORT:   1,
    VEHICLE_TYPE_MACHINEGUN:  0,
    VEHICLE_TYPE_PARACHUTE:   0,
    VEHICLE_TYPE_SOLDIER:     0,
}

SCORE_EXTRA_NCO = 8

def importance_modifier(victim, victim_vehicle, attacker_weapon, attacker_vehicle):
    if None in (victim_vehicle, victim):
        return 0
    
    vvt = getVehicleType(victim_vehicle.templateName)
    try:
        if vvt == VEHICLE_TYPE_SOLDIER:
            if victim.isSquadLeader() or victim.isCommander():
                if g_debug: print 'importance_modifier: giving', SCORE_EXTRA_NCO, 'extra points for destroying an nco'
                return SCORE_EXTRA_NCO
        if vvt in VEHICLE_TYPE_weights:
            if g_debug: print 'importance_modifier: giving', VEHICLE_TYPE_weights[vvt], 'extra points for destroying a', VEHICLE_TYPE_names[vvt]
            return VEHICLE_TYPE_weights[vvt]
    except Exception, e:
        print 'importance_modifier: exception', e
    return 0

def effort_modifier(victim, victim_vehicle, attacker_weapon, attacker_vehicle):
    try:
        if None in (victim_vehicle, attacker_vehicle):
            return 0

        victim_type = getVehicleType(victim_vehicle.templateName)
        attacker_type = getVehicleType(attacker_vehicle.templateName)

        if victim_type not in VEHICLE_TYPE_weights or attacker_type not in VEHICLE_TYPE_weights:
            return 0

        victim_weight = VEHICLE_TYPE_weights[victim_type]
        attacker_weight = VEHICLE_TYPE_weights[attacker_type]

        if g_debug: print 'effort_modifier: victim_weight =', victim_weight, '; attacker_weight =', attacker_weight

        if attacker_weight < victim_weight:
            if g_debug: print 'effort_modifier: giving',  victim_weight - attacker_weight, 'extra:', victim_vehicle.templateName, 'destroyed with a', attacker_vehicle.templateName
            return victim_weight - attacker_weight
        else:
            return 0
    except Exception, e:
        print 'effort_modifier: exception', e
    return 0
    
def score_modifier(victim, victim_vehicle, attacker_weapon, attacker_vehicle):
    return (importance_modifier(victim, victim_vehicle, attacker_weapon, attacker_vehicle) / 2) + \
           effort_modifier(victim, victim_vehicle, attacker_weapon, attacker_vehicle)

def init():

    # set limits for how many repair HPs etc are needed to get a callback
    bf2.gameLogic.setHealPointLimit(HEAL_POINT_LIMIT)
    bf2.gameLogic.setRepairPointLimit(REPAIR_POINT_LIMIT)
    bf2.gameLogic.setGiveAmmoPointLimit(GIVEAMMO_POINT_LIMIT)
    bf2.gameLogic.setTeamDamagePointLimit(TEAMDAMAGE_POINT_LIMIT)
    bf2.gameLogic.setTeamVehicleDamagePointLimit(TEAMVEHICLEDAMAGE_POINT_LIMIT)
    
    host.registerGameStatusHandler(onGameStatusChanged)
    
    if g_debug: print "scoring common init"



def onGameStatusChanged(status):
    if status == bf2.GameStatus.Playing:
        host.registerHandler('PlayerKilled', onPlayerKilled)
        host.registerHandler('PlayerDeath', onPlayerDeath)
        host.registerHandler('PlayerRevived', onPlayerRevived)
        host.registerHandler('PlayerHealPoint', onPlayerHealPoint)
        host.registerHandler('PlayerRepairPoint', onPlayerRepairPoint)
        host.registerHandler('PlayerGiveAmmoPoint', onPlayerGiveAmmoPoint)
        host.registerHandler('PlayerTeamDamagePoint', onPlayerTeamDamagePoint)
        host.registerHandler('EnterVehicle', onEnterVehicle)
        host.registerHandler('ExitVehicle', onExitVehicle)
    
    elif status == bf2.GameStatus.EndGame:

        giveCommanderEndScore(bf2.playerManager.getCommander(1), bf2.gameLogic.getWinner())
        giveCommanderEndScore(bf2.playerManager.getCommander(2), bf2.gameLogic.getWinner())
        
        
            
# give commander score for every player score
def addScore(player, points, subScore = NORMAL, subPoints = -1):

    # commander doesnt get score for regular actions, only for pure commander tasks. he also gets punishing points.
    if not player.isCommander() or subScore == CMND or points < 0:
        player.score.score += points
        if subPoints == -1:
            subPoints = points
        
        # sub score
        if subScore == RPL:
            player.score.rplScore += subPoints
            player.stats.roleScore += subPoints
        if subScore == SKILL:
            player.score.skillScore += subPoints
            player.stats.killScore += subPoints
        if subScore == CMND:
            player.score.cmdScore += subPoints
            player.stats.commandScore += subPoints
        
    # commander score
    commander = bf2.playerManager.getCommander(player.getTeam())
    if commander != None and commander.isValid() and subScore != CMND and player != commander and points > 0:
        preScore = commander.score.score
        numPlayers = bf2.playerManager.getNumberOfAlivePlayersInTeam(commander.getTeam())
        if numPlayers > 0:
            commander.score.score += float(points) / numPlayers
            scoreGotten = commander.score.score - preScore
            if scoreGotten > 0:
                commander.score.cmdScore += scoreGotten



def giveCommanderEndScore(player, winningTeam):
    if player == None: return
    if player.getTeam() != winningTeam: return
    
    # double the commander score and add to regular score
    player.score.score = (player.score.score + player.score.fracScore - player.score.cmdScore) + player.score.cmdScore * 2
    player.score.cmdScore = player.score.cmdScore * 2
    


def onPlayerKilled(victim, attacker, weapon, assists, object):

    killedByEmptyVehicle = False
    countAssists = False
    
    # killed by unknown, no score
    if attacker == None:
        
        # check if killed by vehicle in motion
        if weapon == None and object != None:
            if hasattr(object, 'lastDrivingPlayerIndex'):
                attacker = bf2.playerManager.getPlayerByIndex(object.lastDrivingPlayerIndex)
                killedByEmptyVehicle = True


        if attacker == None:                
            if g_debug: print "No attacker found"
            pass
        
    victimVehicle = victim.getVehicle()
    
    attackerVehicle = object
    if attackerVehicle is None and attacker:
        attackerVehicle = attacker.getVehicle()

    # killed by remote controlled vehicle, no score awarded in this game
    if victimVehicle and victimVehicle.getIsRemoteControlled():
        pass
        
    # no attacker, killed by object
    elif attacker == None:
        pass
        
    # killed by self
    elif attacker == victim:

        # no suicides from own wreck
        if killedByEmptyVehicle and object.getIsWreck():
            return

        attacker.score.suicides += 1
        addScore(attacker, SCORE_SUICIDE, RPL)
        
    # killed by own team
    elif attacker.getTeam() == victim.getTeam():

        # no teamkills from own wreck
        if killedByEmptyVehicle and object.getIsWreck():
            return
        
        tk_pun = SCORE_TEAMKILL
        
        # ignore tks by ju52 against soldiers
        if victimVehicle and getVehicleType(victimVehicle.templateName) == VEHICLE_TYPE_SOLDIER and \
          attackerVehicle and attackerVehicle.templateName.lower() in ignoreTKsFromVehicles:
            tk_pun = 0
        
        # ignore some mine tks
        if victimVehicle and weapon and should_ignore_tk(victimVehicle.getPosition(), weapon):
            tk_pun = SCORE_TEAMKILL_MINE

        if tk_pun:
            attacker.score.TKs += 1
            attacker.stats.TKs += 1
            addScore(attacker, tk_pun, RPL)
        
        countAssists = True

    # killed by enemy
    else:
        attacker.score.kills += 1
        addScore(attacker, SCORE_KILL_BASE + score_modifier(victim, victimVehicle, weapon, attackerVehicle), SKILL)
        
        countAssists = True
        
        try:
            if getVehicleType(attackerVehicle.templateName) == VEHICLE_TYPE_ARTILLERY:
                if hasattr(attacker, 'artillerySpot') and \
                       attacker.artillerySpot is not None and \
                       attacker.artillerySpot.isValid() and \
                       hasattr(attacker.artillerySpot, 'spotter') and \
                       attacker.artillerySpot.spotter is not None and \
                       attacker.artillerySpot.spotter.isValid() and \
                       attacker.artillerySpot.spotter.isConnected() and attacker.index != attacker.artillerySpot.spotter.index:
                    assists = list(assists)
                    assists.append((attacker.artillerySpot.spotter, 1))
                    bf2.gameLogic.sendGameEvent(attacker.artillerySpot.spotter, 9, 1)
        except Exception, e:
            print 'artillery score failed:', e

    # kill assist
    if countAssists and victim:
            
        for a in assists:
            assister = a[0]
            assistType = a[1]
            
            if assister.getTeam() != victim.getTeam():
            
                mod = score_modifier(victim, victimVehicle, weapon, attackerVehicle) / 2
                if assister and attacker:
                    if assister.getSquadId() == attacker.getSquadId() and assister.getSquadId() != 0:
                        mod += SCORE_KILLASSIST_SQUAD
                # passenger
                if assistType == 0:
                    assister.score.passengerAssists += 1
                    addScore(assister, SCORE_KILLASSIST_PASSENGER + mod, RPL)
                # targeter
                elif assistType == 1:
                    assister.score.targetAssists += 1
                    addScore(assister, SCORE_KILLASSIST_TARGETER + mod, RPL)
                # damage
                elif assistType == 2:
                    assister.score.damageAssists += 1
                    addScore(assister, SCORE_KILLASSIST_DAMAGE + mod, RPL)
                # driver passenger
                elif assistType == 3:
                    assister.score.driverAssists += 1
                    addScore(assister, SCORE_KILLASSIST_DRIVER + mod, RPL)                
                else:
                    # unknown kill type
                    pass
            
def should_ignore_tk(where_killed, weapon):
    wt = getWeaponType(weapon.templateName)
    if wt not in (WEAPON_TYPE_ATMINE, WEAPON_TYPE_APMINE):
        return False
    for template in ('mineflag_gb_projectile', 'mineflag_projectile'):
        objs = bf2.objectManager.getObjectsOfTemplate(template)
        for obj in objs:
            if game.utilities.reasonableObject(obj):
                if game.utilities.vectorDistance(where_killed, obj.getPosition()) < IGNORE_MINEFLAG_DIST:
                    return True
    return False

def hasPilotKit(player):
    if not player.isAlive(): return False
    if player.getKit() is None: return False
    kt = getKitType(player.getKit().templateName)
    if kt == KIT_TYPE_PILOT:
        return True
    else:
        return False

def onPlayerDeath(victim, vehicle):
    victim.score.deaths += 1

def onPlayerRevived(victim, attacker):
    if attacker == None or victim == None or attacker.getTeam() != victim.getTeam():
        return
            
    attacker.score.revives += 1
    addScore(attacker, SCORE_REVIVE, RPL)
    
    bf2.gameLogic.sendGameEvent(attacker, 10, 4) #10 = Replenish, 4 = Revive
    
def onPlayerHealPoint(player, object):
    player.score.heals += 1
    addScore(player, 3, RPL)
    bf2.gameLogic.sendGameEvent(player, 10, 0)  # 10 = Replenish, 0 = Heal   
    giveDriverSpecialPoint(player)



def onPlayerRepairPoint(player, object):
    player.score.repairs += 1
    addScore(player, 2, RPL)
    bf2.gameLogic.sendGameEvent(player, 10, 1)  # 10 = Replenish, 1 = Repair
    giveDriverSpecialPoint(player)



def onPlayerGiveAmmoPoint(player, object):
    player.score.ammos += 1
    addScore(player, 1, RPL)
    bf2.gameLogic.sendGameEvent(player, 10, 2)  # 10 = Replenish, 2 = Ammo
    giveDriverSpecialPoint(player)



def giveDriverSpecialPoint(player):

    # special point given to driver, if someone in vehicle gets an abilitypoint
    vehicle = player.getVehicle()
    if vehicle:
        rootVehicle = getRootParent(vehicle)
        driver = rootVehicle.getOccupyingPlayers()[0]
    
        if driver != None and driver != player and driver.getVehicle() == rootVehicle:
            driver.score.driverSpecials += 1
            addScore(driver, 1, RPL)
            bf2.gameLogic.sendGameEvent(driver, 10, 3) #10 = Replenish, 3 = DriverAbility

    
    
def onPlayerTeamDamagePoint(player, object):
    vehicleType = getVehicleType(object.templateName)
    if object.isWreck(): return

    if vehicleType == VEHICLE_TYPE_SOLDIER:
        player.score.teamDamages += 1
        addScore(player, SCORE_TEAMDAMAGE, RPL)
    else:
        player.score.teamVehicleDamages += 1
        addScore(player, SCORE_TEAMVEHICLEDAMAGE, RPL)

class driver:
    def __init__(self):
        self.passengers = {}

def giveDriverPoint(driver, new_pos, old_pos):
    # Point for transporting teammates on battlefield
    dist = game.utilities.vectorDistance(new_pos, old_pos)
    if dist >= MIN_TAXI_DIST:
        addScore(driver, SCORE_TAXI, RPL)
        driver.stats.driverPoints += SCORE_TAXI
        bf2.gameLogic.sendGameEvent(driver, 10, 3) #10 = Replenish, 3 = DriverAbility
        
def onEnterVehicle(player, vehicle, free):
    if not (vehicle.isValid() and game.utilities.reasonableObject(vehicle)): return
    rootVehicle = getRootParent(vehicle)
    if getVehicleType(rootVehicle.templateName) in (VEHICLE_TYPE_TRANSPORT, VEHICLE_TYPE_APC):
        if vehicle == rootVehicle:
            # Player is driver
            player.driver = driver()
            for p in vehicle.getOccupyingPlayers()[1:]:
                player.driver.passengers[p] = vehicle.getPosition()
        else:
            # Player is passenger
            driver_p = rootVehicle.getOccupyingPlayers()[0]
            if not hasattr(driver_p, 'driver'):
                # Driver seat seems to be empty
                # print 'scoringCommon exception: found driver player without driver attribute!'
                return
            driver_p.driver.passengers[player] = rootVehicle.getPosition()

def onExitVehicle(player, vehicle):
    if not (vehicle.isValid() and game.utilities.reasonableObject(vehicle)): return
    rootVehicle = getRootParent(vehicle)
    if getVehicleType(rootVehicle.templateName) in (VEHICLE_TYPE_TRANSPORT, VEHICLE_TYPE_APC) and player.isAlive():
        pos = rootVehicle.getPosition()
        if hasattr(player, 'driver') and vehicle == rootVehicle:
            for p, old_pos in player.driver.passengers.items():
                giveDriverPoint(player, pos, old_pos)
                player.driver = None
                del player.driver
        else:
            driver_p = rootVehicle.getOccupyingPlayers()[0]
            if not hasattr(driver_p, 'driver'):
                # Driver seat seems to be empty
                # print 'scoringCommon exception: found driver player without driver attribute!'
                return
            if player not in driver_p.driver.passengers.keys():
                # Probably driver exited first, do nothing
                # print 'scoringCommon exception: found passenger not listed in driver object!'
                return
            giveDriverPoint(driver_p, pos, driver_p.driver.passengers[player])
            del driver_p.driver.passengers[player]
    elif getVehicleType(rootVehicle.templateName) in (VEHICLE_TYPE_TRANSPORT, VEHICLE_TYPE_APC) and not player.isAlive():
        # Player was killed, reset stats
        if hasattr(player, 'driver'):
            del player.driver
