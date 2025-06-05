#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>

// OLED setup
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// DHT setup
#define DHTPIN1 2
#define DHTPIN2 3
#define DHTTYPE DHT22
DHT dht1(DHTPIN1, DHTTYPE);
DHT dht2(DHTPIN2, DHTTYPE);

// Giả lập cảm biến
#define CO2_PIN A0       // Biến trở: giả lập CO2 ppm
#define DUST_PIN A1      // Biến trở: giả lập PM2.5
#define PM10_PIN A2      // Biến trở: giả lập PM10

void setup() {
  Serial.begin(9600);
  dht1.begin();
  dht2.begin();

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("Không tìm thấy OLED");
    while (1);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
}

void loop() {
  // Đọc DHT
  float t1 = dht1.readTemperature();
  float h1 = dht1.readHumidity();
  float t2 = dht2.readTemperature();
  float h2 = dht2.readHumidity();

  // Đọc CO2
  int co2_raw = analogRead(CO2_PIN);
  float co2_ppm = map(co2_raw, 0, 1023, 400, 5000);

  // Đọc PM2.5 từ điện áp
  int dust_raw = analogRead(DUST_PIN);
  float voltage_dust = dust_raw * 5.0 / 1023.0;
  float pm25 = (voltage_dust - 0.7) / 0.005; // công thức giả lập
  if (pm25 < 0) pm25 = 0;

  // Đọc PM10 từ điện áp
  int pm10_raw = analogRead(PM10_PIN);
  float voltage_pm10 = pm10_raw * 5.0 / 1023.0;
  float pm10 = (voltage_pm10 - 0.7) / 0.005; // công thức giả lập tương tự
  if (pm10 < 0) pm10 = 0;

  // Serial debug
  Serial.print(t1);
  Serial.print(h1);

  Serial.print(t2);
  Serial.print(h2);

  Serial.print(co2_ppm);
  Serial.print(pm25);
  Serial.print(pm10);

  // Hiển thị OLED
  display.clearDisplay();
  display.setCursor(0, 0);
  display.print("T1:"); display.print(t1, 1); display.print(" H1:"); display.print(h1, 0); display.println("%");
  display.print("T2:"); display.print(t2, 1); display.print(" H2:"); display.print(h2, 0); display.println("%");
  display.print("CO2:"); display.print(co2_ppm, 0); display.println("ppm");
  display.print("PM2.5:"); display.print(pm25, 0); display.println("ug/m3");
  display.print("PM10 :"); display.print(pm10, 0); display.println("ug/m3");

  display.display();
  delay(2000);
}
import threading
threading.Thread(target=read_serial, daemon=True).start()