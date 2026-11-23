// Gearotons RS485 controller hardware 0.5, ESP32-S3. All motor actions originate in a form POST.
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>
#include <Servomotor.h>
#include <esp_random.h>
#include <bootloader_random.h>
#include <math.h>

constexpr size_t MAX_MOTORS = 48;
constexpr uint16_t BUSY_OR_BOOT = 0x79;  // bootloader, calibration, homing, transition, busy
constexpr uint16_t OUTPUT_ENABLED = 1U << 1;
constexpr uint16_t CLOSED_LOOP = 1U << 2;
constexpr unsigned MOVE_MS = 1500;

WebServer server(80);
Servomotor& bus() {
  static Servomotor motor(255, Serial1, 5, 4, 230400);
  return motor;
}

detectDevicesResponse motors[MAX_MOTORS];
size_t motorCount = 0;
String ssid, password, token, address;
String notice = "Choose Detect motors to scan the bus.";
bool apReady = false;

String hexId(uint64_t id) {
  char hex[17];
  snprintf(hex, sizeof(hex), "%016llX", (unsigned long long)id);
  return String(hex);
}

String randomToken() {
  uint64_t bits[2];
  esp_fill_random(bits, sizeof(bits));
  return hexId(bits[0]) + hexId(bits[1]);
}

void remember(detectDevicesResponse reply, bool& overflow) {
  for (size_t i = 0; i < motorCount; ++i) {
    if (motors[i].uniqueId == reply.uniqueId) {
      motors[i].alias = reply.alias;
      return;
    }
  }
  if (motorCount == MAX_MOTORS) overflow = true;
  else motors[motorCount++] = reply;
}

void scan() {
  motorCount = 0;
  bool overflow = false, corrupt = false;
  for (int pass = 0; pass < 3; ++pass) {
    while (Serial1.available()) Serial1.read();
    const uint32_t start = millis();
    auto reply = bus().detectDevices();
    // Each broadcast has one 0..950 ms random-response window. Do not send
    // another command during its 1.1 s inhibit interval, even on collisions.
    while (bus().getError() == COMMUNICATION_SUCCESS) {
      remember(reply, overflow);
      if (millis() - start > 1500) break;
      reply = bus().detectDevicesGetAnotherResponse();
    }
    if (bus().getError() != COMMUNICATION_ERROR_TIMEOUT && bus().getError() != COMMUNICATION_SUCCESS) corrupt = true;
    while (millis() - start < 1150) delay(5);
  }
  while (Serial1.available()) Serial1.read();
  notice = "Scan complete. Found " + String(motorCount) + " unique device(s).";
  if (corrupt) notice += " A response was damaged. Repeat if any motor is missing.";
  if (overflow) notice += " Device list full. Connect fewer motors.";
}

String testTurn(uint64_t id) {
  // A fresh UID round trip prevents stale scan rows from selecting a new motor.
  auto info = bus().getProductInfo(id);
  if (bus().getError() || info.uniqueId != id) return "Cannot verify the selected motor.";
  char model[9] = {};
  memcpy(model, info.productCode, sizeof(info.productCode));
  String product(model);
  product.trim();
  if (product != "M17") return "This turn test supports Gearotons M17 motors.";
  auto status = bus().getStatus(id);
  if (bus().getError() || status.fatalErrorCode || (status.statusFlags & (BUSY_OR_BOOT | OUTPUT_ENABLED)))
    return "The motor must be healthy, idle and de-energized. Check the bench.";
  auto queued = bus().getNQueuedItems(id);
  if (bus().getError() || queued) return "Cannot confirm an empty movement queue.";
  auto specs = bus().getProductSpecs(id);
  if (bus().getError() || specs.updateFrequency < 1000 || specs.updateFrequency > 100000 ||
      specs.countsPerRotation < 1000 || specs.countsPerRotation > 100000000)
    return "Motor motion units could not be verified.";
  auto before = bus().getComprehensivePositionRaw(id);
  if (bus().getError() || fabs((double)before.commandedPosition - before.hallSensorPosition) > specs.countsPerRotation * 0.02)
    return "Position target and encoder must agree before enabling the motor.";

  bus().goToClosedLoop(id);
  bool ok = bus().getError() == COMMUNICATION_SUCCESS;
  if (ok) {
    ok = false;
    const uint32_t started = millis();
    do {
      delay(25);
      status = bus().getStatus(id);
      if (bus().getError() || status.fatalErrorCode || (status.statusFlags & 0x19)) break;
      if (!(status.statusFlags & BUSY_OR_BOOT) &&
          (status.statusFlags & (OUTPUT_ENABLED | CLOSED_LOOP)) == (OUTPUT_ENABLED | CLOSED_LOOP)) {
        ok = true;
        break;
      }
    } while (millis() - started < 600);
  }
  if (ok) {
    bus().trapezoidMoveRaw(id, specs.countsPerRotation / 4, specs.updateFrequency * MOVE_MS / 1000);
    ok = bus().getError() == COMMUNICATION_SUCCESS;
  }
  if (ok) {
    delay(MOVE_MS + 100);
    queued = bus().getNQueuedItems(id);
    ok = !bus().getError() && queued == 0;
  }
  if (ok) {
    auto after = bus().getComprehensivePositionRaw(id);
    const double turns = ((double)after.hallSensorPosition - before.hallSensorPosition) / specs.countsPerRotation;
    ok = !bus().getError() && fabs(turns - 0.25) < 0.05;
  }
  // Even a missing command acknowledgement can mean the motor acted.
  // Never retry a move; request release/queue clear on all energizing paths.
  bus().emergencyStop(id);
  if (bus().getError()) return "Motor release unconfirmed. Switch off bench motor power and check wiring.";
  status = bus().getStatus(id);
  if (bus().getError() || (status.statusFlags & OUTPUT_ENABLED))
    return "Cannot confirm driver outputs are off. Switch off bench motor power.";
  if (!ok || status.fatalErrorCode) return "Turn test did not verify. Driver outputs are off.";
  return "Quarter-turn verified by the Hall sensor. Driver outputs are off.";
}

