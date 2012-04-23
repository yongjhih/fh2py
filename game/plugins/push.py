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
# push.py -- push mode
#
#  ©2007 Joseph Birr-Pixton aka ctz for Forgotten Hope
import bf2, host, bf2.Timer, random
from game.gameplayPlugin import base
import game.utilities

g_daemon = None
DEBUG = 0

MARKER_YES = 'push_attackable'
MARKER_NO = 'push_locked'
MARKER_ARROW = 'push_arrow'
MARKER_YES_NORECAP = 'push_attackable_norecap'
TIMER_INTERVAL = 20

class pushDaemon:
    def __init__(self):
        self.links = []
        self.hooker = None
        self.timer = None
        self.time = TIMER_INTERVAL
    
    def add(self, l):
        self.links.append(l)
        if DEBUG: print 'push: added link', l
        if self.timer is None:
            self.timer = bf2.Timer(self.interval, 1, 1)
            self.timer.setRecurring(self.time)
        return len(self.links)
    
    def remove(self, r):
        if r in self.links:
            self.links.remove(r)
        else:
            if DEBUG: print 'push:', r, 'not found in', self.links
        if len(self.links) == 0 and self.timer:
            self.timer.destroy()
            self.timer = None
    
    def update_markers(self):
        # each CP wants zero or one marker. so we build a dict to
        # uniquify the cp->marker relationship.
        markers = {}
        
        for l in self.links:
            # is this link satisified?
            if l.satisfied():
                # yes!
                if l.force and (l.count == 1 or self.team_can_capture(l.target, l.attacker)):
                    markers[l.target] = l.get_target_marker()
                if not l.force and l.target not in markers:
                    markers[l.target] = l.get_target_marker()
                if l.source not in markers and l.wants_source_marker:
                    markers[l.source] = l.get_source_marker()
            else:
                # no!
                if not l.force:
                    markers[l.target] = MARKER_NO
                if l.force and l.target not in markers:
                    markers[l.target] = MARKER_NO
                if l.source not in markers and l.wants_source_marker:
                    markers[l.source] = l.get_source_marker()
            if not l.satisfied_defense() and l.wants_source_marker:
                markers[l.source] = MARKER_NO
            if l.force and l.wants_source_marker and int(l.source.cp_getParam('team')) in (l.defender, 0) and int(l.target.cp_getParam('team')) in (l.attacker, 0) and self.team_can_capture(l.source, l.attacker):
                markers[l.source] = MARKER_YES_NORECAP
        
        # now make the markers
        for cp, marker in markers.items():
            if DEBUG: print 'creating a', marker, 'on', cp.templateName
            game.utilities.createObject(marker, cp.getPosition())
        
        # and now the arrows. these go on satisfied links to cappable CPs
        for l in self.links:
            if l.satisfied() and l.wants_arrow and l.target in markers and markers[l.target] in (MARKER_YES, MARKER_YES_NORECAP):
                if DEBUG: print 'creating a', MARKER_ARROW, 'between', l.source.templateName, 'and', l.target.templateName
                rot = [l.vector_angle(), 0.0, 0.0]
                game.utilities.createObject(MARKER_ARROW, l.equidistant(), rot = rot)
                
    def interval(self, userdata):
        try:
            self.update_markers()
        except Exception, e:
            print 'update_markers failed:', e
    
    def find_attacker_links(self, cp, team):
        out = []
        count = 1
        for x in self.links:
            if x.attacker == team and x.target.templateName.lower() == cp.templateName.lower():
                if x.count > count:
                    count = x.count
                out.append(x)
        return out, count
    
    def find_defender_links(self, cp, team):
        out = []
        for x in self.links:
            if x.defender == team and x.source.templateName.lower() == cp.templateName.lower():
                out.append(x)
        return out
    
    def team_can_capture(self, cp, team):
        # they can only capture if all source flags belong to them (with exceptions for 'force' links)
        links, count = self.find_attacker_links(cp, team)
        a = 0
        b = 0
        c = 0
        if DEBUG: print 'attacker links', links
        for l in links:
            a += 1
            if not l.satisfied() and not l.force:
                if DEBUG: print 'team', team, 'cannot capture', cp.templateName, 'because link', l, 'is not satisfied'
                return False
            elif l.satisfied() and l.force:
                b += 1
                c += 1
                if c >= count:
                    return True
            elif not l.satisfied() and l.force:
                b += 1
            else:
                if DEBUG: print 'team', team, 'have satisfied', l
        # Do not allow to capture if all links are unsatisfied force.
        if a != 0 and b!= 0 and a == b:
            return False
        links = self.find_defender_links(cp, team)
        if DEBUG: print 'defender links', links
        for l in links:
            if not l.satisfied_defense():
                if DEBUG: print 'team', team, 'cannot capture', cp.templateName, 'because link', l, 'is not defended'
                return False
            else:
                if DEBUG: print 'team', team, 'have defended', l
        return True
    
    def veto_capture(self, cp, team):
        return not self.team_can_capture(cp, team)
    
