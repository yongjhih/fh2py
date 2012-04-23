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
# vehicleMetadata.py -- types of vehicles
#  ©2006 Joseph Birr-Pixton aka ctz for Forgotten Hope

tanks = (
  'sdkfz251_1', 'pziic', 'pziiindak', 'pzivf1', 'pzivf2', 'crusadermk1early', 'marder_i', 'marder_iii',
  'crusadermk1late', 'crusadermk3', 'm3grant', 'm3stuarthoney', 'valentineii', 'panthera', 'panthera_alt',
  'markvi', 'm4a1', 'pziiijedak', 'matildaii', 'cruiseriv', 'pziif', 'pziiijldak', 'panthera_late'
  'fiatl6_40', 'carrom13_40_au', 'carrom13_40', 'semoventel40', 'sahariana', 'panthera_late_alt'
  'pantherg', 'pziiijedak_greece', 'pzivd_greece', 'pzivd_na', 'pzivh', 'pzivh_811', 'sdkfz251_10',
  'sdkfz251_d', 'sdkfz251_d_sf', 'stug40', 'stug40r', 'tiger_dak', 'tiger_late', 'tiger_late_222',
  'tiger_late_132', 'wirbelwind', 'kingtiger_1944easternfall', 'kingtiger_1944fall', 'kingtiger_night',
  'kingtiger_standard', 'kingtiger_1944winter', 'kingtiger_1945spring', 'hetzer', 'jagdpanther', 'hetzer_win',
  'jagdpanzeriv', 'panther_g_ard', 'panther_g_late_ard', 'panther_g_win', 'pzivh_ard', 'pzivh_ard_win',
  'sdkfz251_d_ard', 'sdkfz251_d_win', 'achilles_iic', 'churchillmkiv_6pdr', 'cromwell', 'cromwell_irishguard',
  'cromwell_polish', 'crusadermk3_aa', 'm5a1_halftrack', 'm5a1_halftrack_spawn', 'churchillmkiv_75mm'
  'churchillmkiv_avre', 'm4a1early_eu_brit', 'm4a1mid_eu_brit', 'sherman_v_late', 'sherman_v_late_olive',
  'sherman_v_late_alt', 'sherman_v_late_olive', 'sherman_v_mid', 'sherman_v_mid_olive', 'sherman_vc_early',
  'sherman_vc_early_olive', 'sherman_vc_late', 'sherman_vc_late_olive', 'universalcarrier', 'universalcarrier_france',
  'universalcarrier_bren', 'universalcarrier_france_bren', 'universalcarrier_france_bren_spawn', 'm10', 'm36', 'm26_pershing',
  'm3a1', 'm3a1_spawn', 'm4a1_76mm', 'm4a1early_eu', 'm4a1mid_eu', 'm5a1_stuart', 'm5a1_stuart_recon', 'm24_chaffee',  
)

planes = (
  'bf109e7_trop', 'bf109e7_tropalt', 'bf109e7_greece', 'ju87b2', 'ju87b2alt', 'ju52', 'storch_trop', 'beaufightermk1',
  'beaufightermk1_b', 'hurricanemkii', 'hurricanemkii_b', 'pipercub_gb','fw190_alt', 'bf109e7_greecealt',
  'spitfiremkvb', 'swordfish', 'swordfish_b', 'dauntlesssbdtorch', 'storch_france', 'fw190', 'ju87b2_greece', 'ju87b2_libya',
  'typhoon_mk1b_late', 'horsa_glider', 'spitfiremki', 'spitfiremkv', 'hurricanemkii_alt_b', 'hurricanemkiid', 'aix_p51d',
  'aix_p51d_bombs', 'aix_p51d_rockets', 'p47_d', 'p47_d_alt', 'p47_d_rocket', 'c47', 'bf109f4', 'bf109f4_alt250kg', 'bf109f4_alt50kg',
  'bf109f4_trop',
)

parachutes = (
  'x9chute', 'rz20chute',
)

