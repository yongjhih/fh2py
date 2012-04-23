# Supplylines

try:
	import host
	import bf2
	import gpm_cq
	from bf2 import g_debug
except Error, e:
	print "imports failed " + str(e)

def init():
	# events hook
	try:
		host.registerGameStatusHandler(onGameStatusChanged)
		if host.sgl_getIsAIGame() == 1:
			host.sh_setEnableCommander(0)
		else:
			host.sh_setEnableCommander(1)

		if g_debug: print "gpm_sl.py initialized"
	except Error, e:
		print "init faield "+ str(e)
		

def onGameStatusChanged(status):
	if status == bf2.GameStatus.Playing:

		# control point triggers
		cps = bf2.objectManager.getObjectsOfType('dice.hfe.world.ObjectTemplate.ControlPoint')
		for obj in cps:
			radius = float(obj.getTemplateProperty('radius'))
			id = bf2.triggerManager.createRadiusTrigger(obj, onCPTrigger, '<<PCO>>', radius, (1, 2, 3))
			obj.triggerId = id
			
		host.registerHandler('ControlPointChangedOwner', onCPStatusChange)

		# setup ticket system
		ticketsTeam1 = gpm_cq.calcStartTickets(bf2.gameLogic.getDefaultTickets(1))
		ticketsTeam2 = gpm_cq.calcStartTickets(bf2.gameLogic.getDefaultTickets(2))
		
		bf2.gameLogic.setTickets(1, ticketsTeam1)
		bf2.gameLogic.setTickets(2, ticketsTeam2)
		
		bf2.gameLogic.setTicketState(1, 0)
		bf2.gameLogic.setTicketState(2, 0)

		bf2.gameLogic.setTicketLimit(1, 1, 0)
		bf2.gameLogic.setTicketLimit(2, 1, 0)

		bf2.gameLogic.setTicketLimit(1, 1, 0)
		bf2.gameLogic.setTicketLimit(2, 1, 0)
		bf2.gameLogic.setTicketLimit(1, 2, 10)
		bf2.gameLogic.setTicketLimit(2, 2, 10)
		bf2.gameLogic.setTicketLimit(1, 3, int(ticketsTeam1*0.1))
		bf2.gameLogic.setTicketLimit(2, 3, int(ticketsTeam2*0.1))
		bf2.gameLogic.setTicketLimit(1, 4, int(ticketsTeam1*0.2))
		bf2.gameLogic.setTicketLimit(2, 4, int(ticketsTeam1*0.2))
		
		host.registerHandler('TicketLimitReached', onTicketLimitReached)
		updateTicketLoss()

		host.registerHandler('TimeLimitReached', onTimeLimitReached)

		updateSupplyLines()
		
		if g_debug: print "Supplylines gamemode initialized."
	else:
		bf2.triggerManager.destroyAllTriggers()



def showControlGroups(): # temporary help function
	cps = bf2.objectManager.getObjectsOfType('dice.hfe.world.ObjectTemplate.ControlPoint')
	for obj in cps:
		# check this CP's required groups
		if g_debug: print "Checking cp %s: team=%d group=%d supplyteam1=%d supplyteam2=%d" % \
			(obj.templateName, cp.cp_getParam('team'), obj.getSupplyGroupId(), hasSupply(obj, 1), hasSupply(obj, 2))



def hasSupply(cp, team):
	if cp.cp_getParam('onlyTakeableByTeam') != 0 and cp.cp_getParam('onlyTakeableByTeam') != team:
		return False

	groupsNeeded = cp.cp_getParam('supplyGroupsNeeded', team)
	optionalSupply = 0
	for grp in groupsNeeded:
#		if g_debug: print "cp %s team %d needs supply from group %d" % (cp.templateName, team, grp[0])
		groupId = grp[0]
		optional = grp[1]
		if optional == True:
			if hasGroupUnderControl(team, groupId):
				optionalSupply += getSupplyValue(groupId)
		else:
			if hasGroupUnderControl(team, groupId) != True:
#				if g_debug: print "=> required group %d not under control." % (groupId)
				return False

	supplyNeeded = cp.cp_getParam('supplyValueNeeded', team)
		
	if optionalSupply < supplyNeeded:
		if g_debug: print "Not enough supply value (%d < %d)" % (optionalSupply, supplyNeeded)
		return False
	
	
	return True				

	
def hasGroupUnderControl (team, grp):
	
	# check this groups supply status
	cpsInGroup = host.sgl_getControlPointsInGroup(grp)
	
	for cp in cpsInGroup:
		if cp.cp_getParam('team') != team:
			return False
	
	return True

	
	
def updateSupplyLines():
	cps = bf2.objectManager.getObjectsOfType('dice.hfe.world.ObjectTemplate.ControlPoint')
	for obj in cps:

		# check this CP's required groups
		if hasSupply(obj, 1) == True:
			obj.cp_setParam('allowCaptureByTeam', 1, True)
			if obj.cp_getParam('team') != 1:
				if g_debug: print "Team 1 is now allowed to capture ", obj.templateName
		else:
			obj.cp_setParam('allowCaptureByTeam', 1, False)
					
		if hasSupply(obj, 2) == True:
			obj.cp_setParam('allowCaptureByTeam', 2, True)
			if obj.cp_getParam('team') != 2:
				if g_debug: print "Team 2 is now allowed to capture ", obj.templateName
		else:
			obj.cp_setParam('allowCaptureByTeam', 2, False)
		
					
def supplyLinesAllowTakeover(cp, team):
	if not cp.cp_getParam('allowCaptureByTeam', team):
		if g_debug: print "No supply to cp %s from team %d" % (cp.templateName, team)
		return False
				
	return True
				
		



# wrap gpm_cq as most logic is identical
	
def onTimeLimitReached(value):
	gpm_cq.onTimeLimitReached(value)

def updateTicketLoss():
	gpm_cq.updateTicketLoss()
	
def onTicketLimitReached(team, limitId):
	gpm_cq.onTicketLimitReached(team, limitId)

def onCPTrigger(triggerId, cp, vehicle, enter, userData):
	if not cp.isValid(): return

	team1Occupants = 0
	team2Occupants = 0

	pcos = bf2.triggerManager.getObjects(cp.triggerId)
	for o in pcos:
		for p in o.getOccupyingPlayers():
			if p.getTeam() == 1:
				team1Occupants += 1
			elif p.getTeam() == 2:
				team2Occupants += 1

	attackingTeam = 0
	team1OverWeight = team1Occupants - team2Occupants
	
	if team1OverWeight > 0 and cp.cp_getParam('team') != 1:
		attackingTeam = 1
	elif team1OverWeight < 0 and cp.cp_getParam('team') != 2:
		attackingTeam = 2
	
	if attackingTeam > 0:
		if not supplyLinesAllowTakeover(cp, attackingTeam):
			return
	
	if g_debug: print "Ok cp %s had supply. Attacking team=%d, cpteam=%d" % (cp.templateName, attackingTeam, cp.cp_getParam('team'))

	gpm_cq.onCPTrigger(triggerId, cp, vehicle, enter, userData)		


	
		
def onCPStatusChange(cp, attackingTeam):
	gpm_cq.onCPStatusChange(cp, attackingTeam)

	updateSupplyLines()
