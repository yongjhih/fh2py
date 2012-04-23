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
# conParser.py -- con-file parser
#  ©2006 Joseph Birr-Pixton aka ctz for Forgotten Hope
import sys, os, glob

try:
    import bf2
    from game.utilities import path
except:
    import os.path as path

def find_file(fn):
    yy = []
    for x in fn:
        if x.lower() in 'abcdefghijklmnopqrstuvwxyz':
            yy.append('[' + x.lower() + x.upper() + ']')
        else:
            yy.append(x)
    found = glob.glob(''.join(yy))
    if len(found):
        return found[0]
    else:
        return None

def ci_exists(fn):
    return find_file(fn) is not None

def ci_open(fn, mode):
    if os.sys == 'nt':
        return open(fn, mode)
    real_fn = find_file(fn)
    if real_fn is None:
        raise IOError, '%s file does not exist' % fn
    return open(real_fn, mode)

class Template:
    def __init__(self, type, name):
        self.original_name = name
        self.type, self.name = type.lower(), name.lower()
        self.properties = {}
        self.children = []

class Instance:
    def __init__(self, template):
        self.template = template
        self.properties = {}

class ConParser:
    def __init__(self, do_instances = False):
        self.template = None
        self.templates = []
        self.instance = None
        self.instances = []
        self.do_instances = do_instances
        self.lines = []
        self.base = None

    def load(self, filename):
        self.base = path.dirname(filename)
        self.run(filename)
        self.go()

    def run_string(self, string):
        self.lines.extend(string.strip().split('\n'))
        self.go()
        
    def run(self, filename):
        fd = ci_open(filename, 'r')
        l = map(lambda x: x.strip(), fd.readlines())
        l.extend(self.lines)
        self.lines = l
        fd.close()
    
    def do_include(self, filename):
        assert self.base is not None, 'missing base for include'
        if ci_exists(path.join(self.base, filename)):
            self.run(path.join(self.base, filename))
        
    def go(self):
        ignore = False
        while len(self.lines) > 0:
            l = self.lines.pop(0)
            args = self._get_args(l)
            if len(args) == 0: continue
            args[0] = args[0].lower()
            if args[0] in ('endrem', 'endif'):
                ignore = False
                continue
            if args[0] == 'rem' or ignore: continue
            if args[0] in ('beginrem', 'if'):
                ignore = True
                continue
            if args[0] == 'run' or args[0] == 'include':
                assert len(args) == 2
                self.do_include(args[1].lower())
                continue
                
            self.process_directive(args[0], args[1:])
        
    def _get_args(self, line):
        out = []
        slurping = 0
        slurpee = []

        for i in range(len(line)):
            c = line[i]

            if c in (' ', '\t', '\n', '\r') and slurping is not 1:
                if len(slurpee) is not 0:
                    out.append(''.join(slurpee))
                slurpee = []
                continue

            if slurping is 1:
                if c == '"':
                    slurping = 0
                    out.append(''.join(slurpee))
                    slurpee = []
                    continue
                slurpee.append(c)
                continue

            if c == '"':
                slurping = 1
                slurpee = []
                continue

            slurpee.append(c)

        if len(slurpee) is not 0:
            out.append(''.join(slurpee))

        return out

    def process_directive(self, command, args):
        command = command.lower()
            
        if command.startswith('object.') and self.do_instances:
            if command == 'object.create':
                template, = args
                self.instance = Instance(template)
                self.instances.append(self.instance)
                return
            
            if self.instance is None:
                print 'command', command, args, 'executed without current instance'
            props = self.instance.properties.get(command, [])
            props.append(args)
            self.instance.properties[command] = props
        
        elif command.startswith('objecttemplate.'):
            if command == 'objecttemplate.create':
                type, name = args
                self.template = Template(type, name)
                self.templates.append(self.template)
                return

            if command == 'objecttemplate.active':
                name = args[0].lower()
                self.template = None
                for x in self.templates:
                    if x.name == name:
                        self.template = x
                        break
                if self.template is None:
                    if name.lower().startswith('s_'):
                        self.template = Template('Sound', name)
                    else:
                        print '*** unknown active template:', name
                        self.template = Template('SimpleObject', name)
                    self.templates.append(self.template)
                return
            if command == 'objecttemplate.activesafe':
                if len(args) != 2:
                    print '*** invalid objecttemplate.activesafe line in', self.base, ':', command, args
                    return
                type, name = args
                type, name = type.lower(), name.lower()
                self.template = None
                for x in self.templates:
                    if x.name == name:
                        if x.type == type:
                            self.template = x
                        else:
                            print '*** unknown activesafe template', name, 'wrong type: wanted', type, 'got', x.type
                            self.template = x
                        break
                if self.template is None:
                    self.template = Template(type, name)
                    self.templates.append(self.template)
                return

            if command == 'objecttemplate.addtemplate':
                name = args[0].lower()
                self.template.children.append(name)
                return

            if self.template is None:
                print 'command', command, args, 'executed without current template'
            props = self.template.properties.get(command, [])
            props.append(args)
            self.template.properties[command] = props
        else:
            return
        
