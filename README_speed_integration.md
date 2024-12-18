This is a project to integrate a infrared speed sensor to DonkeyCar (version 4.3.22) and regulate throttle based on current speed. Since battery runs out during the driving and the thottle value is not adjusted a StepSpeedController from Autorope DonkeyCar velocity.py, branch 5483490 and additional new script sensordata.py were introduced. 

For running this code and driving the car, manage.py is used. To incorporate the StepSpeedController run a command: python manage.py drive --js --type=velocity. The terminal outputs the values for timestamp, current speed, target speed and current throttle. 

Changes and parts essential to this project outcome.

New sketched loaded to Raspberry Pi:
- velocity.py (handles speed regulation)
- sensordata.py (reads data from Arduino nano, sensor)
- serial_port.py (additional code to support data reading from serial port)
- usb_test.py (optional script to test how and if the Arduino nano sends the data from sensor correctly)

Modified script (recommended to be used from DonkeyCar version 5.0 and add the modifications)
- complete.py (used entirely new version from 5.0)
- manage.py (added StepSpeedController, VelocityNormalize, ArduinoSpeedReader)

Additional scripts loaded, some are just needed to complete the scripts downloaded from version 5.0
- odometer.py
- tachometer.py
- kinematics.py

Current behaviour:
![image (1)](https://github.com/user-attachments/assets/34dd9a5a-22c5-41f2-8ab1-480adde477ca)

Suggested steps to impove the behaviour:
- Detemine the behavior or sensordata.py and the fluctuation of the speed data
- Intruduce PIDController to compensate the oscillation
- Would be ideal to use parts from DonkeyCar version 5.0, understand the pipline and intruduce odometer.py, tachometer.py and kinematics properly to manage.py
