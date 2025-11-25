#include "configuration.h"

#if !MESHTASTIC_EXCLUDE_ENVIRONMENTAL_SENSOR && defined(DHT22_PIN)

#pragma once

#include "TelemetrySensor.h"
#include <DHT.h>

/**
 * DHT22 Temperature and Humidity Sensor
 *
 * This sensor uses a single-wire protocol (not I2C) and requires a GPIO pin.
 * Define DHT22_PIN in your variant.h or build flags to enable this sensor.
 *
 * Wiring for XIAO ESP32-S3:
 *   VCC  -> 3.3V
 *   GND  -> GND
 *   DATA -> GPIO pin (defined by DHT22_PIN)
 *
 * A 10K pull-up resistor between VCC and DATA is recommended but many
 * DHT22 breakout boards have this built-in.
 */
class DHT22Sensor : public TelemetrySensor
{
  private:
    DHT *dht = nullptr;
    bool sensorAvailable = false;

  protected:
    virtual void setup() override;

  public:
    DHT22Sensor();
    virtual ~DHT22Sensor();

    /**
     * Override hasSensor since DHT22 doesn't use I2C address detection
     */
    bool hasSensor() { return sensorAvailable; }

    virtual int32_t runOnce() override;

    /**
     * Read temperature and humidity from the DHT22
     */
    virtual bool getMetrics(meshtastic_Telemetry *measurement) override;
};

#endif
