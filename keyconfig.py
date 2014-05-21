import json
import logging
import os

from Xlib import XK


class XLeaprConfig(object):

    def __init__(self, display, path=os.path.join(os.path.dirname(os.path.realpath(__file__)), "default.json")):
        self.config = {}

        # Load and parse JSON config
        with open(path) as data_file:
            raw_config = json.load(data_file)

        # Iterate through the items in the object
        for dkey, value in raw_config.iteritems():

            # If a value is not a list type, ignore it
            if type(value) is not list:
                logging.error("Key configurations must be listed in arrays.")
                continue

            # Convert all of the key strings into their proper codes
            self.config[dkey] = []
            for key in value:
                code = XK.string_to_keysym(key)

                # If the returned code is 0, then it could not be found by XK
                if code is 0:
                    self.config[dkey] = None
                    logging.warning("Key ("+code+") was not recognized by XK")
                    break
                else:
                    self.config[dkey].append(display.keysym_to_keycode(code))

    # Return the keycode for the specified gesture
    def __getitem__(self, gesture):
        return self.config.get(gesture, [])
