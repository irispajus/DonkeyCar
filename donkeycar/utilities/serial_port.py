import logging
import serial
import serial.tools.list_ports
import time
from typing import Tuple

logger = logging.getLogger(__name__)

class SerialPort:
    """
    Wrapper for serial port connect/read/write.
    Use this rather than raw pyserial api.
    It provides a layer that automatically 
    catches exceptions and encodes/decodes
    between bytes and str.  
    It also provides a layer of indirection 
    so that we can mock this for testing.
    """
    def __init__(self, port:str='/dev/ttyACM0', baudrate:int=115200, bits:int=8, parity:str='N', stop_bits:int=1, charset:str='ascii', timeout:float=0.1):
        self.port = port
        self.baudrate = baudrate
        self.bits = bits
        self.parity = parity
        self.stop_bits = stop_bits
        self.charset = charset
        self.timeout = timeout
        self.ser = None

    def start(self):
        for item in serial.tools.list_ports.comports():
            logger.info(item)  # list all the serial ports
        self.ser = serial.Serial(self.port, self.baudrate, self.bits, self.parity, self.stop_bits, timeout=self.timeout)
        logger.debug("Opened serial port " + self.ser.name)
        return self

    def stop(self):
        if self.ser is not None:
            sp = self.ser
            self.ser = None
            sp.close()
        return self

    def buffered(self) -> int:
        """
        return: the number of buffered characters
        """
        if self.ser is None or not self.ser.is_open:
            return 0

        try:
            return self.ser.in_waiting
        except serial.serialutil.SerialException:
            return 0

    def clear(self):
        """
        Clear the serial read buffer
        """
        try:
            if self.ser is not None and self.ser.is_open:
                self.ser.reset_input_buffer()
        except serial.serialutil.SerialException:
            pass
        return self

    def readBytes(self, count:int=0) -> Tuple[bool, bytes]:
        """
        if there are characters waiting, 
        then read them from the serial port
        bytes: number of bytes to read 
        return: tuple of
                bool: True if count bytes were available to read, 
                      false if not enough bytes were avaiable
                bytes: string string if count bytes read (may be blank), 
                       blank if count bytes are not available
        """
        if self.ser is None or not self.ser.is_open:
            return (False, b'')

        try:
            input = ''
            waiting = self.buffered() >= count
            if waiting:   # read the serial port and see if there's any data there
                input = self.ser.read(count)
            return (waiting, input)
        except (serial.serialutil.SerialException, TypeError):
            logger.warning("failed reading bytes from serial port")
            return (False, b'')

    def read(self, count:int=0) -> Tuple[bool, str]:
        """
        if there are characters waiting, 
        then read them from the serial port
        bytes: number of bytes to read 
        return: tuple of
                bool: True if count bytes were available to read, 
                      false if not enough bytes were available
                str: ascii string if count bytes read (may be blank), 
                     blank if count bytes are not available
        """
        ok, bytestring = self.readBytes(count)
        try:
            return (ok, bytestring.decode(self.charset))
        except UnicodeDecodeError:
            # the first read often includes mis-framed garbage
            return (False, "")

    def readln(self) -> Tuple[bool, str]:
        """
        if there are characters waiting, 
        then read a line from the serial port.
        This will block until end-of-line can be read.
        The end-of-line is included in the return value.
        return: tuple of
                bool: True if line was read, false if not
                str: line if read (may be blank), 
                     blank if not read
        """
        if self.ser is None or not self.ser.is_open:
            return (False, "")

        try:
            input = ''
            waiting = self.buffered() > 0
            if waiting:   # read the serial port and see if there's any data there
                buffer = self.ser.readline()
                input = buffer.decode(self.charset)
            return (waiting, input)
        except (serial.serialutil.SerialException, TypeError):
            logger.warning("failed reading line from serial port")
            return (False, "")
        except UnicodeDecodeError:
            # the first read often includes mis-framed garbage
            logger.warning("failed decoding unicode line from serial port")
            return (False, "")

    def writeBytes(self, value:bytes):
        """
        write byte string to serial port
        """
        if self.ser is not None and self.ser.is_open:
            try:
                self.ser.write(value)  
            except (serial.serialutil.SerialException, TypeError):
                logger.warning("Can't write to serial port")

    def write(self, value:str):
        """
        write string to serial port
        """
        self.writeBytes(value.encode())

    def writeln(self, value:str):
        """
        write line to serial port
        """
        self.write(value + '\n')

