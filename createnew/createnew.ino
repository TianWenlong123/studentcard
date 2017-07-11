
#include <SPI.h>
#include <MFRC522.h>

constexpr uint8_t RST_PIN = 9;     // Configurable, see typical pin layout above
constexpr uint8_t SS_PIN = 10;     // Configurable, see typical pin layout above

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.

MFRC522::MIFARE_Key key;
MFRC522::MIFARE_Key validKeyA;

MFRC522::PICC_Type piccType;

enum CreateNewState {
    NEW_START,
    NEW_NO_CARD,     // detect card
    NEW_VERIFY_CARD, // verify card, wait for info from serial
    NEW_WAIT_INFO,   // wait info from serial
    NEW_WRITE_CARD,  // write info into card
    NEW_DONE         // 
} newState = NEW_START;

constexpr byte VALID_SECTOR  = 10;
constexpr byte VALID_BLOCK   = 40;
constexpr byte VALID_TRAILER = 43;

constexpr byte ID_SECTOR     = 1;
constexpr byte ID_BLOCK      = 4;
constexpr byte ID_TRAILER    = 7;

String comData;
long newID = 0x00112233;

/*
 * 校园卡制作
 */
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
    for (byte i = 0; i < 6; i++) {
        validKeyA.keyByte[i] = 0xFF;
    }

    Serial.println(F("Scan a MIFARE Classic PICC"));
    Serial.print(F("Using key (for A and B):"));
    dump_byte_array(key.keyByte, MFRC522::MF_KEY_SIZE);
    Serial.println();
    
    newState = NEW_START;
}

void loop() {
    // put your main code here, to run repeatedly:
    
    switch (newState)
    {
    case NEW_START:
        newState = NEW_NO_CARD;
        return;
    case NEW_NO_CARD:
        // Look for new cards
        if ( ! mfrc522.PICC_IsNewCardPresent())
            return;
        newState = NEW_VERIFY_CARD;
        Serial.println("State: card verify");
        break;
    case NEW_VERIFY_CARD:
        // Select one of the cards
        if ( ! mfrc522.PICC_ReadCardSerial())
        {
            Serial.println("Read card serial failed.");
            newState = NEW_NO_CARD;
            return;
        }

        // Show some details of the PICC (that is: the tag/card)
        Serial.print(F("Card UID:"));
        dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size);
        Serial.println();
        Serial.print(F("PICC type: "));
        piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
        Serial.println(mfrc522.PICC_GetTypeName(piccType));

        // Check for compatibility
        if ( piccType != MFRC522::PICC_TYPE_MIFARE_1K ) {
            Serial.println(F("This sample only works with MIFARE 1K cards."));
            newState = NEW_DONE;
            return;
        }

        if ( ! validEmptyCard())
        {
            Serial.println(F("This card is not a valid empty card."));
            newState = NEW_DONE;
            return;
        }

        newState = NEW_WAIT_INFO;
        Serial.println("State: wait info");
        break;
    case NEW_WAIT_INFO:
        // Get info from serial
        if ( ! getNewCardInfo())
        {
            newState = NEW_WAIT_INFO;
        }
        else {
            newState = NEW_WRITE_CARD;
            Serial.println("Status: write card");
        }
        break;
    case NEW_WRITE_CARD:
        // Write data to the block
        Serial.print(F("Writing data into block "));

        if ( ! writeNewCard())
        {
            newState = NEW_NO_CARD;
            Serial.println("Write failed.");
            return;
        }

        Serial.println(F("Congratulations! New card complete."));
        newState = NEW_DONE;
        break;
    case NEW_DONE:
        newState = NEW_NO_CARD;
        break;
    default:
        newState = NEW_NO_CARD;
        break;
    }
}


int validEmptyCard() {
    // In this sample we use the second sector,
    // that is: sector #1, covering block #4 up to and including block #7
    
    MFRC522::StatusCode status;
    byte buffer[18];
    byte size = sizeof(buffer);

    // Authenticate using key valid_A
    Serial.println(F("Authenticating using key valid_A..."));
    status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(
        MFRC522::PICC_CMD_MF_AUTH_KEY_A, VALID_TRAILER, 
        &validKeyA, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
        Serial.print(F("PCD_Authenticate() failed: "));
        Serial.println(mfrc522.GetStatusCodeName(status));
        return 0;
    }

    // Read data from the block
    Serial.print(F("Reading data from valid block ")); Serial.print(VALID_BLOCK);
    Serial.println(F(" ..."));
    status = (MFRC522::StatusCode) mfrc522.MIFARE_Read(VALID_BLOCK, buffer, &size);
    if (status != MFRC522::STATUS_OK) {
        Serial.print(F("MIFARE_Read() failed: "));
        Serial.println(mfrc522.GetStatusCodeName(status));
        return 0;
    }
    Serial.print(F("Data in valid block ")); Serial.print(VALID_BLOCK); Serial.println(F(":"));
    dump_byte_array(buffer, 16); Serial.println();
    Serial.println();
    
    if (buffer[0] == 0x00)
        return 1;
    else
        return 0;
}

int getNewCardInfo()
{
    if ( Serial.available() > 0 ) {
        // 2014011111
        newID = Serial.parseInt(); // return value if long(32 bit)
        if (newID == 0)
            return 0;
        Serial.print(F("ID is: ")); Serial.println(newID);
        //comData += char(Serial.read());
    } else  {
        return 0;
    }
    return 1;
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

int writeNewCard()
{
    byte buffer[18];
    byte size = sizeof(buffer);
    byte dataBlock[]    = {
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x00
    };
    
    // write student id
    long * pID = &newID;
    byte * bpID = (byte *)pID;
    for (int i = 0; i < 4; i++) {
        dataBlock[i] = bpID[i];
    }

    // Authenticate using key
    MFRC522::StatusCode status;
    Serial.println(F("Authenticating again using key A..."));
    status = (MFRC522::StatusCode) mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, ID_TRAILER, &key, &(mfrc522.uid));
    if (status != MFRC522::STATUS_OK) {
        Serial.print(F("PCD_Authenticate() failed: "));
        Serial.println(mfrc522.GetStatusCodeName(status));
        return 0;
    }
    
    if ( ! writeToBlock(ID_SECTOR, ID_BLOCK, dataBlock)) {
        Serial.print(F("Please check and try again."));
        newState = NEW_DONE;
        return 0;
    }
    Serial.println();
    // check write result
    if ( ! readFromBlock(ID_SECTOR, ID_BLOCK, buffer, size))
    {
        Serial.println("Read from id sector failed.");
        return 0;
    }
    dump_byte_array(buffer, 16); Serial.println();
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
