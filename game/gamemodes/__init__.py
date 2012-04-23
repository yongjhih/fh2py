
try:
    # thnx to seigman and kiff below...
    import bf2.stats.stats
    from game.stats.stats import fh2stats_init

    bf2.stats.stats.init = fh2stats_init

    print 'patched stat functions [python/game/gamemodes/__init__.py]'
except Exception, e:
    #print 'patch in [python/game/gamemodes/__init__.py] failed:', e
    pass