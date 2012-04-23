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
# fragalyzer.py -- fragalyzer log file generator. 
# 
# this is ©2005 DICE, modifications ©2008 FHMOD

try:
    import host
    import bf2.PlayerManager
    import bf2.GameLogic
    import fpformat, datetime, time

    from game.stats.constants import *
    from bf2 import g_debug
    from game.gameplayPlugin import base
except Exception, e:
    print 'failed on imports', e

class faStat:
    def __init__(self):
        self.enterAt = 0
        self.enterTemplate = None
        self.spawnAt = 0
        
    def copyStats(self, player):
        self.damageAssists = player.score.damageAssists
        self.passengerAssists = player.score.passengerAssists
        self.targetAssists = player.score.targetAssists
        self.revives = player.score.revives
        self.teamDamages = player.score.teamDamages
        self.teamVehicleDamages = player.score.teamVehicleDamages
        self.cpCaptures = player.score.cpCaptures
        self.cpDefends = player.score.cpDefends
        self.cpAssists = player.score.cpAssists
        self.cpNeutralizes = player.score.cpNeutralizes
        self.cpNeutralizeAssists = player.score.cpNeutralizeAssists
        self.suicides = player.score.suicides
        self.kills = player.score.kills
        self.TKs = player.score.TKs

    def getChangedStats(self, player):
        res = []
        if player.score.cpCaptures > self.cpCaptures:
            res += ["cpCaptures"]
        if player.score.cpDefends > self.cpDefends:
            res += ["cpDefends"]
        if player.score.cpAssists > self.cpAssists:
            res += ["cpAssists"]
        if player.score.cpNeutralizes > self.cpNeutralizes:
            res += ["cpNeutralizes"]
        if player.score.cpNeutralizeAssists > self.cpNeutralizeAssists:
            res += ["cpNeutralizeAssists"]
        if player.score.suicides > self.suicides:
            res += ["suicides"]
        if player.score.kills > self.kills:
            res += ["kills"]
        if player.score.TKs > self.TKs:
            res += ["TKs"]
        if player.score.damageAssists > self.damageAssists:
            res += ["damageAssists"]
        if player.score.passengerAssists > self.passengerAssists:
            res += ["passengerAssists"]
        if player.score.targetAssists > self.targetAssists:
            res += ["targetAssists"]
        if player.score.revives > self.revives:
            res += ["revives"]
        if player.score.teamDamages > self.teamDamages:
            res += ["teamDamages"]
        if player.score.teamVehicleDamages > self.teamVehicleDamages:
            res += ["teamVehicleDamages"]
        
        return res

