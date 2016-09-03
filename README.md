# RSMapPi
RSMap Raspberry Pi repository

## Vehicle sound detector

This module collect sound noise and try to identify vehicles.

### Instructions for run

In order to run, **Python 3.4.2** or greather must be installed.

Dependencies are in **requirements.txt** for install it use:

*tip: install it under virtualenv*.

```bash
pip install -r requirements.txt
```

After this, you'll be able to run it with

```bash
python VehicleAnalyzer.py
```

## Data sender

This Java class reads data from socket which is feeded by *analyzer/VehicleDetection.py*. Both have to run in the same machine, in other case *VehicleDetection.py* must be configured with the correct ip address.

### Instructions for compile DataSender

In order to compile, **Java 8** must be installed.

```bash
javac -cp kaa-java-ep-sdk.jar DataSender.java
```

### Instructions for run DataSender
Run DataSender

```bash
java -cp .:./kaa-java-ep-sdk.jar:log4j-over-slf4j-1.7.7.jar:logback-classic-1.1.2.jar:logback-core-1.1.2.jar DataSender
```
