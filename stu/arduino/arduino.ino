/*
 * CMD format: total length is 54 chars
 * | 4  | 2| 2| 2| 2| KEY        | Data 
 *  WRTE SN BA SZ TA FFFFFFFFFFFF 0123456789012345 * 2
 *  READ SN BA SZ TA FFFFFFFFFFFF
 *  CLSE
 */
 
#include <SPI.h>
#include <MFRC522.h>

constexpr uint8_t RST_PIN = 9;     // Configurable, see typical pin layout above
constexpr uint8_t SS_PIN = 10;     // Configurable, see typical pin layout above

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.

MFRC522::MIFARE_Key key;
MFRC522::PICC_Type piccType;

String cmd;

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

    // Serial.println(F("Scan a MIFARE Classic PICC"));
    // Serial.print(F("Using key (for A and B):"));
    dump_byte_array(key.keyByte, MFRC522::MF_KEY_SIZE);
    // Serial.println();
}

void loop() {
    // Look for new cards
    if ( ! mfrc522.PICC_IsNewCardPresent())
        return;

    // Select one of the cards
    if ( ! mfrc522.PICC_ReadCardSerial())
        return;
    
    // Show some details of the PICC (that is: the tag/card)
    Serial.print(F("Card UID:"));
    dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size);
    Serial.println();
    Serial.print(F("PICC type: "));
    MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
    Serial.println(mfrc522.PICC_GetTypeName(piccType));

    // Check for compatibility
    if ( piccType != MFRC522::PICC_TYPE_MIFARE_1K ) {
        Serial.println(F("This sample only works with MIFARE 1K Classic cards."));
        return;
    }

    byte sector         = 0;
    byte blockAddr      = 0;
    byte size           = 0;
    byte trailerBlock   = 0;
    byte dataBlock[]    = {
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00
    };
    byte buffer[18];
    MFRC522::StatusCode status;
    
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
        
        blockAddr    = cmd.substring(4, 8).toInt(); // sector  = blockAddr / 4;
        size         = cmd.substring(8, 10).toInt();
        trailerBlock = cmd.substring(10, 12).toInt();
        byte pos = 12;
        
        for (byte i = 0; i < 6; i++) {
            byte hi, lo;
            hi = cmd[pos] >= 'A' ? cmd[pos] - 'A' + 10 : cmd[pos] - '0';
            pos++;
            lo = cmd[pos] >= 'A' ? cmd[pos] - 'A' + 10 : cmd[pos] - '0';
            pos++;
            key.keyByte[i] = hi * 16 + lo;
        }

        if (cmd.substring(0, 4) == "WRTE") {
            Serial.print("WRTE:\t");
            for (int i = 0; i < size; ++i) {
                byte hi, lo;
                hi = cmd[pos] >= 'A' ? cmd[pos] - 'A' + 10 : cmd[pos] - '0';
                pos++;
                lo = cmd[pos] >= 'A' ? cmd[pos] - 'A' + 10 : cmd[pos] - '0';
                pos++;
                dataBlock[i] = hi * 16 + lo;
            }
        } else if (cmd.substring(0, 4) == "READ") {
            Serial.print("READ:\t");
        } else if (cmd.substring(0, 4) == "CLSE") {
            Serial.print("Close.\t");
            // end of cmd loop
            break;
        }

        Serial.print(sector, DEC);
        Serial.print("\t");
        Serial.print(blockAddr, DEC);
        Serial.print("\t");
        Serial.print(size, DEC);
        Serial.print("\t");
        Serial.print(trailerBlock, DEC);
        Serial.print("\t");
        dump_byte_array(key.keyByte, MFRC522::MF_KEY_SIZE);
        Serial.print("\ndata:\t");
        dump_byte_array(dataBlock, 16);
        Serial.println();
    }
    
    // Halt PICC
    mfrc522.PICC_HaltA();
    // Stop encryption on PCD
    mfrc522.PCD_StopCrypto1();
}


int writeToBlock(byte sector, byte blockAddr, byte dataBlock[])
{
    MFRC522::StatusCode status;
    status = (MFRC522::StatusCode) mfrc522.MIFARE_Write(blockAddr, dataBlock, 16);
    if (status != MFRC522::STATUS_OK) {
        Serial.print(F("MIFARE_Write() failed: "));
        Serial.println(mfrc522.GetStatusCodeName(status));
        Serial.print(F("Please check and try again."));
        return 0;
    }
    dump_byte_array(dataBlock, 16); Serial.println();
    Serial.println();
    return 1;
}

int readFromBlock(byte sector, byte blockAddr, byte duffer[], byte size)
{
    Serial.print(F("Reading data from block ")); Serial.print(blockAddr);
    Serial.println(F(" ..."));
    MFRC522::StatusCode status;
    byte buffer[18];
    status = (MFRC522::StatusCode) mfrc522.MIFARE_Read(blockAddr, buffer, &size);
    if (status != MFRC522::STATUS_OK) {
        Serial.print(F("MIFARE_Read() failed: "));
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
        Serial.print(buffer[i] < 0x10 ? " 0" : " ");
        Serial.print(buffer[i], HEX);
    }
}
