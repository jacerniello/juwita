#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

// --- WIFI SETTINGS ---
const char* ssid = 
const char* password = 

// --- SERVER SETTINGS ---
const char* serverName = 

const int potPin = 26; // GP26 / ADC0

void setup() {
  Serial.begin(115200);
  delay(2000); 

  // Force-reset the Wi-Fi radio to prevent the "infinite dots" stall
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(1000);

  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);
  
  // Try to connect
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nSUCCESS! Connected.");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // Read sensor
  int raw = analogRead(potPin);
  float voltage = (raw * 3.3) / 4095.0;

  // --- TRIGGER LOGIC (Over 0.5V) ---
  if (voltage > 0.5) {
    if (WiFi.status() == WL_CONNECTED) {
      WiFiClientSecure client;
      client.setInsecure(); // Bypass SSL certificate check for hackathon speed

      HTTPClient http;
      
      Serial.print(">>> THRESHOLD MET: ");
      Serial.print(voltage);
      Serial.println("V. Pinging Server...");

      if (http.begin(client, serverName)) { 
        int httpResponseCode = http.GET();
        
        if (httpResponseCode > 0) {
          Serial.print("SERVER RESPONDED: ");
          Serial.println(httpResponseCode);
        } else {
          Serial.print("HTTP ERROR: ");
          Serial.println(http.errorToString(httpResponseCode).c_str());
        }
        http.end();
      }
      
      Serial.println("Cooldown: 5 seconds...");
      delay(5000); 
    } else {
      Serial.println("WiFi Lost! Reconnecting...");
      WiFi.begin(ssid, password);
    }
  } 
  // --- IDLE LOGIC (Under 0.5V) ---
  else {
    Serial.print("Volts: "); 
    Serial.print(voltage);
    Serial.println(" | No Ping");
    
    // 10 second delay for idle monitoring as requested
    delay(5000); 
  }
}