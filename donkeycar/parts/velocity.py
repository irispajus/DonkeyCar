import math
import logging
from donkeycar.utils import map_frange, sign, clamp

#Setting up the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(ch)

class VelocityNormalize:
    """
    Normalize a velocity into the range 0..1.0
    given the measured minimum and maximum speeds.
    @param min_speed: speed below which car stalls
    @param max_speed: car's top speed (may be a target, not a limit)
    @param min_normal_speed: the normalized throttle corresponding to min_speed
    """
    def __init__(self, min_speed: float, max_speed: float, min_normal_speed: float = 0.1) -> None:
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.min_normal_speed = min_normal_speed

    def run(self, speed: float) -> float:
        s = sign(speed)
        speed = abs(speed)
        if speed < self.min_speed:
            logger.debug(f"Speed {speed} below min_speed {self.min_speed}, returning 0.0")
            return 0.0
        if speed >= self.max_speed:
            logger.debug(f"Speed {speed} >= max_speed {self.max_speed}, returning 1.0")
            return s * 1.0
        normalized_speed = s * map_frange(speed, self.min_speed, self.max_speed, self.min_normal_speed, 1.0)
        logger.debug(f"Normalized speed: {normalized_speed}")
        return normalized_speed

    def shutdown(self):
        logger.debug("Shutting down VelocityNormalize")


class VelocityUnnormalize:
    """
    Map normalized speed (0 to 1) to actual speed
    """
    def __init__(self, min_speed: float, max_speed: float, min_normal_speed: float = 0.1) -> None:
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.min_normal_speed = min_normal_speed

    def run(self, speed: float) -> float:
        s = sign(speed)
        speed = abs(speed)
        if speed < self.min_normal_speed:
            logger.debug(f"Normalized speed {speed} below min_normal_speed {self.min_normal_speed}, returning 0.0")
            return 0.0
        if speed >= 1.0:
            logger.debug(f"Normalized speed {speed} >= 1.0, returning 1.0")
            return s * 1.0
        actual_speed = s * map_frange(speed, self.min_normal_speed, 1.0, self.min_speed, self.max_speed)
        logger.debug(f"Normalized speed: {speed} Unnormalized speed: {actual_speed}")
        return actual_speed

    def shutdown(self):
        logger.debug("Shutting down VelocityUnnormalize")


class StepSpeedController:
    """
    Simplistic constant step controller.
    Just increases speed if we are too slow
    or decreases speed if we are too fast.
    Includes feed-forward when reversing direction
    or starting from stopped.
    """
    def __init__(self, min_speed: float, max_speed: float, throttle_step: float = 1 / 255, min_throttle: float = 0) -> None:
        """
        @param min_speed is speed below which vehicle stalls (so slowest stable working speed)
        @param max_speed is speed at maximum throttle
        @param throttle_steps is number of steps in working range of throttle (min_throttle to 1.0)
        @param min_throttle is throttle that corresponds to min_speed; the throttle below which the vehicle stalls.
        """
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.min_throttle = min_throttle
        self.step_size = throttle_step
        self.prev_throttle = 0
        self.logger = logging.getLogger(__name__)  # Logger for StepSpeedController

    def run(self, throttle: float, speed: float, target_speed: float) -> float:
        """
        Given current throttle and speed and a target speed,
        calculate a new throttle to attain target speed
        """
        self.logger.debug(f"Running StepSpeedController - Current Speed: {speed}, Target Speed: {target_speed}")

        if speed is None or target_speed is None:
            # no speed to control, just return throttle
            self.logger.debug(f"Speed or target_speed is None. Returning previous throttle: {self.prev_throttle}")
            return self.prev_throttle

        target_direction = sign(target_speed)
        direction = sign(speed)

        target_speed = abs(target_speed)
        speed = abs(speed)

        if target_speed < self.min_speed:
            self.logger.debug(f"Target speed {target_speed} below min_speed {self.min_speed}. Returning 0")
            return 0

        # When changing direction or starting from stopped, calculate a feed-forward throttle estimate
        #if direction != target_direction:
        #    if speed > self.min_speed:
        #        self.logger.debug(f"Speed {speed} > min_speed {self.min_speed}, slowing down first.")
        #        return 0
        #    estimated_throttle = target_direction * map_frange(target_speed, self.min_speed, self.max_speed, self.min_throttle, 1.0)
        #    self.logger.debug(f"Changing direction, estimated throttle: {estimated_throttle}")
        #    return estimated_throttle

        # Adjust throttle based on speed comparison with target_speed
        throttle = self.prev_throttle
        self.logger.debug(f"Current throttle: {throttle}")

        if speed > target_speed:
            # Too fast, slow down
            throttle -= self.step_size
            self.logger.debug(f"Speed is greater than target, reducing throttle to: {throttle}")
        elif speed < target_speed:
            # Too slow, speed up
            throttle += self.step_size
            self.logger.debug(f"Speed is less than target, increasing throttle to: {throttle}")

        self.prev_throttle = throttle
        self.logger.debug(f"New throttle value: {self.prev_throttle}")
        return target_direction * throttle

    def shutdown(self):
        self.logger.debug("Shutting down StepSpeedController")


class PIDSpeedController:
    """
    Part to smoothly adjust steering.
    """
    def __init__(self, kp=1.1, ki=0.07, kd=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0
        self.prev_speed = 0.0
        self.min_speed = 0.2
        self.logger = logging.getLogger(__name__)  # Logger for PIDSpeedController

    def run(self, throttle: float, target_speed: float, current_speed: float):
        """
        Take in current speed from encoder data as well as target speed from model
        and adjust throttle accordingly.
        """
        self.logger.debug(f"Running PIDSpeedController - Target Speed: {target_speed}, Current Speed: {current_speed}")

        if current_speed is None or target_speed is None:
            # no speed to control, just return throttle
            self.logger.debug(f"Current speed or target speed is None. Returning throttle: {throttle}")
            return throttle

        if current_speed == 0.0:
            current_speed = self.prev_speed
        else:
            self.prev_speed = current_speed

        if self.integral > 0.5:
            self.integral = 0.5

        error = target_speed - current_speed
        self.integral += error
        derivative = error - self.prev_error
        self.prev_error = error
        result = clamp(self.kp * error + self.ki * self.integral + self.kd * derivative, -1.0, 1.0)

        if 0 <= self.min_speed <= self.min_speed:
            self.logger.debug(f"Speed is too slow, returning min_speed: {self.min_speed}")
            return self.min_speed
        else:
            self.logger.debug(f"PID result: {result}")
            return result

    def shutdown(self):
        self.logger.debug("Shutting down PIDSpeedController")

