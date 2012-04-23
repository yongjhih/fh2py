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
# gameplayPlugin.py -- a nice framework for map-specific gameplay modification
#  ©2006 Joseph Birr-Pixton aka ctz for Forgotten Hope

import game.perMapData
import game.utilities
import bf2, host, sys

# for release
standard = 'tankDisable aiFixups limitKitNCO artillery commanderChair artilleryReload parachute awards deployables spawnwave NCOrifle'.split()

# for betatest
#standard = 'tankDisable aiFixups limitKitNCO artillery commanderChair artilleryReload parachute awards deployables spawnwave NCOrifle betaTest'.split()

# for internal use ('testing' opens cameras up, 'ingameEditor' is the server portion of FH2-IGE, 'mapLint' checks various map settings then quits)
#standard = 'tankDisable aiFixups limitKitNCO artillery commanderChair artilleryReload parachute deployables spawnwave NCOrifle betaTest fragalyzer ingameEditor testing awards'.split()
#standard = 'tankDisable aiFixups limitKitNCO artillery commanderChair artilleryReload betaTest parachute deployables spawnwave NCOrifle ingameEditor testing mapLint'.split()

DEFAULT_TICKET_LOSS_PER_MIN = 10
TICKET_LOSS_PER_MIN_1 = DEFAULT_TICKET_LOSS_PER_MIN
TICKET_LOSS_PER_MIN_2 = DEFAULT_TICKET_LOSS_PER_MIN

def setDefaultTicketLossPerMin(team, n):
    if team == 1:
        global TICKET_LOSS_PER_MIN_1
        TICKET_LOSS_PER_MIN_1 = n
    elif team == 2:
        global TICKET_LOSS_PER_MIN_2
        TICKET_LOSS_PER_MIN_2 = n
    else:
        print 'gameplayPlugin.py: setDefaultTicketLossPerMin called with wrong team as argument'

def getDefaultTicketLossPerMin(team):
    try:
        exec('tlpm = TICKET_LOSS_PER_MIN_%d' % team)
        return tlpm
    except:
        return DEFAULT_TICKET_LOSS_PER_MIN

class base(object):
    wants_veto = False
    def bf2_init(self, hooker):
        """
        Called everytime a gamemode is init'd.
        """
        pass
    
    def bf2_deinit(self, hooker):
        """
        As above, except deinit.
        """
        pass
    
    def round_start(self, hooker):
        """
        Called at the start of every round.
        """
        pass
    
    def round_end(self, hooker):
        """
        Called at the end of every round. And perhaps some other times.
        """
        pass
    
    def veto_capture(self, hooker, cp, team, n_players):
        """
        Called at each entry of a vehicle/soldier into a CP zone. Return True to veto capture.
        """
        return False

class later:
    def __init__(self, when, callable, args):
        self.timer = bf2.Timer(self.interval, when, 1)
        self.callable = callable
        self.args = args
    def interval(self, ignore = None):
        if self.timer is None: return
        try:
            self.callable(*self.args)
            self.abort()
        except Exception, e:
            print 'gameplayPlugin: exception in "later" handler', self.callable, '--', e
            sys.excepthook(*sys.exc_info())
    def __del__(self):
        if self.timer:
            self.timer.destroy()
            self.timer = None
    def abort(self):
        if self.timer:
            self.timer.destroy()
            self.timer = None

g_hooker = None
DEBUG_HOOKS = 0

class hookCaller:
    def __init__(self, hooker, type):
        self.hooker, self.type = hooker, type
        self.disabled = False
    
    def disable(self):
        self.disabled = True
        self.hooker = None
        self.type = None
    
    def __call__(self, *args):
        if not self.disabled:
            self.hooker.dispatch(self.type, *args)

class hookProxy:
    def __init__(self):
        self.hooks = {}
        self.registered = {}
        self.laters = []
        print 'gameplayPlugin: hookProxy hooked'
    
    def deregisterAll(self):
        self.hooks = {}
        for l in self.laters:
            l.abort()
        self.laters = []
        
        for hc in self.registered.values():
            hc.disable()
        self.registered = {}
    
    def hasHook(self, type, hook):
        hooks = self.hooks.get(type, [])
        return hook in hooks
    
    def register(self, type, hook):
        hooks = self.hooks.get(type, [])
        hooks.append(hook)
        self.hooks[type] = hooks
        if DEBUG_HOOKS: print 'hookProxy: registered', hook, 'type', type
        
        if type not in self.registered:
            if DEBUG_HOOKS: print 'hookProxy: registered handler for', type
            hc = hookCaller(self, type)
            host.registerHandler(type, hc, 1)
            self.registered[type] = hc
    
    def dispatch(self, type, *args):
        if DEBUG_HOOKS: print 'hookProxy: gameplayPlugin: dispatch for type', type, 'args:', repr(args)
        try:
            hooks = self.hooks.get(type, [])
            for h in hooks:
                try:
                    h(*args)
                except Exception, e:
                    print 'gameplayPlugin: exception in dispatch to', h, 'for type', type, ':', e
                    sys.excepthook(*sys.exc_info())
        except Exception, e:
            print 'gameplayPlugin: exception in dispatch for', type, ':', e
            sys.excepthook(*sys.exc_info())
    
    def later(self, when, callable, *args):
        self.laters.append(later(when, callable, args))
        if DEBUG_HOOKS: print 'gameplayPlugin: later registered: calling', callable, 'with', args, 'in', when, 'seconds'

