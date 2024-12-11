MM1_STEERING_MID = 1550
MM1_MAX_FORWARD = 1620  # Max is 2000
MM1_MAX_REVERSE = 1350
MM1_STOPPED_PWM = 1500
MM1_SHOW_STEERING_VALUE = False
MM1_SERIAL_PORT = '/dev/ttyS0'

THROTTLE_FORWARD_PWM = 430      #pwm value for max forward throttle
THROTTLE_STOPPED_PWM = 370      #pwm value for no movement
THROTTLE_REVERSE_PWM = 320      #pwm value for max reverse throttle

DRIVE_TRAIN_TYPE = "MM1"

JOYSTICK_MAX_THROTTLE = 1.0
JOYSTICK_THROTTLE_DIR = -1.0

CONTROLLER_TYPE='F710'           #(ps3|ps4)
DRIVE_LOOP_HZ = 20

if (CONTROLLER_TYPE=='F710'):
    JOYSTICK_DEADZONE = 0.1

AUTO_CREATE_NEW_TUB = True


HAVE_ODOM = True
HAVE_ODOM_2 = False
ENCODER_TYPE = 'arduino'

PULSES_PER_REVOLUTION = 20
ENCODER_PPR = 20
ENCODER_DEBOUNCE_NS = 0

FORWARD_ONLY = 1
FORWARD_REVERSE = 2
FORWARD_REVERSE_STOP = 3
TACHOMETER_MODE=FORWARD_REVERSE

MM_PER_TICK = 0.078 * 3.141592653589793 * 1000 / ENCODER_PPR
ODOM_SERIAL_BAUDRATE = 115200
ODOM_SERIAL = '/dev/ttyUSB0'
ODOM_SMOOTHING = 1
ODOM_DEBUG = False

AXLE_LENGTH = 0.03     # length of axle; distance between left and right wheels in meters
WHEEL_BASE = 0.1       # distance between front and back wheels in meters
WHEEL_RADIUS = 0.039  # radius of wheel in meters
MIN_SPEED = 0.1        # minimum speed in meters per second; speed below which car stalls
MAX_SPEED = 3.0        # maximum speed in meters per second; speed at maximum throttle (1.0)
MIN_THROTTLE = 0.1     # throttle (0 to 1.0) that corresponds to MIN_SPEED, throttle below which car stalls
MAX_STEERING_ANGLE = 3.141592653589793 / 4  # for car-like robot; maximum steering angle in radians (corresponding to tire angle at steering == -1)


