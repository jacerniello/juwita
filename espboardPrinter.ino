#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>

// --- WIFI SETTINGS ---
const char* ssid = 
const char* password = 

// --- SERVER SETTINGS ---
// We use a "Base" URL so we can append the voltage data dynamically
const char* serverNameBase = 

const int potPin = 26; // GP26 / ADC0

void setup() {
  Serial.begin(115200);
  delay(3000); // Give the system a "Cosmic Moment" to stabilize power

  Serial.println("\n--- SYSTEM ONLINE ---");
  Serial.println("Initializing WiFi Radio...");
  
  WiFi.mode(WIFI_STA);
  WiFi.disconnect(); 
  delay(2000); 

  WiFi.begin(ssid, password);
  
  Serial.print("Connecting to: ");
  Serial.println(ssid);

  // Initial connection loop
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nSUCCESS! Handshake Complete.");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // --- ROBUST AUTO-RECOVERY ---
  // If the connection drops (e.g., you walk away with your phone), 
  // this block takes over until the "Handshake" is restored.
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("\n[Network Lost] Deep cycling radio for reconnection...");
    
    while (WiFi.status() != WL_CONNECTED) {
      WiFi.disconnect();
      delay(3000); // 3-second "Breather" to clear ghost sessions on the phone
      WiFi.begin(ssid, password);
      
      int timeout = 0;
      // Wait up to 10 seconds per attempt
      while (WiFi.status() != WL_CONNECTED && timeout < 20) {
        delay(500);
        Serial.print(".");
        timeout++;
      }

      if (WiFi.status() != WL_CONNECTED) {
        Serial.println("\n[Retry Failed] Retrying in 5 seconds...");
        delay(5000); 
      }
    }
    Serial.println("\n[Healed] Connection restored.");
  }

  // --- SENSOR DATA ACQUISITION ---
  int raw = analogRead(potPin);
  float voltage = (raw * 3.3) / 4095.0;

  // --- TRIGGER LOGIC (Over 0.5V) ---
  if (voltage > 0.5) {
    WiFiClientSecure client;
    client.setInsecure(); // Bypass SSL for hackathon speed/simplicity
    HTTPClient http;
    
    // THE UPGRADE: Appending the voltage value to the URL string
    // This turns the ping into: ...ping?key=XXX&v=0.72
    String fullURL = String(serverNameBase) + "&v=" + String(voltage, 2);
    
    Serial.print(">>> THRESHOLD MET: ");
    Serial.print(voltage);
    Serial.println("V. Pinging Server...");

    if (http.begin(client, fullURL)) { 
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
  } 
  // --- IDLE LOGIC (Under 0.5V) ---
  else {
    Serial.print("Status: Idle | Volts: "); 
    Serial.print(voltage);
    Serial.println(" | No Ping sent.");
    
    // 10 second delay for idle monitoring
    delay(5000); 
  }
}
