import serial
import time
import logging

# Configuration
SERIAL_PORT = '/dev/ttyUSB0'  # Update with your serial port
BAUD_RATE = 115200
MM_PER_TICK = 12.25  # Distance moved per tick in millimeters
TICK_INTERVAL = 0.1  # Time interval to calculate speed in seconds

# Set up logging
#logging.basicConfig(level=logging.INFO)

# Create a logger specific to this module
logger = logging.getLogger(__name__)  # Use the module name as the logger name

# Set up a handler to control formatting
handler = logging.StreamHandler()  # Output to console
formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)

# Attach the handler to the logger
logger.addHandler(handler)

# Set the logger level
logger.setLevel(logging.INFO)

# Ensure the logger doesn't propagate messages to parent loggers (prevents duplicates)
logger.propagate = False

class ArduinoSpeedReader:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.last_ticks = 0  # Track the last known tick count
        self.last_time = time.time()  # Track the last update time
        self.speed = 0.0  # Store the current speed

        # Initialize the serial connection
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        except serial.SerialException as e:
            #logging.error(f"Failed to open serial port: {e}")
            raise

        self.start_continuous_mode()

    def start_continuous_mode(self):
        """Send the command to Arduino to start sending data at regular intervals."""
        try:
            self.ser.write(b'c50\n')  # Command to start continuous data transmission
            #logging.info("Started continuous mode on Arduino.")
        except Exception as e:
            pass
            #logging.error(f"Failed to send continuous mode command: {e}")

    def get_actual_speed(self):
        """Retrieve and calculate speed from Arduino data."""
        try:
            # Ensure continuous mode is active
            self.start_continuous_mode()

            # Read and decode a line from the serial port
            if self.ser.in_waiting > 0:
                line = self.ser.readline().decode().strip()
                if line:
                    try:
                        # Parse ticks and timestamp
                        ticks, _ = map(int, line.split(','))
                        current_time = time.time()

                        # Calculate speed if this is not the first data
                        if self.last_ticks is not None:
                            time_elapsed = current_time - self.last_time

                            # Update speed if enough time has passed
                            if time_elapsed >= TICK_INTERVAL:
                                distance_covered = (ticks - self.last_ticks) * MM_PER_TICK / 1000
                                self.speed = distance_covered / time_elapsed
                                self.last_time = current_time

                        # Update last_ticks unconditionally
                        self.last_ticks = ticks

                    except ValueError:
                        pass
                        #logging.warning(f"Malformed data received: {line}")

        except Exception as e:
            pass
            #logging.error(f"Error reading from serial port: {e}")

        # Return the current speed
        return self.speed

    def run(self):
        """Called to update speed and return it as output."""
        return self.get_actual_speed()

    def close(self):
        """Close the serial connection."""
        if self.ser.is_open:
            self.ser.close()
            logging.info("Serial connection closed.")


if __name__ == "__main__":
    try:
        # Initialize Arduino speed reader
        arduino_reader = ArduinoSpeedReader(port=SERIAL_PORT, baudrate=BAUD_RATE)

        # Continuously fetch and log speed
        while True:
            speed_mps = arduino_reader.run()
            logger.info(f"Speed: {speed_mps:.2f} m/s")
            time.sleep(0.1)  # Avoid excessive CPU usage
    except KeyboardInterrupt:
        logging.info("Stopping speed calculation.")
    finally:
        if 'arduino_reader' in locals():
            arduino_reader.close()


