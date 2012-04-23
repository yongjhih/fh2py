
try:
    # thanks to [poe2]seigman and [dcon]kiff below...
    import bf2.stats.stats
    from game.stats.stats import fh2stats_init

    bf2.stats.stats.init = fh2stats_init

    print 'patched stat functions [python/game/__init__.py]'
except Exception, e:
    pass

# edit to 1 to enabling logging
global_logs = 0

try:
    import sys, datetime
    
    def start_log(f):
        f = open(f, 'w', 0)
        print >>f, ' -- FH2 -- Log started at %s -- '%datetime.datetime.now()
        f.flush()
        return f
    
    if global_logs:
        sys.stdout = start_log('mods/fh2/fh2-debug.log')
        sys.stderr = start_log('mods/fh2/fh2-errors.log')
except Exception, e:
    print 'failed to start logs:', e