#include "configuration.h"

#if !MESHTASTIC_EXCLUDE_ENVIRONMENTAL_SENSOR && defined(DHT22_PIN)

#include "../mesh/generated/meshtastic/telemetry.pb.h"
#include "DHT22Sensor.h"
#include "TelemetrySensor.h"
#include <DHT.h>

DHT22Sensor::DHT22Sensor() : TelemetrySensor(meshtastic_TelemetrySensorType_SENSOR_UNSET, "DHT22") {}

DHT22Sensor::~DHT22Sensor()
{
    if (dht != nullptr) {
        delete dht;
        dht = nullptr;
    }
}

int32_t DHT22Sensor::runOnce()
{
    LOG_INFO("Init sensor: %s on GPIO %d", sensorName, DHT22_PIN);

    dht = new DHT(DHT22_PIN, DHT22);
    dht->begin();

    // Give the sensor time to stabilize
    delay(100);

    // Test read to verify sensor is connected
    float testTemp = dht->readTemperature();
    float testHum = dht->readHumidity();

    if (isnan(testTemp) || isnan(testHum)) {
        LOG_WARN("DHT22 sensor not responding on GPIO %d", DHT22_PIN);
        delete dht;
        dht = nullptr;
        sensorAvailable = false;
        return DEFAULT_SENSOR_MINIMUM_WAIT_TIME_BETWEEN_READS;
    }

    status = 1;
    initialized = true;
    sensorAvailable = true;
    LOG_INFO("DHT22 sensor initialized successfully: temp=%.1fC, humidity=%.1f%%", testTemp, testHum);

    return DEFAULT_SENSOR_MINIMUM_WAIT_TIME_BETWEEN_READS;
}

void DHT22Sensor::setup()
{
    // Setup is handled in runOnce for DHT22
}

bool DHT22Sensor::getMetrics(meshtastic_Telemetry *measurement)
{
    if (dht == nullptr || !sensorAvailable) {
        return false;
    }

    LOG_DEBUG("DHT22 getMetrics");

    // Read temperature and humidity
    float temperature = dht->readTemperature();
    float humidity = dht->readHumidity();

    // Check if readings are valid
    if (isnan(temperature) || isnan(humidity)) {
        LOG_WARN("DHT22 read failed - NaN values returned");
        return false;
    }

    // Sanity check the values
    if (temperature < -40 || temperature > 80 || humidity < 0 || humidity > 100) {
        LOG_WARN("DHT22 values out of range: temp=%.1f, humidity=%.1f", temperature, humidity);
        return false;
    }

    measurement->variant.environment_metrics.has_temperature = true;
    measurement->variant.environment_metrics.has_relative_humidity = true;
    measurement->variant.environment_metrics.temperature = temperature;
    measurement->variant.environment_metrics.relative_humidity = humidity;

    LOG_DEBUG("DHT22: temp=%.1fC, humidity=%.1f%%", temperature, humidity);

    return true;
}

#endif
