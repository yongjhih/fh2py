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
# NCOrifleData.py -- database for NCOrifle script.
#
#  ©2010 Spit for Forgotten Hope

NCO_kits = {
    'alam_halfa':            ('GA_NCOMP40', 'BA_NCOTommygunS'),
    'anctoville_1944':       ('GW_NCO', 'BW_NCO_Sten'),
    'battle_of_brest':       ('GW_NCO', 'UW_NCO'),
    'battle_of_foy':         ('GW_NCO', 'UW_NCO'),
    'bardia':                ('IA_NCOBeretta38', 'AA_NCOTommygunS'),
    'bastogne':              ('GW_NCO', 'UW_NCO'),
    'battle_at_puffendorf':  ('GW_NCO_SME', 'UW_NCO'),
    'crete_1941':            ('GM_NCOMP40', 'BA_NCOTommygunS'),
    'crimea':                ('GW_NCO', 'RE_NCO'),
    'el_alamein':            ('GA_NCOMP40', 'BA_NCOTommygunS'),
    'eppeldorf':             ('GS_NCO_mp40_g43', 'UW_NCO'),
    'falaise_pocket':        ('GW_NCO', 'cw_NCO'),
    'fall_of_tobruk':        ('GA_NCOMP40', 'BA_NCOTommygunS'),
    'gazala':                ('GA_NCOMP40', 'BA_NCOTommygunS'),
    'giarabub':              ('IA_NCOBeretta38', 'AA_NCOTommygunS'),
    'gold_beach':            ('GW_NCO', 'BW_NCO'),
    'hurtgen_forest':        ('GW_NCO', 'UW_NCO'),
    'kuuterselka':           ('SE_NCO', 'RE_NCO'),
    'lebisey':               ('GW_NCO', 'BW_NCO'),
    'mareth_line':           ('GA_NCOMP40', 'BA_NCOTommygunS'),
    'mersa_matruh':          ('GA_NCOMP40', 'BA_NCOTommygunS'),
    'meuse_river':           ('GW_NCO', 'UW_NCO'),
    'mount_olympus':         ('GM_NCOMP40', 'BA_NCOTommygunS'),
    'operation_aberdeen':    ('GA_NCOMP40', 'BA_NCOTommygunS'),
    'operation_cobra':       ('GS_NCO', 'UW_NCO'),
    'operation_goodwood':    ('GS_NCO_GWood', 'BW_NCO_GWood'),
    'operation_hyacinth':    ('IA_NCOBeretta38', 'BA_NCOTommygunS'),
    'operation_luttich':     ('GW_NCO', 'UW_NCO'),
    'operation_totalize':    ('GS_NCO', 'CW_NCO'),
    'pointe_du_hoc':         ('GW_NCO', 'UW_NCO'),
    'port_en_bessin':        ('GW_NCO', 'BW_NCO'),
    'purple_heart_lane':     ('GS_NCO', 'UW_NCO'),
    'ramelle':               ('GS_NCO', 'UW_NCO'),
    'sidi_rezegh':           ('GA_NCOMP40', 'BA_NCOTommygunS'),
    'siege_of_tobruk':       ('GA_NCOMP40', 'AA_NCOTommygunS'),
    'st_lo_breakthrough':    ('GS_NCOStg44', 'UW_NCO'),
    'st_mere_eglise':        ('GW_NCO_SME', 'UW_NCO_SME'),
    'supercharge':           ('GA_NCOMP40', 'BA_NCOTommygunS'),
    'the_battle_for_sfakia': ('GM_NCOMP40', 'BA_NCOTommygunS'),
    'tunis_1943':            ('GA_NCOMP40', 'BA_NCOTommygunS'),
    'villers_bocage':        ('GS_NCO', 'BW_NCO'),
    'vossenack':             ('GW_NCO', 'UW_NCO'),
}

from game.gameplayPlugin import base
from game.utilities import getCurrentRound

class NCOrifleData(base):
    def __init__(self, kits):
        self.kits = kits
    
    def round_start(self, hooker):
        global NCO_kits
        map, gamemode, size = getCurrentRound()
        NCO_kits[map] = self.kits
        print 'Added custom data to NCO_kits [NCOrifleData.py]'
