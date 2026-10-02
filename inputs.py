import ctypes
import time
import sys

# Win32 SendInput API Structures & Constants for DirectX / Minecraft 1.21
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]

class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort)
    ]

class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]

class Input_I(ctypes.Union):
    _fields_ = [
        ("ki", KeyBdInput),
        ("mi", MouseInput),
        ("hi", HardwareInput)
    ]

class Input(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("ii", Input_I)
    ]

# Input Types
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

# Key Flags
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

# Mouse Flags
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MOVE = 0x0001

# DirectInput Hardware Scan Codes
SCANCODES = {
    'w': 0x11,
    'a': 0x1E,
    's': 0x1F,
    'd': 0x20,
    'space': 0x39,
    'shift': 0x2A,
    'f': 0x21,
    '1': 0x02,
    '2': 0x03,
    '3': 0x04,
    '4': 0x05,
    '5': 0x06,
    '6': 0x07,
    '7': 0x08,
    '8': 0x09,
    '9': 0x0A,
    'esc': 0x01
}

def _send_input(inp):
    ctypes.windll.user32.SendInput(1, ctypes.pointer(inp), ctypes.sizeof(inp))

class DirectInputController:
    """DirectInput Controller providing 100% reliable input simulation for Minecraft 1.21"""

    @staticmethod
    def press_key(key_str: str):
        key_str = key_str.lower()
        scan_code = SCANCODES.get(key_str)
        if scan_code is None:
            return
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, scan_code, KEYEVENTF_SCANCODE, 0, ctypes.pointer(extra))
        x = Input(INPUT_KEYBOARD, ii_)
        _send_input(x)

    @staticmethod
    def release_key(key_str: str):
        key_str = key_str.lower()
        scan_code = SCANCODES.get(key_str)
        if scan_code is None:
            return
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(0, scan_code, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
        x = Input(INPUT_KEYBOARD, ii_)
        _send_input(x)

    @staticmethod
    def tap_key(key_str: str, duration: float = 0.05):
        DirectInputController.press_key(key_str)
        time.sleep(duration)
        DirectInputController.release_key(key_str)

    @staticmethod
    def hold_key(key_str: str, duration: float):
        DirectInputController.press_key(key_str)
        time.sleep(duration)
        DirectInputController.release_key(key_str)

    @staticmethod
    def mouse_left_down():
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        _send_input(x)

    @staticmethod
    def mouse_left_up():
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        _send_input(x)

    @staticmethod
    def click_left(hold_time: float = 0.1):
        DirectInputController.mouse_left_down()
        time.sleep(hold_time)
        DirectInputController.mouse_left_up()

    @staticmethod
    def mouse_right_down():
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTDOWN, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        _send_input(x)

    @staticmethod
    def mouse_right_up():
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTUP, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        _send_input(x)

    @staticmethod
    def click_right(hold_time: float = 0.1):
        DirectInputController.mouse_right_down()
        time.sleep(hold_time)
        DirectInputController.mouse_right_up()

    @staticmethod
    def move_mouse(dx: int, dy: int):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.mi = MouseInput(dx, dy, 0, MOUSEEVENTF_MOVE, 0, ctypes.pointer(extra))
        x = Input(INPUT_MOUSE, ii_)
        _send_input(x)

    @staticmethod
    def turn_left(amount: int = 600, steps: int = 15):
        step_dx = -int(amount / steps)
        for _ in range(steps):
            DirectInputController.move_mouse(step_dx, 0)
            time.sleep(0.015)

    @staticmethod
    def turn_right(amount: int = 600, steps: int = 15):
        step_dx = int(amount / steps)
        for _ in range(steps):
            DirectInputController.move_mouse(step_dx, 0)
            time.sleep(0.015)

    @staticmethod
    def release_all():
        """Emergency release of all movement and mouse buttons"""
        for k in SCANCODES:
            DirectInputController.release_key(k)
        DirectInputController.mouse_left_up()
        DirectInputController.mouse_right_up()

