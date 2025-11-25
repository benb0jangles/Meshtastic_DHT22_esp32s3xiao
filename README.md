![image1](https://github.com/benb0jangles/Meshtastic_DHT22_esp32s3xiao/blob/main/pics/1.jpg)

# Meshtastic DHT22 Custom Firmware for XIAO ESP32-S3 + Wio SX1262

Custom Meshtastic firmware with DHT22 temperature/humidity sensor support for the Seeed XIAO ESP32-S3 with Wio SX1262 LoRa module.

## Hardware Requirements

- **Seeed XIAO ESP32-S3** board
- **Wio SX1262 LoRa Module** expansion board (868 MHz for EU/UK)
- **DHT22 (AM2302)** temperature/humidity sensor
- 10K ohm pull-up resistor (optional - many DHT22 modules have this built-in)

### Kit Reference
- [XIAO ESP32-S3 + Wio SX1262 Kit](https://wiki.seeedstudio.com/xiao_esp32s3_&_wio_SX1262_kit_for_meshtastic/)

## DHT22 Wiring

Connect the DHT22 sensor to the XIAO ESP32-S3:

| DHT22 Pin | XIAO ESP32-S3 Pin | Description |
|-----------|-------------------|-------------|
| VCC       | 3.3V              | Power (3.3V) |
| DATA      | D3 (GPIO 4)       | Data signal |
| GND       | GND               | Ground |

```
DHT22 Wiring Diagram:
                    ┌─────────────┐
    3.3V ──────────┤ VCC         │
                   │             │
    GPIO4 (D3) ────┤ DATA    DHT22
         │         │             │
        [10K]      │             │
         │         │             │
    GND ──────────┤ GND         │
                    └─────────────┘

Note: 10K pull-up resistor between VCC and DATA
(often built into DHT22 breakout modules)
```

## XIAO ESP32-S3 Pinout Reference

```
        ┌──────────────────┐
        │    USB-C Port    │
        └──────────────────┘
    D0  │ 1            21 │ 5V
    D1  │ 2            20 │ GND
    D2  │ 3            19 │ 3.3V
    D3  │ 4  (DHT22)   18 │ D10
    D4  │ 5  (SDA)     17 │ D9 (MOSI)
    D5  │ 6  (SCL)     16 │ D8 (MISO)
    D6  │ 7  (TX)      15 │ D7 (SCK)
        └──────────────────┘

GPIO Pin Mapping:
- D0 = GPIO 1
- D1 = GPIO 2
- D2 = GPIO 3
- D3 = GPIO 4  <- DHT22 DATA
- D4 = GPIO 5  (I2C SDA)
- D5 = GPIO 6  (I2C SCL)
- D6 = GPIO 43 (UART TX)
- D7 = GPIO 44 (UART RX)
```

## Firmware Version

Based on Meshtastic firmware **2.6.11.60ec05e Beta** for the seeed-xiao-s3 variant.

## Pre-Upload Configuration

Before uploading the firmware, you should configure your device settings using one of these methods:

### Method 1: Python GUI Configuration Tool (Recommended)

Run the included Python GUI tool to easily configure settings:

```bash
cd dht22-firmware
python meshtastic_config_gui.py
```

The GUI allows you to set:
- Device Name (Long Name)
- Short Name (4 characters max)
- Region (EU_868 for UK/Europe)
- Modem Preset
- TX Power
- Device Role
- DHT22 Telemetry Settings
- Bluetooth/WiFi Connectivity

**New Pre-Install Configuration Features:**

The GUI now supports creating reusable configurations for multiple devices:

1. **Save as Pre-Install Config** - Export your configuration as a structured JSON file that can be:
   - Loaded on any fresh device using the GUI
   - Shared with other users
   - Used as templates for different node types (router, sensor, mobile, etc.)

2. **Export Setup Script** - Generate automated setup scripts that configure fresh devices with one command:
   ```bash
   # Windows
   setup_meshtastic_device.bat COM3

   # Linux/Mac
   ./setup_meshtastic_device.sh /dev/ttyUSB0
   ```

   The script automatically:
   - Tests device connection
   - Applies all configuration settings
   - Reboots the device
   - Displays a configuration summary

   Both `.sh` (Linux/Mac) and `.bat` (Windows) scripts are generated automatically.

**Workflow for Multiple Devices:**

1. Configure your desired settings in the GUI
2. Click "Save as Pre-Install Config" to save a JSON template
3. Click "Export Setup Script" to create executable scripts
4. Flash fresh firmware to new devices
5. Run the setup script on each device to apply identical configuration

This is perfect for:
- Setting up mesh networks with consistent configuration
- Deploying multiple sensor nodes with identical settings
- Quickly configuring replacement devices
- Sharing standardized configurations with team members

### Using Pre-Install Configurations

If you have a pre-install configuration file or setup script:

**Option A: Using the Setup Script (Fastest)**
```bash
# Windows
setup_meshtastic_device.bat COM3

# Linux/Mac
chmod +x setup_meshtastic_device.sh
./setup_meshtastic_device.sh /dev/ttyUSB0
```

The script will automatically:
1. Test connection to the device
2. Apply all configuration settings (name, region, modem, role, telemetry, etc.)
3. Reboot the device
4. Display a summary of applied settings

**Option B: Using the GUI with a Pre-Install Config**
1. Run `python meshtastic_config_gui.py`
2. Click "Load Config"
3. Select your `meshtastic_preinstall_config.json` file
4. Click "Apply to Device" to send the configuration
5. The device will reboot automatically

**Example Pre-Install Config Files:**

You can create different configuration templates for different node types:

- `router_node_config.json` - Fixed router with WiFi enabled
- `mobile_node_config.json` - CLIENT role with Bluetooth only
- `sensor_node_config.json` - SENSOR role with aggressive power saving
- `allotment_monitor_config.json` - DHT22 telemetry every 5 minutes

### Method 2: Post-Flash Configuration via CLI

After flashing, configure via USB:

```bash
# Connect and verify device
meshtastic --port COM3 --info

# Set device name
meshtastic --port COM3 --set-owner "Your Node Name"
meshtastic --port COM3 --set-owner-short "NODE"

# Set region (CRITICAL for UK)
meshtastic --port COM3 --set lora.region EU_868

# Set TX power
meshtastic --port COM3 --set lora.tx_power 22

# Set modem preset
meshtastic --port COM3 --set lora.modem_preset LONG_FAST

# Set device role
meshtastic --port COM3 --set device.role CLIENT

# Enable environmental telemetry (for DHT22)
meshtastic --port COM3 --set telemetry.environment_measurement_enabled true
meshtastic --port COM3 --set telemetry.environment_update_interval 300
```

### Method 3: Meshtastic App Configuration

After flashing, connect via Bluetooth or USB and use:
- **Android**: Meshtastic app from Google Play
- **iOS**: Meshtastic app from App Store
- **Web**: https://client.meshtastic.org

## How to Upload Firmware

### Option A: Meshtastic Web Flasher (Easiest)

1. **Enter Bootloader Mode:**
   - Press and hold the **BOOT** button on the XIAO ESP32-S3
   - While holding BOOT, connect the USB-C cable to your computer
   - Release BOOT after 1 second
   - The device should appear as a USB drive

2. **Open Web Flasher:**
   - Visit: https://flasher.meshtastic.org/
   - Use Chrome or Edge browser (WebSerial support required)

3. **Select Device:**
   - Choose "Seeed XIAO S3" from the device list

4. **Upload Custom Firmware:**
   - Click the **folder icon** or "Load local firmware" button
   - Navigate to the compiled `.bin` firmware file
   - Or upload the firmware `.zip` package

5. **Flash Settings:**
   - Enable "Full Erase and Install" for a clean flash
   - Click "Flash"

6. **Wait for Completion:**
   - Do not disconnect until flashing is complete
   - Device will reboot automatically

### Option B: ESPTool CLI

```bash
# Install esptool
pip install esptool

# Enter bootloader mode (hold BOOT, plug USB, release)

# Find your COM port
# Windows: Check Device Manager
# Linux: ls /dev/ttyUSB* or /dev/ttyACM*

# Flash firmware (adjust COM port as needed)
esptool.py --chip esp32s3 --port COM3 --baud 921600 \
    --before default_reset --after hard_reset \
    write_flash -z 0x0 firmware-seeed-xiao-s3.bin
```

### Option C: PlatformIO (For Development)

If building from source:

```bash
cd meshtastic-firmware
pio run -e seeed-xiao-s3 -t upload
```

## Verifying DHT22 is Working

After flashing and configuring:

1. **Check Device Info:**
   ```bash
   meshtastic --port COM3 --info
   ```
   Look for "Environment" in telemetry section

2. **Monitor Telemetry:**
   ```bash
   meshtastic --port COM3 --listen
   ```
   Watch for temperature/humidity readings

3. **Via Meshtastic App:**
   - Connect to your node
   - Navigate to Device Metrics or Telemetry
   - You should see temperature and humidity values

## Configuration GUI Features Reference

The Python GUI (`meshtastic_config_gui.py`) provides the following features:

### Configuration Management
- **Save Config** - Save current settings to `device_config.json`
- **Load Config** - Load settings from any JSON configuration file
- **Reset to Defaults** - Restore default configuration values

### Pre-Install Configuration Export
- **Save as Pre-Install Config** - Export a structured JSON template for reuse
- **Export Setup Script** - Generate executable bash (.sh) and batch (.bat) scripts

### Device Operations
- **Detect Ports** - Automatically find available COM/USB ports
- **Test Connection** - Verify device is connected and responding
- **Apply to Device** - Send configuration to connected device via USB
- **Generate CLI Commands** - Preview meshtastic CLI commands
- **Export Commands** - Save CLI commands as a script file

### Configuration Sections in GUI
1. **Device Identity** - Name and short name
2. **LoRa Configuration** - Region, modem preset, TX power, hop limit
3. **Device Role** - CLIENT, ROUTER, SENSOR, etc.
4. **DHT22 Telemetry** - Enable/disable, update interval
5. **Connectivity** - Bluetooth and WiFi settings
6. **Device Connection** - COM port selection and testing

## Configuration Options Reference

### Regions (set lora.region)
| Region | Frequency | Use In |
|--------|-----------|--------|
| EU_868 | 868 MHz | UK, Europe |
| US | 915 MHz | USA, Canada |
| AU_915 | 915 MHz | Australia |
| CN | 470 MHz | China |

**WARNING: Using the wrong region is illegal and will prevent communication with other local nodes!**

### Modem Presets (set lora.modem_preset)
| Preset | Range | Speed | Use Case |
|--------|-------|-------|----------|
| LONG_SLOW | ~50+ km | Very Slow | Maximum range |
| LONG_FAST | ~30 km | Moderate | **Recommended** |
| LONG_MODERATE | ~20 km | Good | Balanced |
| SHORT_FAST | ~5 km | Fast | Urban only |

### Device Roles (set device.role)
| Role | Description |
|------|-------------|
| CLIENT | Standard operation, mobile use |
| CLIENT_MUTE | Receive only, no transmit |
| ROUTER | Forward messages, fixed installation |
| ROUTER_CLIENT | Router + client features |
| SENSOR | Low power, remote sensing |

### TX Power (set lora.tx_power)
- Maximum legal in EU: 27 dBm
- Recommended: 22 dBm (safe default)
- Lower values save battery

## Telemetry Settings

Enable and configure DHT22 readings:

```bash
# Enable environmental telemetry
meshtastic --port COM3 --set telemetry.environment_measurement_enabled true

# Set update interval (seconds)
meshtastic --port COM3 --set telemetry.environment_update_interval 300

# Screen display update interval
meshtastic --port COM3 --set telemetry.environment_screen_enabled true
meshtastic --port COM3 --set telemetry.environment_display_fahrenheit false
```

## Troubleshooting

### DHT22 Not Reading

1. **Check wiring:** Verify VCC, DATA, GND connections
2. **Check pin:** DATA must be on GPIO 4 (D3)
3. **Pull-up resistor:** Add 10K between VCC and DATA if not built-in
4. **Power:** Ensure 3.3V power is stable
5. **Wait:** DHT22 needs ~2 seconds between readings

### Device Not Detected

1. **Enter bootloader:** Hold BOOT, plug USB, release
2. **Check drivers:** Install CP210x or CH340 drivers if needed
3. **Try different cable:** Some USB cables are charge-only
4. **Check Device Manager:** Verify COM port appears

### Poor LoRa Range

1. Check antenna is connected securely
2. Increase TX power: `meshtastic --set lora.tx_power 22`
3. Use LONG_FAST modem preset
4. Elevate antenna position
5. Check for interference sources

### Factory Reset

```bash
meshtastic --port COM3 --factory-reset
```

## File Structure

```
dht22-firmware/
├── README.md                           # This file
├── meshtastic_config_gui.py            # Python GUI configuration tool
├── device_config.json                  # Saved device configuration (GUI)
├── meshtastic_preinstall_config.json   # Pre-install config template (exported)
├── setup_meshtastic_device.sh          # Automated setup script (Linux/Mac)
├── setup_meshtastic_device.bat         # Automated setup script (Windows)
├── source/
│   ├── DHT22Sensor.h                   # DHT22 sensor header
│   ├── DHT22Sensor.cpp                 # DHT22 sensor implementation
│   └── seeed_xiao_s3/                  # Variant configuration
│       ├── variant.h                   # Pin definitions (inc. DHT22_PIN)
│       ├── platformio.ini              # Build configuration
│       └── pins_arduino.h              # Arduino pin mapping
└── firmware/                           # Place compiled firmware here
    └── (firmware.bin)
```

**Configuration Files:**
- `device_config.json` - Working configuration saved by the GUI
- `meshtastic_preinstall_config.json` - Exportable configuration template for fresh devices
- `setup_meshtastic_device.sh/bat` - Executable scripts generated from your configuration

## Building Firmware with PlatformIO

### Prerequisites

#### 1. Install PlatformIO

**Option A: VS Code Extension (Recommended)**
1. Install [Visual Studio Code](https://code.visualstudio.com/)
2. Open VS Code Extensions (Ctrl+Shift+X)
3. Search for "PlatformIO IDE" and install it
4. Restart VS Code
5. Wait for PlatformIO to finish installing (check bottom status bar)

**Option B: Command Line Installation**
```bash
# Using pip
pip install platformio

# Or using pipx (isolated environment)
pipx install platformio
```

#### 2. Install Git
- Windows: Download from https://git-scm.com/download/win
- Linux: `sudo apt install git`
- macOS: `brew install git`

#### 3. Install Python 3.x
- Download from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### Step-by-Step Build Instructions

#### Step 1: Clone or Navigate to Firmware Repository

If you don't have the firmware source yet:
```bash
git clone https://github.com/meshtastic/firmware.git meshtastic-firmware
cd meshtastic-firmware
git checkout v2.6.11.60ec05e  # or latest version
```

If you already have it:
```bash
cd /path/to/meshtastic-firmware
git pull
```

#### Step 2: Verify DHT22 Support is Enabled

The DHT22 sensor files should already be in place. Verify:
```bash
# Check DHT22 sensor files exist
ls src/modules/Telemetry/Sensor/DHT22Sensor.*

# Check variant.h has DHT22_PIN defined
grep "DHT22_PIN" variants/seeed_xiao_s3/variant.h
```

You should see `#define DHT22_PIN 4` in the variant.h file.

#### Step 3: Build the Firmware

**Using VS Code with PlatformIO:**
1. Open the `meshtastic-firmware` folder in VS Code
2. Wait for PlatformIO to initialize (bottom status bar)
3. Click the PlatformIO icon in the left sidebar (alien head)
4. Expand "seeed-xiao-s3" under PROJECT TASKS
5. Click "Build"
6. Wait for compilation to complete

**Using Command Line (Windows CMD/PowerShell):**
```cmd
cd C:\Users\Home\Desktop\Meshtastic\meshtastic-firmware

# Build firmware
C:\Users\Home\.platformio\penv\Scripts\pio.exe run -e seeed-xiao-s3

# Or if pio is in PATH:
pio run -e seeed-xiao-s3
```

**Using Command Line (Linux/macOS/WSL):**
```bash
cd ~/Desktop/Meshtastic/meshtastic-firmware

# Build firmware
pio run -e seeed-xiao-s3

# Or with full path if not in PATH:
~/.platformio/penv/bin/pio run -e seeed-xiao-s3
```

#### Step 4: Locate Compiled Firmware

After successful build, find the firmware files in:
```
meshtastic-firmware/.pio/build/seeed-xiao-s3/
```

Key files:
- `firmware.bin` - Main firmware binary
- `firmware.elf` - Debug symbols (for advanced debugging)
- `partitions.bin` - Partition table

#### Step 5: Copy Firmware to dht22-firmware Folder

```bash
# Windows (PowerShell)
copy .pio\build\seeed-xiao-s3\firmware.bin ..\dht22-firmware\firmware\

# Linux/macOS
cp .pio/build/seeed-xiao-s3/firmware.bin ../dht22-firmware/firmware/
```

### Build Troubleshooting

#### "pio: command not found"

**Windows:**
```cmd
# Use full path
C:\Users\Home\.platformio\penv\Scripts\pio.exe run -e seeed-xiao-s3

# Or add to PATH:
set PATH=%PATH%;C:\Users\Home\.platformio\penv\Scripts
```

**Linux/macOS:**
```bash
# Use full path
~/.platformio/penv/bin/pio run -e seeed-xiao-s3

# Or add to PATH in ~/.bashrc or ~/.zshrc:
export PATH="$PATH:$HOME/.platformio/penv/bin"
```

#### Missing Dependencies / Library Errors

```bash
# Clean and rebuild
pio run -e seeed-xiao-s3 -t clean
pio run -e seeed-xiao-s3

# Or force library reinstall
pio pkg install -e seeed-xiao-s3
```

#### ESP-IDF or Toolchain Errors

PlatformIO should auto-download required toolchains. If issues persist:
```bash
# Update PlatformIO
pio upgrade

# Update platforms and packages
pio pkg update -e seeed-xiao-s3
```

#### Out of Memory During Compilation

Close other applications. If still failing:
```bash
# Build with reduced parallelism
pio run -e seeed-xiao-s3 -j 1
```

#### "DHT22Sensor.h: No such file or directory"

Ensure the DHT22 sensor files are in the correct location:
```
meshtastic-firmware/
└── src/
    └── modules/
        └── Telemetry/
            └── Sensor/
                ├── DHT22Sensor.h
                └── DHT22Sensor.cpp
```

If missing, copy from the `source/` folder:
```bash
cp dht22-firmware/source/DHT22Sensor.* meshtastic-firmware/src/modules/Telemetry/Sensor/
```

### Build Options

#### Clean Build
```bash
pio run -e seeed-xiao-s3 -t clean
pio run -e seeed-xiao-s3
```

#### Build and Upload in One Step
```bash
# Connect device in bootloader mode first (hold BOOT, plug USB)
pio run -e seeed-xiao-s3 -t upload
```

#### Build with Verbose Output
```bash
pio run -e seeed-xiao-s3 -v
```

#### Check Available Build Environments
```bash
pio project config --list-targets
```

### Creating Firmware Package for Web Flasher

The Meshtastic web flasher can accept individual `.bin` files or a `.zip` package.

**Simple Method - Single Binary:**
Just use the `firmware.bin` file from `.pio/build/seeed-xiao-s3/`

**Full Package Method:**
```bash
cd .pio/build/seeed-xiao-s3/

# Create zip with necessary files
zip firmware-seeed-xiao-s3-dht22.zip firmware.bin partitions.bin bootloader.bin
```

### Verifying the Build

After building, check the output for:
```
Building .pio/build/seeed-xiao-s3/firmware.bin
RAM:   [==        ]  XX.X% (used XXXXX bytes from XXXXXX bytes)
Flash: [========  ]  XX.X% (used XXXXXXX bytes from XXXXXXX bytes)
========================= [SUCCESS] =========================
```

The firmware size should be around 1.5-2MB for ESP32-S3.

### Quick Reference Commands

| Action | Command |
|--------|---------|
| Build firmware | `pio run -e seeed-xiao-s3` |
| Clean build | `pio run -e seeed-xiao-s3 -t clean` |
| Build + Upload | `pio run -e seeed-xiao-s3 -t upload` |
| Monitor serial | `pio device monitor -e seeed-xiao-s3` |
| List COM ports | `pio device list` |
| Update packages | `pio pkg update` |

## Resources

- [Meshtastic Documentation](https://meshtastic.org/docs/)
- [Web Flasher](https://flasher.meshtastic.org/)
- [XIAO ESP32-S3 + SX1262 Wiki](https://wiki.seeedstudio.com/xiao_esp32s3_&_wio_SX1262_kit_for_meshtastic/)
- [Meshtastic Python CLI](https://meshtastic.org/docs/software/python/)
- [Meshtastic Firmware GitHub](https://github.com/meshtastic/firmware)

## License

This firmware modification follows the Meshtastic project's open-source license (GPL-3.0).

