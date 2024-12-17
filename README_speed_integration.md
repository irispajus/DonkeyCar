This is a project to intagrate a infrared speed sensor to DonkeyCar (version 4.3.22) and regulate throttle based on current speed. Since battery runs out during the driving and the thottle value is not adjusted a StepSpeedController from Autorope DonkeyCar velocity.py from branch 5483490 and additional new sketch sensordata.py were introduced. 

For running this code and driving the car, manage.py is used. To incorporate the StepSpeedController run a command: python manage.py drive --js --type=velocity. The terminal outputs the values for timestamp, current speed, target speed and current throttle. 

Changes and parts essential to this project outcome.

New sketched loaded to Raspberry Pi:
- velocity.py
- sensordata.py
- serial_port.py

Modified sketches (recommended to be used from DonkeyCar version 5.0 and add the modifications)
- complete.py (used entirely new version from 5.0)
- manage.py (added StepSpeedController, VelocityNormalize, StepSpeedController)

Additional sketches loaded, some are just needed to complete the sketches downloaded from version 5.0
- odometer.py
- tachometer.py
- kinematics.py

![image (1)](https://github.com/user-attachments/assets/34dd9a5a-22c5-41f2-8ab1-480adde477ca)

