from RPi import GPIO
import time
import smbus

class LCD():
    def __init__(self) -> None:
        #Create an i2c bus
        self.i2c = smbus.SMBus(1)

        #Create constants
        self.I2C_ADDR = 0x3f #For me the i2c address is a bit different, maybe this should be changed if someone else is running the code.
        self.LCD_WIDTH = 16
        self.LCD_CHR = 1
        self.LCD_CMD = 0
        self.LCD_LINE_1 = 0x80 | 0x0
        self.LCD_LINE_2 = 0x80 | 0x40
        self.LCD_BACKLIGHT = 0b1000
        self.ENABLE = 0x4
        self.E_PULSE = 0.0002
        self.E_DELAY = 0.0002
        self.LCD_LINE_1_RIGHT = 0x0F

        self.LCD_BACKLIGHT_ON = True

        #Set display to 8bit mode
        self.send_byte_with_e_toggle(0b0011_0000)
        self.send_byte_with_e_toggle(0b0011_0000)

        #Set display to 4bit mode
        self.send_byte_with_e_toggle(0b0010_0000)

        #4bit mode, 2 lines, 5x7 character size
        self.send_instruction(0x28)
        #Display on, cursor off
        self.send_instruction(0x0C)
        #Cursor home
        self.send_instruction(0x06)
        
        self.send_instruction(0x1)        
    
    #This function sends data to the display, according to the mode
    def send_data_bits(self, byte, mode):
        #Split into MS and LS nibbles, and OR them with (1111 or-ed with mode)
        #              
        if self.LCD_BACKLIGHT_ON == True:                       
            self.MSN_nibble = (byte & 0b1111_0000)|(0x8|mode)
            self.LSN_nibble = ((byte & 0b0000_1111) << 4) |(0x8|mode)
        else:
            self.MSN_nibble = (byte & 0b1111_0000)|(0x0|mode)
            self.LSN_nibble = ((byte & 0b0000_1111) << 4) |(0x0|mode)

        #Send both nibbles individually
        self.send_byte_with_e_toggle(self.MSN_nibble)
        #I found that I need to add an extra delay (even though in the function there already is one)
        #Otherwise when I write normal text, mathematical symbols are displayed, and other weird things happen
        time.sleep(self.E_DELAY)
        self.send_byte_with_e_toggle(self.LSN_nibble)
        time.sleep(self.E_DELAY)

    def send_byte_with_e_toggle(self, bits):
        time.sleep(self.E_DELAY)
        #write data to i2c with e bit high
        self.i2c.write_byte(self.I2C_ADDR, (bits | self.ENABLE))
        #Wait for a little bit for the display to process the info
        time.sleep(self.E_PULSE)
        #write data to i2c with e bit low
        self.i2c.write_byte(self.I2C_ADDR, bits& (~ self.ENABLE))
        #Wait again
        time.sleep(self.E_DELAY)

    def send_instruction(self, byte):
        self.send_data_bits(byte, self.LCD_CMD)

    def send_character(self, byte):
        self.send_data_bits(byte, self.LCD_CHR)
    
    def display_text(self, some_string: str, line = None):
        #If no line is given, the text is automatically split in 2
        if line == None:
        #Split the string in first 16 characters and everything after that
            #Write first line
            for character in some_string[:16]:
                self.send_character(ord(character))
            #Shift to second line
            self.send_instruction(self.LCD_LINE_2)
            for character in some_string[16:]:
                self.send_character(ord(character))
        else:
            #Shift to desired line
            self.send_instruction(line)
            for character in some_string:
                character = ord(character)
                self.send_character(character)



    def clear_display(self):
        #Clear display & cursor home function
        self.send_instruction(1)
    
    def turn_off(self):
        self.LCD_BACKLIGHT_ON = False

        self.send_instruction(0b1000)
    
    def turn_back_on(self):
        self.LCD_BACKLIGHT_ON = True

        self.send_instruction(0b0000)

    if __name__ == '__main__':
        from lcd import LCD
        lcd = LCD()
        lcd.display_text("O O", lcd.LCD_LINE_1)
        lcd.display_text(" -", lcd.LCD_LINE_2)
        time.sleep(0.5)
        lcd.display_text("- O", lcd.LCD_LINE_1)
        time.sleep(0.1)
        lcd.display_text("- -", lcd.LCD_LINE_1)
        time.sleep(0.5)
        lcd.display_text("O O", lcd.LCD_LINE_1)
        lcd.display_text(" o", lcd.LCD_LINE_2)
        time.sleep(1)
        lcd.clear_display()
        lcd.turn_off()
        time.sleep(0.5)
        lcd.turn_back_on()
        time.sleep(0.5)
        lcd.turn_off()
        GPIO.cleanup()