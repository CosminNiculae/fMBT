# fMBT, free Model Based Testing tool
# Copyright (c) 2013, Intel Corporation.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms and conditions of the GNU Lesser General Public License,
# version 2.1, as published by the Free Software Foundation.
#
# This program is distributed in the hope it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.
#
# You should have received a copy of the GNU Lesser General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St - Fifth Floor, Boston, MA 02110-1301 USA.

"""
This is library implements fmbtandroid.Device-like interface for
Tizen devices.

WARNING: THIS IS A VERY SLOW PROTOTYPE WITHOUT ANY ERROR HANDLING.
"""

import commands
import subprocess
import os

import fmbt
import fmbtgti

def _run(command, expectedExitStatus=None):
    if type(command) == str: shell=True
    else: shell=False

    try:
        p = subprocess.Popen(command, shell=shell,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             close_fds=True)
        if expectedExitStatus != None:
            out, err = p.communicate()
        else:
            out, err = ('', None)
    except Exception, e:
        class fakeProcess(object): pass
        p = fakeProcess
        p.returncode = 127
        out, err = ('', e)

    exitStatus = p.returncode

    if (expectedExitStatus != None and
        exitStatus != expectedExitStatus and
        exitStatus not in expectedExitStatus):
        msg = "Executing %s failed. Exit status: %s, expected %s" % (command, exitStatus, expectedExitStatus)
        fmbt.adapterlog("%s\n    stdout: %s\n    stderr: %s\n" % (msg, out, err))
        raise FMBTTizenError(msg)

    return exitStatus, out, err

class Device(fmbtgti.GUITestInterface):
    def __init__(self):
        fmbtgti.GUITestInterface.__init__(self)
        self.setConnection(TizenDeviceConnection())

class TizenDeviceConnection(fmbtgti.GUITestConnection):
    def __init__(self):
        self._serialNumber = self.recvSerialNumber()
        self.connect()

    def connect(self):
        agentFilename = "/tmp/fmbttizen-agent.py"
        agentRemoteFilename = "/tmp/fmbttizen-agent.py"

        file(agentFilename, "w").write(_X11agent)

        status, _, _ = _run(["sdb", "push", agentFilename, agentRemoteFilename])

        self._sdbShell = subprocess.Popen(["sdb", "shell"], shell=False,
                                          stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                          close_fds=True)
        self._sdbShell.stdin.write("\r")
        self._agentCmd("python %s; exit" % (agentRemoteFilename,),
                       afterPrompt = lambda s: s.strip().endswith("#"))
        self._agentWaitLine(lambda s: s.strip() == "fmbttizen-agent")
        os.remove(agentFilename)

    def close(self):
        self._sdbShell.stdin.close()
        self._sdbShell.stdout.close()
        self._sdbShell.terminate()

    def _agentWaitLine(self, lineValidator):
        l = self._sdbShell.stdout.readline().strip()
        if lineValidator == None:
            lineValidator = lambda s: s == "OK"
        while not lineValidator(l):
            l = self._sdbShell.stdout.readline()
            if l == "": raise IOError("Unexpected end of sdb shell output")
            l = l.strip()

    def _agentCmd(self, command, afterPrompt = None, retry=3):
        try:
            self._agentWaitLine(afterPrompt)
            self._sdbShell.stdin.write("%s\r" % (command,))
            self._sdbShell.stdin.flush()
        except IOError:
            if retry > 0:
                self.connect()
                self._agentCmd(command, afterPrompt, retry=retry-1)
            else:
                raise
        return True

    def sendPress(self, keyName):
        s, o = commands.getstatusoutput("sdb shell xte 'key %s'" % (keyName,))
        return True

    def sendKeyDown(self, keyName):
        s, o = commands.getstatusoutput("sdb shell xte 'keydown %s'" % (keyName,))
        return True

    def sendKeyUp(self, keyName):
        s, o = commands.getstatusoutput("sdb shell xte 'keyup %s'" % (keyName,))
        return True

    def sendTap(self, x, y):
        return self._agentCmd("t%s %s 1" % (x, y))

    def sendTouchDown(self, x, y):
        return self._agentCmd("d%s %s 1" % (x, y))

    def sendTouchMove(self, x, y):
        return self._agentCmd("m%s %s" % (x, y))

    def sendTouchUp(self, x, y):
        return self._agentCmd("u%s %s 1" % (x, y))

    def sendType(self, string):
        s, o = commands.getstatusoutput("sdb shell xte 'str %s'" % (string,))
        return True

    def recvScreenshot(self, filename):
        remoteFilename = "/tmp/fmbttizen.screenshot.xwd"
        s, o = commands.getstatusoutput("sdb shell 'xwd -root -out %s'" % (remoteFilename,))
        s, o = commands.getstatusoutput("sdb pull %s %s.xwd" % (remoteFilename, filename))
        s, o = commands.getstatusoutput("sdb shell rm %s" % (remoteFilename,))
        s, o = commands.getstatusoutput("convert %s.xwd %s" % (filename, filename))
        os.remove("%s.xwd" % (filename,))
        return True

    def recvSerialNumber(self):
        s, o = commands.getstatusoutput("sdb get-serialno")
        return o.splitlines()[-1]

    def target(self):
        return self._serialNumber

# _X11agent code is executed on Tizen device in sdb shell.
# The agent synthesizes X events.
_X11agent = """
import ctypes
import sys

libX11         = ctypes.CDLL("libX11.so")
libXtst        = ctypes.CDLL("libXtst.so.6")
X_CurrentTime  = ctypes.c_ulong(0)
X_True         = ctypes.c_int(1)
X_False        = ctypes.c_int(0)
NULL           = ctypes.c_char_p(0)

display        = ctypes.c_void_p(libX11.XOpenDisplay(NULL))
current_screen = ctypes.c_int(-1)

def read_cmd():
    sys.stdout.write('OK\\n')
    sys.stdout.flush()
    return sys.stdin.readline().strip()

sys.stdout.write('fmbttizen-agent\\n')
sys.stdout.flush()
cmd = read_cmd()
while cmd:
    if cmd.startswith("m"):   # move(x, y)
        xs, ys = cmd[1:].strip().split()
        libXtst.XTestFakeMotionEvent(display, current_screen, int(xs), int(ys), X_CurrentTime)
        libX11.XFlush(display)
    elif cmd.startswith("t"): # tap(x, y, button)
        xs, ys, button = cmd[1:].strip().split()
        button = int(button)
        libXtst.XTestFakeMotionEvent(display, current_screen, int(xs), int(ys), X_CurrentTime)
        libXtst.XTestFakeButtonEvent(display, button, X_True, X_CurrentTime)
        libXtst.XTestFakeButtonEvent(display, button, X_False, X_CurrentTime)
        libX11.XFlush(display)
    elif cmd.startswith("d"): # down(x, y, button)
        xs, ys, button = cmd[1:].strip().split()
        button = int(button)
        libXtst.XTestFakeMotionEvent(display, current_screen, int(xs), int(ys), X_CurrentTime)
        libXtst.XTestFakeButtonEvent(display, button, X_True, X_CurrentTime)
        libX11.XFlush(display)
    elif cmd.startswith("u"): # up(x, y, button)
        xs, ys, button = cmd[1:].strip().split()
        button = int(button)
        libXtst.XTestFakeMotionEvent(display, current_screen, int(xs), int(ys), X_CurrentTime)
        libXtst.XTestFakeButtonEvent(display, button, X_False, X_CurrentTime)
        libX11.XFlush(display)
    cmd = read_cmd()

display = libX11.XCloseDisplay(display)
"""

class FMBTTizenError(Exception): pass
