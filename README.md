# CAN Test Sender

A python program for a test task  
Includes SocketCAN / ISO-TP communication, I2C scanning, and LED control

## Requirements

### 1. System 
The program runs on Linux, with kernel support for CAN-ISOTP and I2C

### 2. Python 

* Python Interpreter, 3.9 or higher 

* Python Packages:
```text
can-isotp python-can smbus2 gpiozero
```

## Data flow:

```text
[input.txt] ---> FileReader ----> BufferEditor ----> CANController (Rx: 0x700, Tx: 0x701) ----> vcan0
                                                           |
[I2C Bus] -----> I2CScanner -----------------------> CANController (Rx: 0x702, Tx: 0x703) ----> vcan0
                                      │
[GPIO 17] <----- LEDController <------- (LED Mode)
```

## Component Logic

### Main application

Serves as the main orchestrator for application tasks:

* Sets up logging
* Reads content from an input file [Input.txt]
* Passes the content to BufferEditor to insert spaces every 4 characters
* Initializes the CANController on vcan0
* Sends the formatted text via ISO-TP (Rx: 0x700, Tx: 0x701)
* Scans active I2C addresses every 60 seconds
* Sends the scan result(s) via ISO-TP (Rx: 0x702, Tx: 0x703)
* Blinks the status LED on GPIO #17 at 1Hz (Normal) by default, and at 4Hz (Fast) when I2C scan starts

### CAN Controller
Used to communicate over vcan0 using linux socketCAN and ISO-TP standard 

* Socket Registry: Dynamically binds, reuses, and manages ISO-TP sockets for target address pairs
* send(): Transmits raw binary payloads over an initialized ISO-TP socket
* receive(): Receives incoming ISO-TP multi-frame payloads

### LED Controller
Manages status LED states and frequency changes

* set_mode(), set_mode_for_period() : Sets LED behavior (Normal or Fast)
* blink(): Toggles LED on and off according to active mode

### I2C Scanner
Scans I2C devices similar to the Linux i2cdetect tool

* scan(): Probes active I2C bus addresses and returns a list of detected devices
* scan_to_str(): Formats detected addresses into an easily readable grid table

### Utilities
Used to modify strings
* FileReader: Asynchronously reads raw file content from disk
* BufferEditor: Modifies payload strings (e.g., adding spaces every 4 characters) before binary transmission
