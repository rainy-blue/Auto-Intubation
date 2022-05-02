import serial

if __name__ == '__main__':
    serUno = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    serUno.reset_input_buffer()
    
    serMega = serial.Serial('/dev/ttyACM1', 9600, timeout=1)
    serMega.reset_input_buffer()
    
    while True:
        if serUno.in_waiting > 0:
            line = serUno.readline().decode('utf-8').rstrip()
            print(line, "UnoACM0\n")
            
        if serMega.in_waiting > 0:
            line = serMega.readline().decode('utf-8').rstrip()
            print(line)