class fragalyzer(base):
    def __init__(self):
        self.logfile = None
        self.fileName = ""
        self.startTime = None
    
    def round_start(self, hooker):
        if host.sgl_getIsAIGame():
            return
    
        # register events
        hooker.register('PlayerKilled', self.onPlayerKilled)
        hooker.register('PlayerDeath', self.onPlayerDeath)
        hooker.register('EnterVehicle', self.onEnterVehicle)
        hooker.register('ExitVehicle', self.onExitVehicle)
        hooker.register('PickupKit', self.onPickupKit)
        hooker.register('DropKit', self.onDropKit)
        hooker.register('ControlPointChangedOwner', self.onCPStatusChange)
        hooker.register('PlayerScore', self.onPlayerScore)
        hooker.register('PlayerSpawn', self.onPlayerSpawn)
        hooker.register('PlayerConnect', self.onPlayerConnect)

        currentDate = datetime.datetime.today()
        dateString = ""
        dateString = time.strftime("%y%m%d_%H%M", currentDate.timetuple())

        if dateString != "":
            fileName = bf2.gameLogic.getModDir() + "/logs/" + bf2.gameLogic.getMapName() + "_" + dateString + "_faLog.txt"
        else:
            fileName = bf2.gameLogic.getModDir() + "/logs/" + bf2.gameLogic.getMapName() + "_faLog.txt"

        print "log file: ", fileName

        try:
            self.logfile = file (fileName, 'w')
        except Exception:
            print "Couldnt open fragalyzer self.logfile: ", fileName
            return

        self.startTime = int(self.date())
        timeString = str(self.startTime)
        startDate = time.strftime("%Y.%m.%d,%H:%M", currentDate.timetuple())
        if self.logfile: self.logfile.write("INIT LevelName=" + bf2.gameLogic.getMapName() + " self.startTime=" + timeString + " StartDate=" + startDate + " Filename=" + fileName + "\n")

        if self.logfile: self.logfile.flush()
        print "Fragalyzer logging enabled."

        # Connect already connected players if reinitializing
        for p in bf2.playerManager.getPlayers():
            self.onPlayerConnect(p)
    
    def round_end(self, hooker):
        self.disable()

    def onPlayerConnect(self, player):
        player.fa = faStat()    
        player.fa.enterAt = self.date()
        if player.isAlive():
            player.fa.spawnAt = self.date()
        vehicle = player.getVehicle()
        self.onEnterVehicle(player, vehicle)
        kit = player.getKit()
        if kit:
            self.onPickupKit(player, kit)
        
        player.fa.copyStats(player)
    
    def disable(self):
        if self.logfile:
            timeString = str(int(self.date()))
            if self.logfile: self.logfile.write("DISABLE LevelName=" + bf2.gameLogic.getMapName() + " EndTime=" + timeString + "\n")
            if self.logfile: self.logfile.close()
            print "Fragalyzer logging disabled."
        else:
            print "Fragalyzer logging was already disabled."
    
    def getPosStr(self, orgPos):
        worldSize = bf2.gameLogic.getWorldSize();
        scale = [512.0 / worldSize[0], 1, 512.0 / worldSize[1]]
        pos = [orgPos[0] * scale[0], orgPos[1] * scale[1], orgPos[2] * scale[2]]
        res = str(fpformat.fix(pos[0], 3)) + "," + str(fpformat.fix(pos[1], 3)) + "," + str(fpformat.fix(pos[2], 3))
        return res
    
    def date(self):
        return host.timer_getWallTime()
    
    def wallString(self):
        return str(int(host.timer_getWallTime()) - self.startTime)
    
    def onEnterVehicle(self, player, vehicle, freeSoldier = False):
        if player == None: return
        rootVehicle = getRootParent(vehicle)
        if rootVehicle.templateName == 'MultiPlayerFreeCamera':
            return

        vehicleType = getVehicleType(rootVehicle.templateName)

        if vehicleType == VEHICLE_TYPE_SOLDIER:
            pass
        else:
            timeString = self.wallString()
            playerTeam = str(player.getTeam())
            if self.logfile: self.logfile.write("ENTER PlayerName=" + player.getName() + " PlayerTeam=" + playerTeam + " VehicleName=" + rootVehicle.templateName + " Time=" + timeString + "\n")
            player.fa.enterAt = self.date()
            player.fa.enterTemplate = rootVehicle.templateName


        if self.logfile: self.logfile.flush()
        return
    
    def onPlayerSpawn(self, player, soldier):
        pass
    
    def onExitVehicle(self, player, vehicle):
        if player == None: return
        rootVehicle = getRootParent(vehicle)
        vehicleType = getVehicleType(rootVehicle.templateName)
        playerTeam = str(player.getTeam())

        if vehicleType == VEHICLE_TYPE_SOLDIER:
            pass
        else:
            timeInVehicle = 0
            if player.fa.enterTemplate == rootVehicle.templateName:
                timeInVehicle = self.date() - player.fa.enterAt
            timeString = self.wallString()
            if self.logfile: self.logfile.write("EXIT PlayerName=" + player.getName() + " PlayerTeam=" + playerTeam + " VehicleName=" + rootVehicle.templateName + " VehicleTime="\
             + str(fpformat.fix(timeInVehicle, 1)) + " Time=" + timeString + "\n")

        player.fa.enterAt = 0

        if self.logfile: self.logfile.flush()
        return
    
    def onPickupKit(self, player, kit):
        timeString = self.wallString()
        playerSpawnTimePickupDiff = str(int(self.date())-int(player.stats.spawnedAt))
        playerTeam = str(player.getTeam())
        if self.logfile: self.logfile.write("PICKUPKIT PlayerName=" + player.getName() + " PlayerTeam=" + playerTeam + " PlayerKit=" + kit.templateName + " PickupSpawnDiff=" + playerSpawnTimePickupDiff + " Time=" + timeString + "\n")
        player.fa.spawnAt = self.date()
        player.lastKitTemplateName = kit.templateName
        if self.logfile: self.logfile.flush()
    
    def onDropKit(self, player, kit):
        timeInVehicle = 0
        if player.fa.spawnAt != 0:
            timeInVehicle = self.date() - player.fa.spawnAt 
        timeString = self.wallString()
        playerTeam = str(player.getTeam())
        if self.logfile: self.logfile.write("DROPKIT PlayerName=" + player.getName() + " PlayerTeam=" + playerTeam + " PlayerKit=" + kit.templateName + " PlayerKitTime=" + str(fpformat.fix(timeInVehicle, 1)) + " Time=" + timeString + "\n")
        if self.logfile: self.logfile.flush()
        return
    
    def onPlayerKilled(self, victim, attacker, weapon, assists, object):
        victimKitName = victim.lastKitTemplateName
        victimVehicle = victim.getVehicle()
        victimRootVehicle = getRootParent(victimVehicle)
        victimVehicleType = getVehicleType(victimRootVehicle.templateName)
        victimName = victim.getName()
        victimTeam = str(victim.getTeam())
        
        if attacker:
            attackerKitName = attacker.lastKitTemplateName  
            attackerVehicle = attacker.getVehicle()
            attackerRootVehicle = getRootParent(attackerVehicle)
            attackerVehicleType = getVehicleType(attackerRootVehicle.templateName)
            attackerName = attacker.getName()
            attackerTeam = str(attacker.getTeam())
        else:
            attackerKitName = None
            attackerVehicle = None
            attackerRootVehicle = None
            attackerVehicleType = VEHICLE_TYPE_UNKNOWN
        
        if self.logfile: self.logfile.write("KILL")
        if attacker:
            if self.logfile: self.logfile.write(" AttackerName=" + attackerName + " AttackerTeam=" + attackerTeam + " AttackerPos=" + self.getPosStr(attackerVehicle.getPosition()))
        if victimVehicle != None:
            if self.logfile: self.logfile.write(" VictimName=" + victimName + " VictimTeam=" + victimTeam + " VictimPos=" + self.getPosStr(victimVehicle.getPosition()))
            if victimKitName != None:
                if self.logfile: self.logfile.write(" VictimKit=" + victimKitName)
            if victimVehicle != None and (attackerVehicleType != VEHICLE_TYPE_SOLDIER):
                if self.logfile: self.logfile.write(" VictimVehicle=" + victimRootVehicle.templateName)
        
        if attackerKitName != None:
            if self.logfile: self.logfile.write(" AttackerKit=" + attackerKitName)
        if attackerVehicle != None and (attackerVehicleType != VEHICLE_TYPE_SOLDIER):
            if self.logfile: self.logfile.write(" AttackerVehicle=" + attackerRootVehicle.templateName)
        
        if weapon != None:
            if self.logfile: self.logfile.write(" AttackerWeapon=" + weapon.templateName)
        
        timeString = self.wallString()   
        if self.logfile: self.logfile.write(" Time=" + timeString + "\n")
        if self.logfile: self.logfile.flush()
    
    def onPlayerDeath(self, victim, vehicle):
        # dump accuracy stats on death (can't invoke on each shot being fired)
        tempFireMap = {}
        bulletsHit = victim.score.bulletsGivingDamage
        for b in bulletsHit:
            templateName = b[0]
            nr = b[1]
            tempFireMap[templateName] = nr

        bulletsFired = victim.score.bulletsFired
        if g_debug: print "bf: ", len(bulletsFired)
        for b in bulletsFired:
            templateName = b[0]
            fired = b[1]
            hits = 0
            if templateName in tempFireMap:
                hits = tempFireMap[templateName]
            timeString = self.wallString()
            if self.logfile: self.logfile.write("FIRED PlayerName=" + victim.getName() + " Weapon=" + templateName + " ShotsFired=" + str(fired) + " ShotsHit=" + str(hits) + " Time=" + timeString + "\n")

        if self.logfile: self.logfile.flush()
    
    def onCPStatusChange(self, cp, attackingTeam):
        position = cp.getPosition()
        if (cp.cp_getParam('team') == 0):
            captureType = "team"
        else:
            if attackingTeam == 0:
                return
            captureType = "neutral"

        timeString = self.wallString()
        if self.logfile: self.logfile.write("CAPTURE ControlPointID=" + cp.getTemplateProperty('controlPointId') + " CaptureType=" + captureType\
         + " CaptureTeam=" + str(attackingTeam) + " CapturePointPos=" + self.getPosStr(cp.getPosition()) + " Time=" + timeString + "\n")

        if self.logfile: self.logfile.flush()
    
    def onPlayerScore(self, player, difference):
        if player != None:
            playerKitName = player.lastKitTemplateName
            playerVeh = player.getVehicle()
            playerRootVeh = getRootParent(playerVeh)
            playerVehName = playerRootVeh.templateName
            playerVehType = getVehicleType(playerRootVeh.templateName)
            timeString = self.wallString()

            # figure out score type
            scoreTypeList = player.fa.getChangedStats(player)
            player.fa.copyStats(player)
            if len(scoreTypeList):
                scoreType = scoreTypeList[0]
            else:
                scoreType = "Unknown"

            if self.logfile: self.logfile.write("SCORE ScoreDiff=" + str(difference) + " PlayerName=" + player.getName() + " PlayerTeam=" + str(player.getTeam()) + " PlayerKit=" + playerKitName)
            if (playerVeh != None) and (playerVehType != VEHICLE_TYPE_SOLDIER):
                if self.logfile: self.logfile.write(" PlayerVehicle=" + playerVehName)
            if self.logfile: self.logfile.write(" PlayerPos=" + self.getPosStr(playerVeh.getPosition()) + " Time=" + timeString + " Scoretype=" + scoreType + "\n")

        if self.logfile: self.logfile.flush()
