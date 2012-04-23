import game.utilities, sys

DEBUG = 0

def _go_broken(vehicle, info, u, v):
    parabolic = info.get('parabolic', False)
    vector = game.utilities.gunVector(u, v, info['velocity'], info['gravitymod'], parabolic)
    if DEBUG: print 'AM: vector is', vector

    vehrot = game.utilities.findAbsoluteRotation(game.utilities.rootParent(vehicle), vehicle.templateName)
    if DEBUG: print 'vehicle is', vehicle.templateName, 'rotation', vehrot
    translated_vector = game.utilities.rotateVector((vehrot[1], vehrot[0], vehrot[2]), vector)
    heading = game.utilities.vectorAngle((0, 0), (translated_vector[0], translated_vector[2]))
    elevation_vector = game.utilities.rotateVector((0, 0, -heading), translated_vector)
    if DEBUG: print 'AM: elevation vector', elevation_vector
    elevation = 90 - game.utilities.vectorAngle((0, 0), (elevation_vector[1], elevation_vector[2]))

    if DEBUG:
        print 'AM:       vector', vector
        print 'AM: xlate vector', translated_vector
    
        print 'AM: desired elevation is', elevation, 'degrees'
        print 'AM: heading is', heading, 'degrees absolute'

        print 'AM: vehicle rotation is', vehrot, 'degrees'
        print 'AM: result rotation is', heading, 'degrees'
    
    return -elevation, heading

def _go(vehicle, info, u, v):
        heading = game.utilities.vectorAngle((u[0], u[2]), (v[0], v[2]))
        distance = game.utilities.vectorDistance(u, v)
        deltah = v[1] - u[1]
        
        parabolic = info.get('parabolic', False)
        
        elevation = game.utilities.gunElevationDeltaH(deltah, distance, info['velocity'], info['gravitymod'], parabolic)
        
        vehrot = game.utilities.rootParent(vehicle).getRotation()[0]
        
        if DEBUG:
            print 'desired elevation is', elevation, 'degrees'
            print 'heading is', heading, 'degrees absolute'
            print 'distance is', distance, 'meters'
            print 'deltah is', deltah, 'meters'
            
            print 'vehicle rotation is', vehrot, 'degrees'
            print 'result rotation is', heading - vehrot, 'degrees'
        
        return -elevation, heading - vehrot

def go(vehicle, info, u, v):
    try:
        return _go(vehicle, info, u, v)
    except Exception, e:
        print 'AM failed:', e
        sys.excepthook(*sys.exc_info())
        return 0.0, 0.0