#! /usr/bin/env python

import Leap, os, sys
from Xlib import X, display, ext, XK
from keyconfig import XLeaprConfig


class XLeapr(Leap.Listener):
    swipe_lock = 0
    hand_down = 0
    hand_up = 0
    hand_dist = 0
    crunch = 0

    disp = display.Display()

    leftkey = disp.keysym_to_keycode(XK.XK_Left)
    rightkey = disp.keysym_to_keycode(XK.XK_Right)
    upkey = disp.keysym_to_keycode(XK.XK_Up)
    downkey = disp.keysym_to_keycode(XK.XK_Down)

    def __init__(self, configpath=os.path.join(os.path.dirname(os.path.realpath(__file__)), "default.json")):
        super(XLeapr, self).__init__()

        self.config = XLeaprConfig(XLeapr.disp, configpath)

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_disconnect(self, controller):
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        currentframe = controller.frame()

        #Swipe
        if XLeapr.swipe_lock != 0:
            if currentframe.timestamp - XLeapr.swipe_lock > 1e6:
                XLeapr.swipe_lock = 0
        elif len(currentframe.hands) is 1:
            for gesture in currentframe.gestures():
                if gesture.type == Leap.Gesture.TYPE_SWIPE:
                    XLeapr.swipe_lock = currentframe.timestamp
                    swipe = Leap.SwipeGesture(gesture)
                    if swipe.direction.x > 0.75:
                        print("Swipe right: %f" % swipe.direction.x)
                        self.perform_gesture("swipe", [XLeapr.leftkey])
                    elif swipe.direction.x < -0.75:
                        print("Swipe left: %f" % swipe.direction.x)
                        self.perform_gesture("swipe", [XLeapr.rightkey])
                    elif swipe.direction.y > 0.75:
                        print("Swipe up: %f" % swipe.direction.y)
                        self.perform_gesture("swipe", [XLeapr.downkey])
                    elif swipe.direction.y < -0.75:
                        print("Swipe down: %f" % swipe.direction.y)
                        self.perform_gesture("swipe", [XLeapr.upkey])

        #Spin
        if len(currentframe.hands) is 1:
            for gesture in currentframe.gestures():
                if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                    circle = Leap.CircleGesture(gesture)
                    if circle.progress > 1:
                        if (circle.pointable.direction.angle_to(circle.normal)
                                <= Leap.PI / 2):
                            print("Spin")
                            break
                        else:
                            print("Spin counter")
                            break

        #Rotate
        if len(currentframe.hands) is 1:
            hand = currentframe.hands.rightmost.palm_normal
            if XLeapr.hand_down != 0 \
                    and currentframe.timestamp - XLeapr.hand_down < 2e6 \
                    and hand.y > 0:
                print("Hand flip up")
                self.perform_gesture("flip")
                XLeapr.hand_down = 0
            if hand.y < 0 and hand.x > -0.3 and hand.x < 0.3 \
                    and hand.z > -0.3 and hand.z < 0.3:
                XLeapr.hand_down = currentframe.timestamp

            if XLeapr.hand_up != 0 \
                    and currentframe.timestamp - XLeapr.hand_up < 2e6 \
                    and hand.y < 0:
                print("Hand flip down")
                self.perform_gesture("flip")
                XLeapr.hand_up = 0
            if hand.y > 0 and hand.x > -0.3 and hand.x < 0.3 \
                    and hand.z > -0.3 and hand.z < 0.3:
                XLeapr.hand_up = currentframe.timestamp

        #Clap
        if len(currentframe.hands) is 2:
            right = currentframe.hands.rightmost.palm_position
            left = currentframe.hands.leftmost.palm_position

            if left.distance_to(right) > 200:
                XLeapr.hand_dist = currentframe.timestamp
            elif left.distance_to(right) < 40 \
                    and currentframe.timestamp - XLeapr.hand_dist < 1.5e6:
                print("Clap")
                self.perform_gesture("clap")
                XLeapr.hand_dist = 0

        #Crunch
        #TODO Add bounds for other sides so crunch isn't accidentally called when
        # a hand leaves the zone
        if len(currentframe.hands) is 1:
            hand = currentframe.hands.rightmost
            radius = hand.sphere_radius
            depth = hand.palm_position.z

            if radius > 70:
                XLeapr.crunch = currentframe.timestamp
            elif radius < 60 and depth < 90 \
                    and currentframe.timestamp - XLeapr.crunch < 1.5e6:
                print("Crunch: %d" % radius)
                #self.crunch()
                XLeapr.crunch = 0

        XLeapr.disp.sync()
        return

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

    def perform_gesture(self, name, extra_keys=[]):
        for key in self.config[name]:
            ext.xtest.fake_input(XLeapr.disp, X.KeyPress, key)

        for key in extra_keys:
            ext.xtest.fake_input(XLeapr.disp, X.KeyPress, key)

        for key in extra_keys[::-1]:
            ext.xtest.fake_input(XLeapr.disp, X.KeyRelease, key)

        for key in self.config[name][::-1]:
            ext.xtest.fake_input(XLeapr.disp, X.KeyRelease, key)

        XLeapr.disp.flush()

    def swipe(self, direction):
        for key in self.config["swipe"]:
            ext.xtest.fake_input(XLeapr.disp, X.KeyPress, key)

        ext.xtest.fake_input(XLeapr.disp, X.KeyPress, direction)
        ext.xtest.fake_input(XLeapr.disp, X.KeyRelease, direction)

        for key in self.config["swipe"][::-1]:
            ext.xtest.fake_input(XLeapr.disp, X.KeyRelease, key)

        XLeapr.disp.flush()


def main():
    # Create a sample listener and controller
    listener = XLeapr()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.enable_gesture(Leap.Gesture.TYPE_SWIPE)
    #controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE)
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    sys.stdin.readline()

    # Remove the sample listener when done
    controller.remove_listener(listener)


if __name__ == "__main__":
    main()
