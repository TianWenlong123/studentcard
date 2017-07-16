#include <SPI.h>
#include <deprecated.h>
#include <MFRC522.h>
#include <MFRC522Extended.h>
#include <require_cpp11.h>

constexpr uint8_t RST_PIN = 9;     // Configurable, see typical pin layout above
constexpr uint8_t SS_PIN = 10;     // Configurable, see typical pin layout above
constexpr uint8_t ID_BLOCK = 4;
constexpr uint8_t ID_TRAILER_BLOCK = 7;

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.

MFRC522::MIFARE_Key key;
MFRC522::PICC_Type piccType;

String cmd;

uint8_t successRead;    // Variable integer to keep if we have Successful Read from Reader

void setup() {
    // put your setup code here, to run once:
    Serial.begin(9600); // Initialize serial communications with the PC
    while (!Serial);    // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
    SPI.begin();        // Init SPI bus
    mfrc522.PCD_Init(); // Init MFRC522 card

    // Prepare the key (used both as key A and as key B)
    // using FFFFFFFFFFFFh which is the default at chip delivery from the factory
    for (byte i = 0; i < 6; i++) {
        key.keyByte[i] = 0xFF;
    }
}

void loop() {
    do {
        successRead = getID();  // sets successRead to 1 when we get read from reader otherwise 0
    } while (!successRead);
    
    // Read command from Serial
    cmd = "";
    while (1) {
        if ( Serial.available() ) {
            cmd = Serial.readString();
        } else {
            continue;
        }
        if (cmd.length() < 4)
            continue;

        if (cmd.substring(0, 4) == "PASS") {
            Serial.print("OKAY\n");
            break;
        } else if (cmd.substring(0, 4) == "CLSE") {
            Serial.print("CLSE\n");
            break;
        } else {
            Serial.print("FAIL\n");
            break;
        }
    }
    
    // Stop encryption on PCD
     mfrc522.PCD_StopCrypto1();
     delay(1000);
}

uint8_t getID() {
    // Getting ready for Reading PICCs
    if ( ! mfrc522.PICC_IsNewCardPresent()) { //If a new PICC placed to RFID reader continue
        return 0;
    }
    if ( ! mfrc522.PICC_ReadCardSerial()) {   //Since a PICC placed get Serial and continue
        return 0;
    }
    // There are Mifare PICCs which have 4 byte or 7 byte UID care if you use 7 byte PICC
    // I think we should assume every PICC as they have 4 byte UID
    // Until we support 7 byte PICCs
    // Serial.println(F("Scanned PICC's UID:"));
    MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
    mfrc522.PICC_GetTypeName(piccType);

    // Check for compatibility
    if ( piccType != MFRC522::PICC_TYPE_MIFARE_1K ) {
        Serial.println(F("FAIL This sample only works with MIFARE 1K Classic cards."));
        return 0;
    }

    byte buffer[18];
    MFRC522::StatusCode status;

    if ( ! readFromBlock(ID_BLOCK, ID_TRAILER_BLOCK, buffer, sizeof(buffer))) {
        Log("Read failed.");
        return 0;
    }
    Serial.print("REQU");
    dump_byte_array(buffer, 16);
    Serial.println();
    
    mfrc522.PICC_HaltA(); // Stop reading
    return 1;
}

int writeToBlock(byte blockAddr, byte trailerBlock, byte dataBlock[], byte size)
{
    MFRC522::StatusCode status;
    // Authenticate using key A or B
    status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
        status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_B, trailerBlock, &key, &(mfrc522.uid));
        if (status != MFRC522::STATUS_OK) {
            Serial.print(F("FAIL: PCD_Authenticate() failed: "));
            Serial.println(mfrc522.GetStatusCodeName(status));
            return 0;
        }
    }
    
    status = (MFRC522::StatusCode) mfrc522.MIFARE_Write(blockAddr, dataBlock, size);
    if (status != MFRC522::STATUS_OK) {
        Serial.print(F("FAIL: MIFARE_Write() failed: "));
        Serial.println(mfrc522.GetStatusCodeName(status));
        return 0;
    }
    // dump_byte_array(dataBlock, 16); Serial.println();
    // Serial.println();
    return 1;
}

int readFromBlock(byte blockAddr, byte trailerBlock, byte buffer[], byte size)
{
    MFRC522::StatusCode status;
    // Authenticate using key A or B
    status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, trailerBlock, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
        status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_B, trailerBlock, &key, &(mfrc522.uid));
        if (status != MFRC522::STATUS_OK) {
            Serial.print(F("FAIL: PCD_Authenticate() failed: "));
            Serial.println(mfrc522.GetStatusCodeName(status));
            return 0;
        }
    }

    // Read block from sector-blockAddr
    status = (MFRC522::StatusCode) mfrc522.MIFARE_Read(blockAddr, buffer, &size);
    if (status != MFRC522::STATUS_OK) {
        Serial.print(F("FAIL: MIFARE_Read() failed: "));
        Serial.println(mfrc522.GetStatusCodeName(status));
        return 0;
    }
    return 1;
}


/**
 * Helper routine to dump a byte array as hex values to Serial.
 */
void dump_byte_array(byte *buffer, byte bufferSize) {
    for (byte i = 0; i < bufferSize; i++) {
        Serial.print(buffer[i] < 0x10 ? "0" : "");
        Serial.print(buffer[i], HEX);
    }
}

/* Log
 */
void Log(char *info) {
    Serial.print("LOG");
    Serial.println(info);
}