class link:
    def __init__(self, source, target, attacker, display_arrow, wants_source_marker, force, count):
        self.source = game.utilities.getNamedCP(source)
        self.target = game.utilities.getNamedCP(target)
        self.attacker = attacker
        self.defender = [0, 2, 1][attacker]
        self.ok = True
        self.wants_source_marker = wants_source_marker
        self.wants_arrow = display_arrow
        self.can_recap_target = True
        self.source_takeable_by = 0
        self.force = force
        self.count = count
        if self.source is None:
            print 'push: source CP', source, 'does not exist!'
            self.ok = False
        if self.target is None:
            print 'push: target CP', target, 'does not exist!'
            self.ok = False
        
        game.utilities.activeSafe('ControlPoint', self.source.templateName)
        if int(game.utilities.templateProperty('unableToChangeTeam')) == 1:
            self.wants_source_marker = False
        self.source_takeable_by = int(game.utilities.templateProperty('onlyTakeableByTeam'))
        
        game.utilities.activeSafe('ControlPoint', self.target.templateName)
        if int(game.utilities.templateProperty('onlyTakeableByTeam')) != 0:
            self.can_recap_target = False
    
    def get_source_marker(self):
        if self.source_takeable_by == 0:
            return MARKER_YES
        else:
            if int(self.source.cp_getParam('team')) == self.source_takeable_by:
                return MARKER_NO
            else:
                return MARKER_YES_NORECAP
    
    def get_target_marker(self):
        if self.can_recap_target:
            return MARKER_YES
        else:
            if self.target.cp_getParam('team') == self.attacker:
                return MARKER_NO
            else:
                return MARKER_YES_NORECAP
        
    def __repr__(self): return str(self)
    def __str__(self):
        if not self.ok: return 'pushlink: bad'
        return 'pushlink: %s -> %s for team %d'%(self.source.templateName, self.target.templateName, self.attacker)
    def satisfied(self):
        return int(self.source.cp_getParam('team')) == self.attacker
    def satisfied_defense(self):
        return int(self.target.cp_getParam('team')) == self.defender
    def equidistant(self):
        u = self.source.getPosition()
        v = self.target.getPosition()
        return [(a + b) / 2.0 for a, b in zip(u, v)]
    
    def vector_angle(self):
        u = self.source.getPosition()
        v = self.target.getPosition()
        return game.utilities.vectorAngle((u[0], u[2]), (v[0], v[2]))

class push(base):
    def __init__(self, source, target, attacker, display_arrow = True, wants_source_marker = True, force = False, count = 1):
        attacker = int(attacker)
        self.links = []
        if type(source) == type(''):
            self.links.append(link(source, target, attacker, display_arrow, wants_source_marker, force, count))
        else:
            for s in source:
                self.links.append(link(s, target, attacker, display_arrow, wants_source_marker, force, count))
        
    def round_start(self, hooker):
        global g_daemon
        
        for link in self.links:
            if not link.ok:
                return
            
            if g_daemon is None:
                g_daemon = pushDaemon()
            g_daemon.hooker = hooker
            if g_daemon.add(link) == 1:
                self.wants_veto = True # first push wants veto
                print self, 'wants veto'
    
    def round_end(self, hooker):
        global g_daemon
        for link in self.links:
            if g_daemon is not None:
                g_daemon.remove(link)
    
    def veto_capture(self, hooker, cp, team, n_players):
        try:
            return g_daemon.veto_capture(cp, team)
        except Exception, e:
            print 'daemon.veto_capture failed:', e
