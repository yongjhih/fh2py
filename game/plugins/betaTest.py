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
# betaTest.py -- allows certain people to execute unfair/administrative commands
#
#  ©2007 Joseph Birr-Pixton aka ctz for Forgotten Hope
import bf2, host, bf2.Timer, random, fnmatch
from game.gameplayPlugin import base
import game.utilities

allow_globs = ('*lightning*', '*ctz*', '*toddel*', '*lobo*', '*knoff*', '*bob_sacamano*', '*fenring*', '*natty*', '*beregil*', '*cheese*', '*otolikos*', '*bizness*', '*kev4000*', '*spit*')
rcon = game.utilities.rconExec

class betaTest(base):    
    def is_allowed(self, name):
        name = name.lower()
        for g in allow_globs:
            if fnmatch.fnmatchcase(name, g):
                return True
        return False
    
    def onchat(self, id, text, channel, flags):
        try:
            self._onchat(id, text, channel, flags)
        except Exception, e:
            print 'onchat exception', e
    
    def _onchat(self, id, text, channel, flags):
        if id == -1: id = 255
        player = bf2.playerManager.getPlayerByIndex(id)
        if player is None or not player.isValid(): return
        
        for x in ('HUD_CHAT_DEADPREFIX', 'HUD_TEXT_CHAT_TEAM', 'HUD_TEXT_CHAT_SQUAD'):
            text = text.replace(x, '')
        
        if text[0] == '!':
            if not self.is_allowed(player.getName()):
                rcon('game.sayAll "betaTest: %s is not authorised"'%(player.getName()))
                return
            text = text[1:].strip()
            print player.getName(), 'executing', text
            if text.startswith('startdemo '):
                demoname = text[len('startdemo '):]
                print 'starting demo', demoname
                rcon('demo.stopRecording')
                rcon('demo.recordDemo "%s"'%demoname)
                rcon('game.sayAll "betaTest: Started recording demo \'%s\'..."'%demoname)
            elif text.startswith('stopdemo'):
                rcon('demo.stopRecording')
                rcon('game.sayAll "betaTest: Stopped recording."')
            elif text.startswith('restart'):
                rcon('game.sayAll "betaTest: Restarting map..."')
                rcon('admin.restartMap')
            elif text.startswith('finish '):
                bits = text.split()
                team = int(bits[-1])
                rcon('game.sayAll "betaTest: Racing tickets for team %d..."'%team)
                bf2.gameLogic.setTicketChangePerSecond(team, -100)
            elif text.startswith('switch '):
                bits = text.split()
                if len(bits) not in (3,4):
                    rcon('game.sayAll "betaTest: Error: \'%s\' is not a valid switch command (usage: switch Map_Name 16 [gpm_cq])"'%text)
                    return
                if len(bits) == 3:
                    verb, mapname, nplayers = bits
                    gamemode = 'gpm_cq'
                else:
                    verb, mapname, nplayers, gamemode = bits
                    
                rcon('game.sayAll "betaTest: Attempting to switch to \'%s\' %s players [%s]..."'%(mapname, nplayers, gamemode))
                worked = int(rcon('maplist.append %s %s %s'%(mapname, gamemode, nplayers)))
                if worked == 0:
                    rcon('game.sayAll "betaTest: Map \'%s\' unknown."'%(mapname))
                    return
                maplist = game.utilities.getMapList()
                id = 0
                for m in maplist:
                    if m[0].lower() == mapname and m[1].lower() == gamemode and int(m[2]) == int(nplayers):
                        break
                    id += 1
                if id > len(maplist): return
                rcon('admin.nextLevel %d'%id)
                rcon('admin.runNextLevel')
                rcon('game.sayAll "betaTest: Switching \'%s\' %s players now!"'%(mapname, nplayers))
            elif text.startswith('writesounds'):
                f = open('audiotweak.con', 'w')
                templates = [x.strip() for x in rcon('sound.getAllSoundTemplates').split('\n')]
                print repr(templates)
                print >>f, 'rem generated automatically by betatest.py'
                for x in templates:
                    print >>f, 'sound.tweakTemplate', x, '1.000 1.000 1.200 1.450 1.000 1.000'
            elif text.startswith('serversettings'):
                rcon('game.sayAll "betaTest: Resetting server settings and restarting map..."')
                rcon('sv.mandowntime 1')
                rcon('sv.spawntime 15')
                rcon('sv.ticketRatio 200')
                rcon('sv.tkPunishEnabled 0')
                rcon('sv.tkNumPunishToKick 1000')
                rcon('sv.autoBalanceTeam 0')
                rcon('sv.allowfreecam 1')
                rcon('admin.restartMap')
            elif text.startswith('exec '):
                text = text[5:]
                out = rcon(text)
                game.utilities.sayAll("result: '%s'"%out)
            elif text.startswith('camera'):
                if player.getVehicle():
                    pos = list(player.getVehicle().getPosition())
                    pos[0] += 1.0
                    pos[1] += 1.0
                    game.utilities.instantiateObject('filmcamera', pos, (0.0, 0.0, 0.0), team = player.getTeam())
            elif text.startswith('cpteam'):
                args = text.split()
                if len(args) != 3:
                    rcon('game.sayAll "betaTest: cpteam usage: cpteam team cp_name"')
                    return
                cp = game.utilities.getNamedCP(args[2])
                if cp:
                    game.utilities.cp_setTeam(cp, int(args[1]))
                    rcon('game.sayAll "betaTest: set %s to team %s"' % (cp.templateName, args[1]))
                else:
                    rcon('game.sayAll "betaTest: CP not found!"')
            else:
                rcon('game.sayAll "betaTest: Bad command \'%s\'!"'%(text))
                
    def round_start(self, hooker):
        hooker.register('ChatMessage', self.onchat)