artillery_info = {
  '25pdr': dict(barrel = '25pdr_barrel', azimuth = '25pdr_remotecam_azi_req', elevation = '25pdr_remotecam_elev_req',
                camera = '25pdr_remotecam_holder', velocity = 480.0, gravitymod = 10.0, elevation_offset = -16.3974,
                indicator = '25pdr_remotecam_targetind',
                static = True),
  '25pdr_ai': dict(barrel = '25pdr_ai_barrel', azimuth = '25pdr_remotecam_azi_req', elevation = '25pdr_remotecam_elev_req',
                camera = '25pdr_remotecam_holder', velocity = 480.0, gravitymod = 10.0, elevation_offset = -16.3974,
                indicator = '25pdr_remotecam_targetind',
                static = True),
  '3inchmortar':
           dict(barrel = '3inchmortar_mortarfirearm', azimuth = '3inchmortar_remotecam_azi_req', elevation = '3inchmortar_remotecam_elev_req',
                camera = '3inchmortar_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -50.25,
                indicator = '3inchmortar_remotecam_targetind',
                parabolic = True),
  '3inchmortar_ai':
           dict(barrel = '3inchmortar_ai_mortarfirearm', azimuth = '3inchmortar_remotecam_azi_req', elevation = '3inchmortar_remotecam_elev_req',
                camera = '3inchmortar_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -50.25,
                indicator = '3inchmortar_remotecam_targetind',
                parabolic = True),
  'bedfordoyd_mortar':
           dict(barrel = '3inchmortar_mortarfirearm', azimuth = '3inchmortar_remotecam_azi_req', elevation = '3inchmortar_remotecam_elev_req',
                camera = '3inchmortar_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -50.25,
                indicator = '3inchmortar_remotecam_targetind',
                static = False, parabolic = True, base = '3inchmortar'),
  'lefh18':
           dict(barrel = 'lefh18_gun', azimuth = 'lefh18_remotecam_azi_req', elevation = 'lefh18_remotecam_elev_req',
                camera = 'lefh18_remotecam_holder', velocity = 480.0, gravitymod = 10.0, elevation_offset = -0.25,
                indicator = 'lefh18_remotecam_targetind',
                static = True),
  'lefh18_ai':
           dict(barrel = 'lefh18_ai_gun', azimuth = 'lefh18_remotecam_azi_req', elevation = 'lefh18_remotecam_elev_req',
                camera = 'lefh18_remotecam_holder', velocity = 480.0, gravitymod = 10.0, elevation_offset = -0.25,
                indicator = 'lefh18_remotecam_targetind',
                static = True),
  'lefh18_france':
           dict(barrel = 'lefh18_france_gun', azimuth = 'lefh18_france_remotecam_azi_req', elevation = 'lefh18_france_remotecam_elev_req',
                camera = 'lefh18_france_remotecam_holder', velocity = 480.0, gravitymod = 10.0, elevation_offset = -0.25,
                indicator = 'lefh18_france_remotecam_targetind',
                static = True), 
  'lefh18_france_ai':
           dict(barrel = 'lefh18_france_ai_gun', azimuth = 'lefh18_france_remotecam_azi_req', elevation = 'lefh18_france_remotecam_elev_req',
                camera = 'lefh18_france_remotecam_holder', velocity = 480.0, gravitymod = 10.0, elevation_offset = -0.25,
                indicator = 'lefh18_france_remotecam_targetind',
                static = True), 
 'gpf_155mm':
           dict(barrel = 'GPF_155mm_Barrel', azimuth = 'gpf_155mm_remotecam_azi_req', elevation = 'gpf_155mm_remotecam_elev_req',
                camera = 'gpf_155mm_remotecam_holder', velocity = 480.0, gravitymod = 10.0, elevation_offset = -0.25,
                indicator = 'gpf_155mm_remotecam_targetind',
                static = True),   
  'sgwr34':
           dict(barrel = 'sgwr34_mortarfirearm', azimuth = 'sgwr34_remotecam_azi_req', elevation = 'sgwr34_remotecam_elev_req',
                camera = 'sgwr34_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -75.25,
                indicator = 'sgwr34_remotecam_targetind',
                parabolic = True),
  'sgwr34_ai':
           dict(barrel = 'sgwr34_ai_mortarfirearm', azimuth = 'sgwr34_remotecam_azi_req', elevation = 'sgwr34_remotecam_elev_req',
                camera = 'sgwr34_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -75.25,
                indicator = 'sgwr34_remotecam_targetind',
                parabolic = True),
  'sgwr34_france':
           dict(barrel = 'sgwr34_france_mortarfirearm', azimuth = 'sgwr34_france_remotecam_azi_req', elevation = 'sgwr34_france_remotecam_elev_req',
                camera = 'sgwr34_france_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -75.25,
                indicator = 'sgwr34_france_remotecam_targetind',
                parabolic = True),
  'sgwr34_france_ai':
           dict(barrel = 'sgwr34_france_ai_mortarfirearm', azimuth = 'sgwr34_france_remotecam_azi_req', elevation = 'sgwr34_france_remotecam_elev_req',
                camera = 'sgwr34_france_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -75.25,
                indicator = 'sgwr34_france_remotecam_targetind',
                parabolic = True),                
  '25pdr_mkiv': dict(barrel = '25pdr_mkiv_barrel', azimuth = '25pdr_mkiv_remotecam_azi_req', elevation = '25pdr_mkiv_remotecam_elev_req',
                     camera = '25pdr_mkiv_remotecam_holder', velocity = 540.0, gravitymod = 10.0, elevation_offset = -16.3974,
                     indicator = '25pdr_mkiv_remotecam_targetind',
                     static = True),
  '25pdr_mkiv_ai': dict(barrel = '25pdr_mkiv_ai_barrel', azimuth = '25pdr_mkiv_remotecam_azi_req', elevation = '25pdr_mkiv_remotecam_elev_req',
                     camera = '25pdr_mkiv_remotecam_holder', velocity = 540.0, gravitymod = 10.0, elevation_offset = -16.3974,
                     indicator = '25pdr_mkiv_remotecam_targetind',
                     static = True),
  '3inchmortar_deployed':
           dict(barrel = '3inchmortar_deployed_mortarfirearm', azimuth = '3inchmortar_remotecam_azi_req', elevation = '3inchmortar_remotecam_elev_req',
                camera = '3inchmortar_deployed_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -50.25,
                indicator = '3inchmortar_remotecam_targetind',
                parabolic = True),
  'sgwr34_deployed':
           dict(barrel = 'sgwr34_deployed_mortarfirearm', azimuth = 'sgwr34_remotecam_azi_req', elevation = 'sgwr34_remotecam_elev_req',
                camera = 'sgwr34_deployed_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -75.25,
                indicator = 'sgwr34_remotecam_targetind',
                parabolic = True),
  'sgwr34_france_deployed':
           dict(barrel = 'sgwr34_france_deployed_mortarfirearm', azimuth = 'sgwr34_france_remotecam_azi_req', elevation =   'sgwr34_france_remotecam_elev_req',
                camera = 'sgwr34_france_deployed_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -75.25,
                indicator = 'sgwr34_france_remotecam_targetind',
                parabolic = True),
  'nebelwerfer':
           dict(barrel = 'nebelwerfer_barrel_he', azimuth = 'nebelwerfer_remotecam_azi_req', elevation = 'nebelwerfer_remotecam_elev_req',
                camera = 'nebelwerfer_remotecam_holder', velocity = 320.0, gravitymod = 3.0, elevation_offset = 0.0,
                indicator = 'nebelwerfer_remotecam_targetind',
                static = True),
  'nebelwerfer_ai':
           dict(barrel = 'nebelwerfer_ai_barrel_he', azimuth = 'nebelwerfer_remotecam_azi_req', elevation = 'nebelwerfer_remotecam_elev_req',
                camera = 'nebelwerfer_remotecam_holder', velocity = 320.0, gravitymod = 3.0, elevation_offset = 0.0,
                indicator = 'nebelwerfer_remotecam_targetind',
                static = True),
  'nebelwerfer_ard':
           dict(barrel = 'nebelwerfer_ard_barrel_he', azimuth = 'nebelwerfer_remotecam_azi_req', elevation = 'nebelwerfer_remotecam_elev_req',
                camera = 'nebelwerfer_ard_remotecam_holder', velocity = 320.0, gravitymod = 3.0, elevation_offset = 0.0,
                indicator = 'nebelwerfer_remotecam_targetind',
                static = True),
  'nebelwerfer_pan':
           dict(barrel = 'nebelwerfer_pan_barrel_he', azimuth = 'nebelwerfer_remotecam_azi_req', elevation = 'nebelwerfer_remotecam_elev_req',
                camera = 'nebelwerfer_pan_remotecam_holder', velocity = 320.0, gravitymod = 3.0, elevation_offset = 0.0,
                indicator = 'nebelwerfer_remotecam_targetind',
                static = True),
  'nebelwerfer_win':
           dict(barrel = 'nebelwerfer_win_barrel_he', azimuth = 'nebelwerfer_remotecam_azi_req', elevation = 'nebelwerfer_remotecam_elev_req',
                camera = 'nebelwerfer_win_remotecam_holder', velocity = 320.0, gravitymod = 3.0, elevation_offset = 0.0,
                indicator = 'nebelwerfer_remotecam_targetind',
                static = True),
  '81mm_mortar_m1_deployed':
           dict(barrel = '81mm_mortar_m1_deployed_mortarfirearm', azimuth = '81mm_mortar_remotecam_azi_req', elevation =   '81mm_mortar_remotecam_elev_req',
                camera = '81mm_mortar_m1_deployed_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -70.25,
                indicator = '81mm_mortar_remotecam_targetind',
                parabolic = True),
  '81mm_mortar_m1':
           dict(barrel = '81mm_mortar_m1_mortarfirearm', azimuth = '81mm_mortar_remotecam_azi_req', elevation = '81mm_mortar_remotecam_elev_req',
                camera = '81mm_mortar_m1_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -70.25,
                indicator = '81mm_mortar_remotecam_targetind',
                parabolic = True),
  '81mm_mortar_m1_ai':
           dict(barrel = '81mm_mortar_m1_ai_mortarfirearm', azimuth = '81mm_mortar_remotecam_azi_req', elevation = '81mm_mortar_remotecam_elev_req',
                camera = '81mm_mortar_m1_remotecam_holder', velocity = 185.0, gravitymod = 4.0, elevation_offset = -70.25,
                indicator = '81mm_mortar_remotecam_targetind',
                parabolic = True),
  'wespe_gunner':
           dict(barrel = 'wespe_gun', azimuth = 'wespe_remotecam_azi_req', elevation = 'wespe_remotecam_elev_req',
                camera = 'wespe_remotecam_holder', velocity = 480.0, gravitymod = 10.0, elevation_offset = -1.25,
                indicator = 'wespe_remotecam_targetind',
                static = False),
  'm2a1_howitzer_105mm': dict(barrel = 'm2a1_howitzer_105mm_barrel', azimuth = '105mm_remotecam_azi_req', elevation = '105mm_remotecam_elev_req',
                camera = '105mm_remotecam_holder', velocity = 480.0, gravitymod = 10.0, elevation_offset = -13.8940,
                indicator = '105mm_remotecam_targetind',
                static = True),
  'm2a1_howitzer_105mm_ai': dict(barrel = 'm2a1_howitzer_105mm_ai_barrel', azimuth = '105mm_remotecam_azi_req', elevation = '105mm_remotecam_elev_req',
                camera = '105mm_remotecam_holder', velocity = 480.0, gravitymod = 10.0, elevation_offset = -13.8940,
                indicator = '105mm_remotecam_targetind',
                static = True),
  'm2a1_howitzer_105mm_win': dict(barrel = 'm2a1_howitzer_105mm_win_barrel', azimuth = '105mm_remotecam_azi_req', elevation = '105mm_remotecam_elev_req',
                camera = '105mm_remotecam_holder', velocity = 480.0, gravitymod = 10.0, elevation_offset = -13.8940,
                indicator = '105mm_remotecam_targetind',
                static = True),
  'wurfgerat41': dict(barrel = 'wurfgerat28_trigger', azimuth = 'wurfgerat41_remotecam_azi_req', elevation = 'wurfgerat41_remotecam_elev_req',
                camera = 'wurfgerat41_remotecam_holder', velocity = 320.0, gravitymod = 8.0, elevation_offset = -22.0,
                indicator = 'wurfgerat41_remotecam_targetind',
                static = True), 
  'wurfgerat41_alt': dict(barrel = 'Wurfgerat28_Trigger_alt', azimuth = 'wurfgerat41_alt_remotecam_azi_req', elevation = 'wurfgerat41_alt_remotecam_elev_req',
                camera = 'wurfgerat41_alt_remotecam_holder', velocity = 320.0, gravitymod = 8.0, elevation_offset = -33.0,
                indicator = 'wurfgerat41_alt_remotecam_targetind',
                static = True),
  'stuka_fuzz_rocketpod': dict(barrel = 'stuka_fuzz_rocketpod_rocket', azimuth = 'sdkfz251d_sf_remotecam_azi_req', elevation = 'sdkfz251d_sf_remotecam_elev_req',
                camera = 'sdkfz251d_sf_remotecam_holder', velocity = 320.0, gravitymod = 6.0, elevation_offset = 2.0,
                indicator = 'sdkfz251d_sf_remotecam_targetind',
                static = False),
  'willysmb_rocket_codriver': dict(barrel = 'WillysMB_rockets', azimuth = 'willysmb_rocket_remotecam_azi_req', elevation = 'willysmb_rocket_remotecam_elev_req',
                camera = 'willysmb_rocket_remotecam_holder', velocity = 150.0, gravitymod = 2.0, elevation_offset = -2.75,
                indicator = 'willysmb_rocket_remotecam_targetind',
                static = False),
}

