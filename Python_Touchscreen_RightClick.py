"""
Python Script for adding 1 & 2 finger multitouch gestures to implement
a right click option with Touchscreens in the Ubuntu unity environment.

This is implemented with the evdev Python library on an ELAN touchscreen.

Currently implements 2 types of right click options:
1 finger long touch: Timeout of 1.7 seconds, movement cancels action
2 finger tap: movement cancels action
"""

from evdev import InputDevice, ecodes, UInput, list_devices
from threading import Timer


class TrackedEvent(object):

    """
    Class for multitouch event tracking.
    Track position, movement, slots used (total number of fingers in gesture),
    timing of long presses, and event completion.
    """

    def __init__(self, dev, abilities, var_x, var_y):
        """ Initialize tracking attributes. """
        self.dev = dev
        self.abilities = abilities
        self.vars = {'ABS_X': var_x, 'ABS_Y': var_y}
        self.position = {'ABS_X': None, 'ABS_Y': None}
        self.fingers = 0
        self.total_event_fingers = 0
        self.discard = 0
        self.moved = 0
        self.track_start = None
        self.click_delay = 1.5

    def add_finger(self):
        """  Add a detected finger. """
        self.fingers += 1
        self.total_event_fingers = self.fingers

    def remove_fingers(self):
        """ Remove detected finger upon release. """
        if self.fingers == 1:
            print('Total Fingers used: ', self.total_event_fingers)
        self.fingers -= 1

        if (self.fingers == 0 and
                self.total_event_fingers == 2 and
                self.moved == 0):
            self.total_event_fingers = 0
            self._initiate_right_click()

        elif (self.fingers == 0 and
                self.total_event_fingers == 1 and
                self.moved == 0):
            self.total_event_fingers = 0
            try:
                self.track_start.cancel()
                self.track_start.join()
            except AttributeError:  # capture Nonetype track_start
                pass
            try:
                self.dev.ungrab()
            except OSError:  # capture case where grab was never initiated
                pass

        if self.fingers == 0:
            self.discard = 1

    def position_event(self, event_code, value):
        """ tracks position to track movement of fingers """
        if self.position[event_code] is None:
            self.position[event_code] = value
        else:
            if abs(self.position[event_code] - value) > self.vars[event_code]:
                self._moved_event()
        if (self.fingers == 1 and self.position['ABS_X'] and
                self.position['ABS_Y'] and self.track_start is None):
            self._trackit()

    def _trackit(self):
        """ start timing for long press """
        self.track_start = Timer(self.click_delay, self._long_press)
        self.track_start.start()

    def _long_press(self):
        if self.fingers == 1 and self.moved == 0:
            self._initiate_right_click()
            self.dev.grab()

    def _moved_event(self):
        """ movement detected. """
        self.moved = 1

    def _initiate_right_click(self):
        """ Internal method for initiating a right click at touch point. """
        with UInput(self.abilities) as ui:
            ui.write(ecodes.EV_ABS, ecodes.ABS_X, 0)
            ui.write(ecodes.EV_ABS, ecodes.ABS_Y, 0)
            ui.write(ecodes.EV_KEY, ecodes.BTN_RIGHT, 1)
            ui.write(ecodes.EV_KEY, ecodes.BTN_RIGHT, 0)
            ui.syn()


def initiate_gesture_find():
    """
    This function will scan all input devices until it finds an
    ELAN touchscreen. It will then enter a loop to monitor this device
    without blocking its usage by the system.
    """
    for device in list_devices():
        dev = InputDevice(device)
        if (dev.name == 'ELAN Touchscreen') or \
           (dev.name == 'Atmel Atmel maXTouch Digitizer'):
            break
    Abs_events = {}
    abilities = {ecodes.EV_ABS: [ecodes.ABS_X, ecodes.ABS_Y],
                 ecodes.EV_KEY: (ecodes.BTN_LEFT, ecodes.BTN_RIGHT)}
    # Assuming QHD screen on my Yoga 2 Pro as default for resolution measures
    res_x = 13  # touch unit resolution # units/mm in x direction
    res_y = 13  # touch unit resolution # units/mm in y direction
    # would be weird if above resolutions differed, but will treat generically
    codes = dev.capabilities()
    for code in codes:
        if code == 3:
            for type_code in codes[code]:

                human_code = ecodes.ABS[type_code[0]]
                if human_code == 'ABS_X':
                    vals = type_code[1]
                    abilities[ecodes.EV_ABS][0] = (ecodes.ABS_X, vals)
                    res_x = vals[-1]
                elif human_code == 'ABS_Y':
                    vals = type_code[1]
                    abilities[ecodes.EV_ABS][1] = (ecodes.ABS_Y, vals)
                    res_y = vals[-1]
                Abs_events[type_code[0]] = human_code
    # Average  index finger width is 16-20 mm, assume 20 mm
    # touch resolution noise assumed at 10% (5% radius), so 1.0 mm by default
    # this seemed resonable from my own trial tests
    var_x = 1.0 * res_x  # variablity in movement allowed in x direction
    var_y = 1.0 * res_y  # variablity in movement allowed in y direction

    MT_event = None
    for event in dev.read_loop():
        if event.type == ecodes.EV_ABS:
            if MT_event is None:
                MT_event = TrackedEvent(dev, abilities, var_x, var_y)
            event_code = Abs_events[event.code]
            if event_code == 'ABS_X' or event_code == 'ABS_Y':
                MT_event.position_event(event_code, event.value)
            elif event_code == 'ABS_MT_TRACKING_ID':
                if event.value == -1:
                    MT_event.remove_fingers()
                    if MT_event.discard == 1:
                        MT_event = None
                else:
                    MT_event.add_finger()


if __name__ == '__main__':
    initiate_gesture_find()
