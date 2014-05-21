XLeapr
=========

My own Leap Motion X window management script. Loosely based off of DesktopLeapr.

## Recognized Gestures

* Swipe (up/down/left/right)
* Flip hand (palm up/palm down)
* Clap

## Command Configuration

The keypresses initiated by the gestures can be changed with a configuration file.

Example:
```json
{
   "flip":["Alt_L", "Tab"],
   "swipe":["Control_L", "Alt_L"],
   "clap":["Control_L", "Alt_L", "l"]
}
```

The keys are all based on their corresponding Xlib enum names. You can find them all here:

https://github.com/Ademan/python-xlib-branch/tree/master/Xlib/keysymdef

## Future Work

* Crunch (In progress, buggy)
* Spin (In progress, buggy)
* Spirit fingers (One day...)
