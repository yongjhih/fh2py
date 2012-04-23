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
# utilities.py -- a bunch of utilities usable by lots of gamemodes
#  ©2006 Joseph Birr-Pixton aka ctz for Forgotten Hope
try:
    import bf2, host
except:
    pass # probably not running in bf2

import sys, math

# we have a hilariously broken python environment, so
# os.path doesn't work.
if sys.platform == 'win32':
    import ntpath as path
elif sys.platform == 'unknown':
    import posixpath as path

rconlog = None #open('bf2-python-rcon.log', 'w', 0)

def getMapList():
    maplist = host.rcon_invoke('maplist.list').strip()
    out = []
    for l in maplist.split('\n'):
        bits = l.split()
        if len(bits) == 3:
            idx, mapname, gamemode = bits
            size = '64'
        else:
            idx, mapname, gamemode, size = l.split()
        mapname = mapname[1:-1].lower()
        
        out.append([mapname, gamemode, size])
    return out

def getCurrentRound():
    """
    Returns a 3 tuple of map, gamemode, size (str, str, int).
    """
    maplist = getMapList()
    current = int(host.rcon_invoke('maplist.currentMap').strip())
    if current >= len(maplist):
        return ('unknown', 'gpm_cq', 16)
    return maplist[current]

def rconExec(cmd):
    """
    Calls host.rcon_invoke.
    """
    global rconlog
    if rconlog: print >>rconlog, '$', cmd
    out = host.rcon_invoke(cmd).strip()
    if len(out) > 0 and rconlog: print >>rconlog, out
    if 'Unauthorised' in out:
        if rconlog: print >>rconlog, '! Unauthorised; console.access is', host.rcon_invoke('console.access').strip()
        return ''
    return out

def sayAll(s):
    if '"' in s and "'" in s:
        print "wanted to sayall", s, "but can't"
        return
    if '"' in s:
        rconExec("game.sayall '%s'"%s)
    else:
        rconExec('game.sayall "%s"'%s)

def sayTeam(s,t):
    if '"' in s and "'" in s:
        print "wanted to sayteam", s, "but can't"
        return
    if '"' in s:
        rconExec("game.sayTeam %d '%s'"%(t,s))
    else:
        rconExec('game.sayTeam %d "%s"'%(t,s))

def active(t):
    rconExec('objecttemplate.active %s'%t)

def activeSafe(t, template):
    rconExec('objecttemplate.activesafe %s %s' % (t, template))

def isType(t):
    return t.lower() == rconExec('objecttemplate.type').lower()

def getType():
    return  rconExec('objecttemplate.type').lower()

def createObject(t, pos, rot = (0,0,0), team = 0, ttl = None):
    spawner = 'spw_' + t
    rconExec('ObjectTemplate.create ObjectSpawner %s' % spawner)
    rconExec('ObjectTemplate.activeSafe ObjectSpawner %s' % spawner)
    rconExec('ObjectTemplate.hasMobilePhysics 0')
    rconExec('ObjectTemplate.setObjectTemplate 0 %s' % t)
    rconExec('ObjectTemplate.setObjectTemplate 1 %s' % t)
    rconExec('ObjectTemplate.setObjectTemplate 2 %s' % t)
    if ttl:
        rconExec('ObjectTemplate.TimeToLive %d'%ttl)
    if team != 0:
        rconExec('ObjectTemplate.teamOnVehicle 1')
    instantiateSpawner(spawner, pos, rot, team)

def instantiateSpawner(spawner, pos, rot, team = 0):
    pos = '/'.join(map(str, pos))
    rot = '/'.join(map(str, rot))
    rconExec('Object.create %s' % spawner)
    rconExec('Object.absolutePosition %s' % pos)
    rconExec('Object.rotation %s' % rot)
    rconExec('Object.team %d' % team)
    rconExec('Object.delete')

def instantiateObject(template, pos, rot, team = 0):
    pos = '/'.join(map(str, pos))
    rot = '/'.join(map(str, rot))
    rconExec('gamelogic.createobject %s' % template)
    rconExec('Object.absolutePosition %s' % pos)
    rconExec('Object.rotation %s' % rot)
    rconExec('Object.team %d' % team)
    return rconExec('object.active')

def walkTemplate():
    all = rconExec('objecttemplate.listtemplates')
    if all == '': raise StopIteration
    for line in all.split('\n'):
        index, template = line.split()
        yield template

def templateProperty(p):
    return rconExec('objecttemplate.' + p)

def activeObject(id):
    rconExec('object.active id%d'%int(id))

def objectTransform(id):
    activeObject(id)
    pos = map(float, rconExec('object.absolutePosition').split('/'))
    rot = map(float, rconExec('object.rotation').split('/'))
    return pos, rot

def deleteObject(id):
    activeObject(id)
    rconExec('object.delete')

def sameTransform(x, y):
    return int(x[0]) == int(y[0]) and int(x[1]) == int(y[1]) and int(x[2]) == int(y[2])

