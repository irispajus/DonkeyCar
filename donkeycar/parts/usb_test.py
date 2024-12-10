import serial
import time

def test_arduino_encoder(port='/dev/ttyUSB0', baudrate=115200, timeout=1.0):
    """
    Test USB communication with the Arduino encoder sketch.
    
    - Sends commands to Arduino to test encoder functionality.
    - Reads and prints the incoming data.
    
    :param port: The USB port to connect to (e.g., '/dev/ttyUSB0' or 'COM3').
    :param baudrate: Baud rate for the serial connection (default: 115200).
    :param timeout: Timeout for the serial connection in seconds (default: 1.0).
    """
    try:
        # Initialize the serial connection
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        print(f"Connected to {port} at {baudrate} baud.")

        # Give the device some time to initialize
        time.sleep(2)

        # Reset encoder ticks (send 'r' command)
        ser.write(b"r\n")
        print("Sent 'r' command to reset encoder ticks.")
        time.sleep(0.5)

        # Start continuous mode with a delay of 500ms (send 'c500' command)
        ser.write(b"c500\n")
        print("Sent 'c500' command to start continuous mode with 500ms delay.")
        
        print("Listening for data... (Press Ctrl+C to exit)")
        while True:
            try:
                # Read data from Arduino
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"Received: {line}")
            except UnicodeDecodeError as e:
                print(f"Decoding error: {e}. Raw data ignored.")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if 'ser' in locals() and ser.is_open:
            # Stop continuous mode (send 'c' command)
            ser.write(b"c\n")
            print("Sent 'c' command to stop continuous mode.")
            ser.close()
            print("Serial port closed.")

if __name__ == '__main__':
    # Update the port and baudrate as necessary for your setup
    test_arduino_encoder(port='/dev/ttyUSB0', baudrate=115200)

