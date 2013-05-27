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
This library implements fmbt GUITestInterface for X.
"""

import fmbtgti
import ctypes
import os
from wand.image import Image

class Screen(fmbtgti.GUITestInterface):
    def __init__(self):
        fmbtgti.GUITestInterface.__init__(self)
        self.setConnection(X11Connection())

class X11Connection(fmbtgti.GUITestConnection):
    def __init__(self):
        fmbtgti.GUITestConnection.__init__(self)
        self.libX11 = ctypes.CDLL("libX11.so")
        self.libXtst = ctypes.CDLL("libXtst.so.6")
        self.X_True = ctypes.c_int(1)
        self.X_False = ctypes.c_int(0)
        self.X_CurrentTime = ctypes.c_ulong(0)
        self.NULL = ctypes.c_char_p(0)
        self.current_screen = ctypes.c_int(-1)
        self.X_ZPixmap = ctypes.c_int(2)
        self.display = ctypes.c_void_p(self.libX11.XOpenDisplay(self.NULL))

        class XImage(ctypes.Structure):
            _fields_ = [
                ('width'            , ctypes.c_int),
                ('height'           , ctypes.c_int),
                ('xoffset'          , ctypes.c_int),
                ('format'           , ctypes.c_int),
                ('data'             , ctypes.c_void_p),
                ('byte_order'       , ctypes.c_int),
                ('bitmap_unit'      , ctypes.c_int),
                ('bitmap_bit_order' , ctypes.c_int),
                ('bitmap_pad'       , ctypes.c_int),
                ('depth'            , ctypes.c_int),
                ('bytes_per_line'   , ctypes.c_int),
                ('bits_per_pixel'   , ctypes.c_int)]
        self.libX11.XGetImage.restype = ctypes.POINTER(XImage)

    def __del__(self):
        self.libX11.XCloseDisplay(self.display)

    def sendTap(self, x, y):
        self.libXtst.XTestFakeMotionEvent(self.display, self.current_screen, int(x), int(y), self.X_CurrentTime)
        self.libXtst.XTestFakeButtonEvent(self.display, 1, self.X_True, self.X_CurrentTime)
        self.libXtst.XTestFakeButtonEvent(self.display, 1, self.X_False, self.X_CurrentTime)
        self.libX11.XFlush(self.display)
        return True
	
    def sendPress(self, key):
        # Convert to key code
        keysim = self.libXtst.XStringToKeysym(str(key))
        keycode = self.libXtst.XKeysymToKeycode(self.display, keysim)
        self.libXtst.XTestFakeKeyEvent(self.display, keycode, self.X_True, self.X_CurrentTime)
        self.libXtst.XTestFakeKeyEvent(self.display, keycode, self.X_False, self.X_CurrentTime)
        self.libXtst.XFlush(self.display)
	return True

    def sendKeyDown(self, key):
        keysim = self.libXtst.XStringToKeysym(str(key))
        keycode = self.libXtst.XKeysymToKeycode(self.display, keysim)
        self.libXtst.XTestFakeKeyEvent(self.display, keycode, self.X_True, self.X_CurrentTime)
        self.libXtst.XFlush(self.display)
        return True

    def sendKeyUp(self, key):
        keysim = self.libXtst.XStringToKeysym(str(key))
        keycode = self.libXtst.XKeysymToKeycode(self.display, keysim)
        self.libXtst.XTestFakeKeyEvent(self.display, keycode, self.X_False, self.X_CurrentTime)
        self.libXtst.XFlush(self.display)
        return True

    def sendTouchMove(self, X, Y):
        self.libXtst.XTestFakeButtonEvent(self.display, 1, self.X_True, self.X_CurrentTime)
        self.libXtst.XTestFakeMotionEvent(self.display, self.current_screen, int(X), int(Y), self.X_CurrentTime)
        self.libXtst.XTestFakeButtonEvent(self.display, 1, self.X_False, self.X_CurrentTime)
        self.libXtst.XFlush(self.display)
        return True

    def sendTouchDown(self, X, Y):
        self.libXtst.XTestFakeMotionEvent(self.display, self.current_screen, int(X), int(Y), self.X_CurrentTime)
        self.libXtst.XTestFakeButtonEvent(self.display, 1, self.X_True, self.X_CurrentTime)
        self.libXtst.XFlush(self.display)
        return True

    def sendTouchUp(self, X, Y):
        self.libXtst.XTestFakeMotionEvent(self.display, self.current_screen, int(X), int(Y), self.X_CurrentTime)
        self.libXtst.XTestFakeButtonEvent(self.display, 1, self.X_False, self.X_CurrentTime)
        self.libXtst.XFlush(self.display)
        return True

    def sendType(self, string):
        for character in string:
            keysim = self.libXtst.XStringToKeysym(str(character))
            keycode = self.libXtst.XKeysymToKeycode(self.display, keysim)
            self.libXtst.XTestFakeKeyEvent(self.display, keycode, self.X_True, self.X_CurrentTime)
            self.libXtst.XTestFakeKeyEvent(self.display, keycode, self.X_False, self.X_CurrentTime)
            self.libXtst.XFlush(self.display)
        return True

    def sendTap(self, X, Y):
        self.libXtst.XTestFakeMotionEvent(self.display, -1, int(X), int(Y), self.X_CurrentTime)
        self.libXtst.XTestFakeButtonEvent(self.display, 1, self.X_True, self.X_CurrentTime)
        self.libXtst.XTestFakeButtonEvent(self.display, 1, self.X_False, self.X_CurrentTime)
        self.libXtst.XFlush(self.display)
        return True

    def recvScreenshot(self, filename):
        # Variables needed in order to invoke the XGetGeometry function
        self.current_screen = self.libX11.XDefaultScreen(self.display)
        root_window = self.libX11.XRootWindow(self.display, self.current_screen)
        ref = ctypes.byref
        __rw = ctypes.c_uint(0)
        __x = ctypes.c_int(0)
        __y = ctypes.c_int(0)
        root_width = ctypes.c_uint(0)
        root_height = ctypes.c_uint(0)
        __bwidth = ctypes.c_uint(0)
        root_depth = ctypes.c_uint(0)
        
        # Return the root window and the current geometry of the drawable.	
        self.libX11.XGetGeometry(self.display, root_window, ref(__rw), ref(__x), ref(__y),ref(root_width), ref(root_height), ref(__bwidth), ref(root_depth))

        # Get the screenshot
        shot_p = self.libX11.XGetImage(self.display, root_window, 0, 0, root_width, root_height, self.libX11.XAllPlanes(), self.X_ZPixmap)
        shot = shot_p[0]

        # Create a string representation of the image residing in memory and convert it to RGB format
        data = ctypes.string_at(shot.data, shot.height * shot.bytes_per_line)
        fmbtgti.eye4graphics.bgrx2rgb(data, shot.width, shot.height)

        # Create a PPM header and then convert to PNG
        ppm_header = "P6\n%d %d\n%d\n" % (shot.width, shot.height, 255)
        Image(blob=ppm_header+data).save(filename=filename+".png")

        self.libX11.XDestroyImage(shot_p)
        return True