void formStart(String& page, const char* action) {
  page += "<form method='post' action='";
  page += action;
  page += "'><input type='hidden' name='token' value='" + token + "'>";
}

void showPage() {
  if (server.hostHeader() != address && server.hostHeader() != address + ":80") {
    server.send(400, "text/plain", "Use the board IP address.");
    return;
  }
  String page;
  page.reserve(3000 + 640 * motorCount);
  page = F("<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
           "<title>RS485 controller motor tester</title><style>body{font:17px system-ui;max-width:44rem;margin:2rem auto;padding:0 1rem}"
           "button{font:inherit;padding:.5rem .8rem}section{padding:.65rem 0;border-top:1px solid #aaa}form{margin:.65rem 0}"
           "label{display:block;margin:.6rem 0}code{overflow-wrap:anywhere}</style><h1>RS485 controller motor tester</h1>");
  page += "<p role='status'>" + notice + "</p>";
  formStart(page, "/scan");
  page += F("<button>Detect motors</button></form><p>Use an unloaded, secured M17 on a dedicated bench bus. "
            "Keep motor power within reach. The turn test releases holding torque afterward.</p>");
  for (size_t i = 0; i < motorCount; ++i) {
    const String uid = hexId(motors[i].uniqueId);
    const String field = "<input type='hidden' name='id' value='" + uid + "'>";
    page += "<section><h2>Motor <code>" + uid + "</code></h2><p>Alias " + String(motors[i].alias) + "</p>";
    formStart(page, "/identify");
    page += field + "<button>Blink motor LED</button></form>";
    formStart(page, "/turn");
    page += field + "<label><input type='checkbox' required name='clear' value='yes'> Shaft is unloaded and clear</label>"
                    "<button>Turn 90&deg; and release</button></form></section>";
  }
  page += "</html>";
  server.sendHeader("Cache-Control", "no-store");
  server.sendHeader("X-Frame-Options", "DENY");
  server.sendHeader("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'");
  server.send(200, "text/html; charset=utf-8", page);
}

void handleAction() {
  if ((server.hostHeader() != address && server.hostHeader() != address + ":80") ||
      server.arg("token") != token || token.isEmpty()) {
    server.send(403, "text/plain", "Reload the tester page and try again.");
    return;
  }
  // Forms from old pages and replayed clicks cannot repeat a motion.
  token = randomToken();
  if (server.uri() == "/scan") scan();
  else {
    size_t i = 0;
    while (i < motorCount && hexId(motors[i].uniqueId) != server.arg("id")) ++i;
    if (i == motorCount) notice = "Unknown motor. Run detection again.";
    else if (server.uri() == "/identify") {
      bus().identify(motors[i].uniqueId);
      notice = bus().getError() ? "Motor did not acknowledge identification." : "The selected motor acknowledged its LED blink.";
    } else if (server.arg("clear") == "yes") notice = testTurn(motors[i].uniqueId);
    else notice = "Confirm the shaft is unloaded and clear before starting.";
  }
  server.sendHeader("Location", "/");
  server.send(303, "text/plain", "");
}

void printAccess() {
  if (apReady) Serial.printf("Wi-Fi: %s\nPassword: %s\nOpen http://%s/\n", ssid.c_str(), password.c_str(), address.c_str());
  else Serial.println("RS485 controller motor tester could not start its protected access point. Check the USB console and restart.");
}

void setup() {
  Serial.begin(115200);
  bus();
  ssid = "RS485-controller-" + hexId(ESP.getEfuseMac()).substring(4);
  Preferences settings;
  if (!settings.begin("rs2-bench", false)) return;
  password = settings.getString("wifi-key", "");
  if (password.isEmpty()) {
    // Seed the password from hardware entropy while the radio is still off.
    bootloader_random_enable();
    password = randomToken().substring(0, 16);
    bootloader_random_disable();
    if (!settings.putString("wifi-key", password)) { settings.end(); return; }
  }
  settings.end();
  if (password.length() != 16) return;
  WiFi.persistent(false);
  if (!WiFi.softAP(ssid.c_str(), password.c_str(), 1, 0, 1)) {
    WiFi.mode(WIFI_OFF);
    return;
  }
  address = WiFi.softAPIP().toString();
  token = randomToken();
  server.on("/", HTTP_GET, showPage);
  server.on("/scan", HTTP_POST, handleAction);
  server.on("/identify", HTTP_POST, handleAction);
  server.on("/turn", HTTP_POST, handleAction);
  server.begin();
  apReady = true;
  printAccess();
}

void loop() {
  static bool wasConnected = false;
  bool connected = (bool)Serial;
  if ((connected && !wasConnected) || Serial.available()) {
    while (Serial.available()) Serial.read();
    printAccess();
  }
  wasConnected = connected;
  if (apReady) server.handleClient();
  delay(2);
}