def matmult(a, b):
    """does a * b, where a and b are both matrices, represented as lists of rows"""
    return [[sum([i*j for i, j in zip(row, col)]) for col in zip(*b)] for row in a]

def normalise(v, u):
    """convert the u world vector to be an offset with respect to v."""
    return (v[0] - u[0], v[1] - u[1], v[2] - u[2])
    
def denormalise(v, u):
    """convert the u local vector with respect to v to world system."""
    return (v[0] + u[0], v[1] + u[1], v[2] + u[2])

def rot_X(w):
    w = math.radians(w)
    return [[1.0,          0.0,         0.0],
            [0.0,          math.cos(w), -math.sin(w)],
            [0.0,          math.sin(w), math.cos(w)]]

def rot_Y(w):
    w = math.radians(w)
    return [[math.cos(w),  0.0,  math.sin(w)],
            [0.0,          1.0,  0.0],
            [-math.sin(w), 0.0,  math.cos(w)]]

def rot_Z(w):
    w = math.radians(w)
    return [[math.cos(w),  math.sin(w), 0.0],
            [-math.sin(w), math.cos(w), 0.0],
            [0.0,          0.0,         1.0]]

def rotateVector(rot, v):
    """transform the local vector v through rot[0] in X, rot[1] in Y and rot[2] in Z"""
    print 'rotateVector:', 'heading', rot[1], 'attitude', rot[2], 'bank', rot[0]
    print 'input', v
    if rot[1]: v = matmult([v], rot_Y(rot[1]))[0]
    print ' in y', v
    if rot[2]: v = matmult([v], rot_Z(rot[2]))[0]
    print ' in z', v
    if rot[0]: v = matmult([v], rot_X(rot[0]))[0]
    print ' in x', v
    return v

def reasonableObject(obj):
    return object is not None and not sameTransform(obj.getPosition(), (0, 0, 0))

def findAbsoluteRotation(obj, name):
    """
    Finds the rotation (in absolute terms) of the template 'name'
    under 'obj'.
    """
    thing = findSubObject(obj, name)
    if thing is None: return None
    rotation = list(thing.getRotation())
    parent = thing.getParent()
    while parent and parent != obj:
        parent_rotation = parent.getRotation()
        rotation[0] += parent_rotation[0]
        rotation[1] += parent_rotation[1]
        rotation[2] += parent_rotation[2]
        parent = parent.getParent()
    if parent == obj:
        parent_rotation = parent.getRotation()
        rotation[0] += parent_rotation[0]
        rotation[1] += parent_rotation[1]
        rotation[2] += parent_rotation[2]
    return rotation

def findSubObject(obj, name):
    name = name.lower()
    if obj.templateName.lower() == name: return obj
    for o in obj.getChildren():
        if o.templateName.lower() == name: return o
        f = findSubObject(o, name)
        if f: return f
    return None

def rootParent(obj):
    while obj.getParent() is not None:
        obj = obj.getParent()
    return obj

def printScriptTillItFuckingWorks():
    # crashes engine if run on certain templates
    if rconExec('objecttemplate.type') in ('Soldier', 'Kit'):
        raise ValueError, 'printscript not implemented for soldier/kit templates'
    s = ''
    while len(s) < 8 or not s.lower().startswith('objecttemplate.'):
        s = rconExec('objecttemplate.printscript')
    return s

def dump(obj, indent = ''):
    print indent, obj.templateName, obj.getPosition(), obj.getRotation()
    for o in obj.getChildren():
        dump(o, indent + '  ')

def listObjectsOfTemplate(template):
    """
    Generator returning ids from object.listObjectsOfTemplate for the
    given template.
    """
    out = rconExec('object.listObjectsOfTemplate ' + template)
    if out == '': raise StopIteration
    for l in out.split('\n'):
        parts = l.split()
        yield parts[3]

def getNamedCP(name):
    name = name.lower()
    cps = bf2.objectManager.getObjectsOfType('dice.hfe.world.ObjectTemplate.ControlPoint')
    for x in cps:
        if x.templateName.lower() == name:
            return x
    return None

def nrInSquad(team, squadid):
    players = bf2.playerManager.getPlayers()
    count = 0
    for p in players:
        if p.isValid() and p.getTeam() == team and p.getSquadId() == squadid:
            count += 1
    return count

def toDeg(rad):
    return math.degrees(rad)

def vectorAngle(u, v):
    try:
        ux, uy = u
        vx, vy = v
        dx = vx - ux
        dy = vy - uy
        if dx == 0.0 and dy == 0.0: return 0.0
        if dx < 0.0 and dy < 0.0:
            return toDeg(math.atan2(dx, dy))
        else:
            return 90.0 - toDeg(math.atan2(dy, dx))
    except Exception, e:
        print 'vectorAngle failed', e
        return 0.0

