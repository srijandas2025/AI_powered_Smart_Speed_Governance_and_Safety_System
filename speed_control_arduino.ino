#define ENA 9
#define IN1 8
#define IN2 7
#define IR_PIN 2
#define PULSES_PER_REV 7

volatile int pulseCount = 0;
unsigned long lastTime = 0;
unsigned long lastCmdTime = 0;

int rpm = 0;
int motorPWM = 180;   // 🔥 startup high speed

void countPulse() {
  pulseCount++;
}

void setup() {
  Serial.begin(9600);

  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IR_PIN, INPUT);

  attachInterrupt(digitalPinToInterrupt(IR_PIN), countPulse, RISING);

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
}

void loop() {

  // ===== READ PYTHON COMMAND =====
  if (Serial.available()) {
    int cmd = Serial.parseInt();

    if (cmd == 60) motorPWM = 150;   // ≈200 RPM
    else if (cmd == 40) motorPWM = 120; // ≈170 RPM

    lastCmdTime = millis();
  }

  // ===== 30 sec no sign → normal speed =====
  if (millis() - lastCmdTime > 30000) {
    motorPWM = 180; // ≈230–240 RPM
  }

  analogWrite(ENA, motorPWM);

  // ===== RPM CALC + SEND =====
  if (millis() - lastTime >= 1000) {
    rpm = (pulseCount * 60) / PULSES_PER_REV;
    pulseCount = 0;
    lastTime = millis();

    Serial.print("RPM:");
    Serial.println(rpm);
  }
}