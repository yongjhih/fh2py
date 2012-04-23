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
# ingameEditor.py -- ingame editor, based upon default rcon module by DICE
# ©2006 Joseph Birr-Pixton aka ctz for Forgotten Hope

import socket
import errno
import bf2, host, bf2.Timer
from game.gameplayPlugin import base
import game.utilities

# A stateful output buffer that knows how to enqueue data and ship it out
# without blocking.
class OutputBuffer(object):

    def __init__(self, sock):
        self.sock = sock
        self.data = []
        self.index = 0

    def enqueue(self, str):
        self.data.append(str)

    def update(self):
        allowBatching = True
        while len(self.data) > 0:
            try:
                item = self.data[0]
                scount = self.sock.send(item[self.index:])
                self.index += scount
                if self.index == len(item):
                    del self.data[0]
                    self.index = 0
            except socket.error, detail:
                if detail[0] != errno.EWOULDBLOCK:
                    return detail[1]
            if not allowBatching:
                break
        return None

# Each TCP connection is represented by an object of this class.
class EditorConnection(object):

    def __init__(self, srv, sock, addr):
        print 'new editor connection from %s:%d' % (addr[0], addr[1])
        self.server = srv
        self.sock = sock
        self.addr = addr
        self.sock.setblocking(0)
        self.buffer = ''
        self.outbuf = OutputBuffer(self.sock)
        
        self.outbuf.enqueue('FH2EDIT\n\n')

    def update(self):
        err = None
        try:
            allowBatching = True
            while not err:
                data = self.sock.recv(1024)
                if data:
                    self.buffer += data
                    while not err:
                        nlpos = self.buffer.find('\n')
                        if nlpos != -1:
                            self.server.onRemote(self, self.buffer[0:nlpos])
                            self.buffer = self.buffer[nlpos+1:] # keep rest of buffer
                        else:
                            if len(self.buffer) > 128:
                                err = 'data format error: no newline in message'
                            break
                        if not allowBatching: break
                else:
                    err = 'peer disconnected'
                
                if not allowBatching: break

        except socket.error, detail:
            if detail[0] != errno.EWOULDBLOCK:
                err = detail[1]

        if not err:
            err = self.outbuf.update()

        if err:
            print 'editor: closing %s:%d: %s' % (self.addr[0], self.addr[1], err)
            try:
                self.sock.shutdown(2)
                self.sock.close()
            except:
                print 'editor: warning: failed to close %s:%d' % (self.addr[0], self.addr[1])
                pass
            return 0
        else:
            return 1

# The server itself.
class EditorServer(object):

    def __init__(self, port):
        # state for tcp rcon connections
        self.port = port
        self.backlog = 1
        self.peers = []
        self.openSocket()

    def onRemote(self, socket, cmd):
        cmd = cmd.strip()
        if cmd[0] == '!':
            try:
                result = repr(eval(cmd[1:]))
            except Exception, e:
                result = repr('failed: ' + str(e))
            socket.outbuf.enqueue(result + '\x00')
        else:
            socket.outbuf.enqueue(host.rcon_invoke(cmd) + '\x00')
    
    # Sets up the listening TCP RCON socket. This binds to 0.0.0.0, which may
    # not be what you want but it's a sane default for most installations.
    def openSocket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, 0)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('127.0.0.1', self.port))
            self.sock.listen(self.backlog)
            self.sock.setblocking(0)
        except socket.error, detail:
            print 'failed to bind editor socket'

    # WARNING: update is called very frequently -- don't go crazy with logic
    # here.
    def update(self):
        # if we don't have a socket, just return
        if not self.sock: return

        # without blocking, check for new connections
        try:
            conn, peeraddr = self.sock.accept()
            self.peers.append(EditorConnection(self, conn, peeraddr))
        except socket.error, detail:
            if detail[0] != errno.EWOULDBLOCK:
                raise socket.error, detail

        # update clients and mark connections that fail their update
        disc = []
        for client in self.peers:
            if not client.update(): disc.append(client)

        # now keep the remaining clients
        self.peers = filter(lambda x: x not in disc, self.peers)

    def shutdown(self):
        if self.sock:
            self.sock.close()

class ingameEditor(base):
    def __init__(self):
        # our single server instance
        self.server = EditorServer(19991)
        self.timer = None
        print 'initialized ingame editor module'
    
    def round_start(self, hooker):
        self.timer = bf2.Timer(self.update, 0.1, 1)
        self.timer.setRecurring(0.1)

    def round_end(self, hooker):
        if self.timer:
            self.timer.destroy()
            self.timer = None

    def update(self, ignore):
        try:
            if self.server:
                self.server.update()
        except Exception, e:
            print 'ingameEditor interval function failed', type(e), e, dir(e)