def vectorDistance(u, v):
    d = [math.fabs(a - b) for a, b in zip(u, v)]
    return math.sqrt(d[0] * d[0] + d[1] * d[1] + d[2] * d[2])

def vectorElevation(v):
    return math.degrees(math.atan(v[0] / v[1]))

def layFlat(r):
    return [r[0], 0, 0]

def xform(u, v):
    return [x + y for x, y in zip(u, v)]

gravity = 14.73

def gunRange(t, v, g):
    """
    t  -> elevation of fire
    v  -> muzzle velocity
    g  -> gravitymod
    """
    try:
        t, v, g = map(float, (t, v, g))
        t = math.radians(t)
        vh = v * math.cos(t)
        vv = v * math.sin(t)
        return (2 * vh * vv) / (gravity * g)
    except Exception, e:
        print 'gunElevationDeltaH failed', e
        return 0.0

def gunElevation(r, v, g):
    """
    r  -> range as crow flies
    v  -> muzzle velocity
    g  -> gravitymod
    """
    try:
        r, v, g = map(float, (r, v, g))
        g *= gravity
        t = 0.5 * math.asin((g * r) / (v ** 2))
        return math.degrees(t)
    except Exception, e:
        print 'gunElevation failed', e
        return 0.0

elevation_out_of_range = 90.0

def gunElevationDeltaH(dh, r, v, g, parabolic = False):
    """
    dh -> delta h (h_end - h_start)
    r  -> range as crow flies
    v  -> muzzle velocity
    g  -> gravitymod
    parabolic -> select the other root
    """
    dh, r, v, g = map(float, (dh, r, v, g))
    g *= gravity
    A = (-g * (r ** 2)) / (2 * (v ** 2))
    k = r ** 2 - 4 * A * (A - dh)
    if k < 0.0: return elevation_out_of_range
    k = math.sqrt(k)
    if parabolic:
        t = (-r - k) / (2 * A)
    else:
        t = (-r + k) / (2 * A)
    return math.degrees(math.atan(t))

def gunVector(gun, targ, v, g, parabolic = False):
    """
    credit to Jon Watte from the ODE mailing list
    gun       -> triple; coordinates of gun
    targ      -> triple; coordinates of target
    v         -> muzzle velocity
    g         -> gravitymod
    parabolic -> select the other root
    """
    v, g = map(float, (v, g))
    g *= gravity
    v2 = v ** 2
    v4 = v2 ** 2
    g2 = g ** 2
    
    vec = [float(targ[i] - gun[i]) for i in range(3)]
    
    p = v4 - (2 * vec[1] * g * v2) - (vec[2] ** 2 * g2) - (vec[0] ** 2 * g2)
    if p < 0: raise ValueError, "gun cannot reach target"
    
    p = math.sqrt(p)
    q = v2 - vec[1] * g
    if parabolic:
        r = q - p
    else:
        r = q + p
    
    ti = math.sqrt(r) * math.sqrt(2) / g
    return (vec[0] / ti,
            g * ti / 2 + vec[1] / ti,
            vec[2] / ti)
            
def getSpawnTime(rstime, dt):
    """
    Returns seconds to next spawnwave.
    rstime - walltime of round_start
    dt - walltime of player death
    """
    if rstime and dt:
        time = int(dt - rstime)
        serverSpawnTime = float(rconExec('sv.spawntime'))
        if serverSpawnTime != 0.0:
            timeMarker = time / serverSpawnTime
        else:
            timeMarker = 1.0
        if timeMarker == 1.0:
            return 0
        else:
            fraction = timeMarker - int(timeMarker)
            time_inverted = int(fraction * serverSpawnTime)
            timeToSpawn = int(serverSpawnTime - time_inverted)
            return timeToSpawn

gamemode = None
            
def cp_setTeam(cp, team, do_plugins = 1):
    # Proper Control Point team changing function
    global gamemode
    if gamemode is None:
        mapname, mode, mapsize = getCurrentRound()
        if mode == 'gpm_cq':
            import game.gamemodes.gpm_cq
            gamemode = game.gamemodes.gpm_cq
        elif mode == 'gpm_coop':
            import game.gamemodes.gpm_coop
            gamemode = game.gamemodes.gpm_coop
        else:
            import game.gamemodes.gpm_cq
            gamemode = game.gamemodes.gpm_cq
    
    if team in (1, 2):
        top = 1
    else:
        top = 0
    
    if top:
        cp.cp_setParam('flag', team)
    cp.cp_setParam('team', team)
    gamemode.onCPTrigger(cp.triggerId, cp, 0, 0, 0)
    gamemode.updateTicketLoss()

    if do_plugins:
        for p in gamemode.g_plugin.loaded_plugins:
            if hasattr(p, 'onCPStatusChange'):
                try:
                    p.onCPStatusChange(cp, top)
                except Exception, e:
                    print 'cp_setTeam exception while calling onCPStatusChange in %s: %s' % (p, e)
            