class pluginsystem:
    def __init__(self):
        self.is_inited = False
        self.loaded_plugins = []
    
    def load_standard(self):
        try:
            import game.plugins
        except Exception, e:
            print 'gameplayPlugin: exception loading plugins', e
            sys.excepthook(*sys.exc_info())
        
        # load these before the others
        for ps in standard:
            try:
                print 'gameplayPlugin: loading', ps
                p = getattr(game.plugins, ps)
                self.loaded_plugins.append(p())
                print 'gameplayPlugin: loaded standard plugin', ps
            except Exception, e:
                print 'gameplayPlugin: exception loading standard plugin', ps + ':', e
                sys.excepthook(*sys.exc_info())
    
    def bf2_init(self):
        print 'gameplayPlugin: pluginsystem.bf2_init'
        global g_hooker
        if g_hooker is None: g_hooker = hookProxy()
        g_hooker.deregisterAll()
        try:
            import game.plugins
        except Exception, e:
            print 'gameplayPlugin: exception loading plugins', e
            sys.excepthook(*sys.exc_info())
        
        for x in self.loaded_plugins:
            try:
                x.round_end(g_hooker)
            except Exception, e:
                print 'gameplayPlugin: exception in plugin.round_end', x, e
                sys.excepthook(*sys.exc_info())
            try:
                x.bf2_deinit(g_hooker)
            except Exception, e:
                print 'gameplayPlugin: exception in plugin.bf2_deinit', x, e
                sys.excepthook(*sys.exc_info())
        
        self.loaded_plugins = []
        self.load_standard()
        self.is_inited = True
        
        try:
            d = game.perMapData.getMapData()
        except Exception, e:
            print 'gameplayPlugin: exception loading permapdata', e
            sys.excepthook(*sys.exc_info())
            return
            
        if d is not None:
            for p in d:
                print p
                if p[0].__name__ in dir(game.plugins):
                    try:
                        self.loaded_plugins.append(p[0](**p[1]))
                    except Exception, e:
                        print 'gameplayPlugin: exception creating plugin', p[0].__name__, repr(p[1]), e
                        sys.excepthook(*sys.exc_info())
                else:
                    print "gameplayPlugin: Something not inside game.plugins in a mapdata.py", p
                    continue
        print 'gameplayPlugin: loaded', len(self.loaded_plugins), 'plugins'
        for p in self.loaded_plugins:
            try:
                p.bf2_init(g_hooker)
            except Exception, e:
                print 'gameplayPlugin: exception in plugin.bf2_init', p, ':', e
                sys.excepthook(*sys.exc_info())
    
    def bf2_deinit(self):
        print 'gameplayPlugin: pluginsystem.bf2_deinit'
        for p in self.loaded_plugins:
            try:
                p.bf2_deinit(g_hooker)
            except Exception, e:
                print 'gameplayPlugin: exception in plugin.bf2_deinit', p, repr(p), ':', e
                sys.excepthook(*sys.exc_info())
        self.loaded_plugins = []
        g_hooker.deregisterAll()
    
    def round_start(self):
        print 'gameplayPlugin: pluginsystem.round_start'
        for p in self.loaded_plugins:
            try:
                p.round_start(g_hooker)
            except Exception, e:
                print 'gameplayPlugin: exception in plugin.round_start', p, repr(p), ':', e
                sys.excepthook(*sys.exc_info())
    
    def round_end(self):
        print 'gameplayPlugin: pluginsystem.round_end'
        for p in self.loaded_plugins:
            try:
                p.round_end(g_hooker)
            except Exception, e:
                print 'gameplayPlugin: exception in plugin.round_end', p, repr(p), ':', e
                sys.excepthook(*sys.exc_info())
        g_hooker.deregisterAll()
    
    def veto_capture(self, cp, team, n_players):
        for p in self.loaded_plugins:
            if not p.wants_veto: continue
            try:
                if p.veto_capture(g_hooker, cp, team, n_players):
                    return True
            except Exception, e:
                print 'gameplayPlugin: exception in plugin.veto_capture', p, repr(p), ':', e
                sys.excepthook(*sys.exc_info())
        return False