artillery = artillery_info.keys()

# We need this to be able to give spotting points to spotters using vehicles, like spotterplanes
# Dict PlayerControlObject -> GenericFireArm
targetting_pcos = {
'storch_trop_rearspotter': 'storch_trop_spotter',
'storch_france_rearspotter': 'storch_france_spotter',
'pipercub_gb_frontspotter': 'piper_front_spotter',
'pipercub_us_frontspotter': 'piper_front_spotter_us',
'beaufightermk1_rearobserver': 'beaufightermk1_rearobserver_gb',
'stug_lookout': 'stug_front_spotter_de',
'stugr_lookout': 'stug40r_front_spotter_de',
}

deployables = {
  'vickers303_dep':     dict(template = 'vickers303_tripod_dep', offset = 0.0227396),
  'bredam37_dep':       dict(template = 'bredam37_tripod_dep', offset = 0.0579149),
  'mg34_lafette_dep':   dict(template = 'mg34_lafette_deployed', offset = 0.300426),
  'mg42_lafette_dep':   dict(template = 'mg42_lafette_deployed', offset = 0.300426),
  '3inchmortar_dep':    dict(template = '3inchmortar_deployed', offset = 0.1194, flatten = True),
  'sgwr34_dep':         dict(template = 'sgwr34_deployed', offset = 0.08462, flatten = True),
  'sgwr34_france_dep':  dict(template = 'sgwr34_france_deployed', offset = 0.08462, flatten = True),
  '81mm_mortar_dep':    dict(template = '81mm_mortar_m1_deployed', offset = 0.12, flatten = True),
  'm1919a4_dep':        dict(template = 'm1919a4', offset = 0.23, flatten = True),
}
