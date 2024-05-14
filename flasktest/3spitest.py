import re
import serial
import subprocess
from datetime import datetime
import time, struct
#from machine import Pin, SPI   
import spidev
import RPi.GPIO as GPIO


class LoRa:
	def __init__(self, DIO0_Pin, local_ADD, plus20dBm=False):  #dio0 pin27gpio  13other  dest_ADD is destination address/localaddress
        ####################
        #                  #
        #     1.Reset      #
        #                  #
        ####################
	# Reset LoRa Module
		'''
		rst_pin = Pin(RST_Pin, Pin.OUT)
	rst_pin.off()
        time.sleep(0.01)
        rst_pin.on()
        time.sleep(0.01)
       		'''
	 ####################
        #                  #
        #      2.SPI       #
        #                  #
        ####################
		'''
        We command LoRa module to perform Tx/Rx operations via the SPI interface.
        We disable SPI communication first to ensure it only happends when we need.
        Define communication functions read and write.
        The SPI comm is enabled temporarily for reading and writing and disabled thereafter.
        	'''
        # Disable SPI communication with the LoRa module
        #self.cs_pin = Pin(CS_Pin, Pin.OUT)
        #self.cs_pin.on() # Release board from SPI Bus by bringing it into high impedance status.

        # SPI communication
        # See datasheet: Device support SPI mode 0 (polarity & phase = 0) up to a max of 10MHz.
        # Initialize the SPI connection
		self.spi = spidev.SpiDev()
		self.spi.open(0, 0)  # Open SPI bus 0, device 0
		self.spi.max_speed_hz = 500000  # Set SPI speed (you can adjust this)
		self.spi.mode = 0  # SPI mode (commonly mode 0)

	#self.spi = SPI(SPI_CH, baudrate=10_000_000, polarity=0, phase=0,
        #              sck=Pin(SCK_Pin), mosi=Pin(MOSI_Pin), miso=Pin(MISO_Pin)
        #            ) 
        ####################
        #                  #
        #      3.Lora      #
        #                  #
        ####################
		print(local_ADD)
		self.local_ADD=local_ADD
		print(self.local_ADD)
		self.RegTable = {  # register table
            'RegFifo'              : 0x00 ,
            'RegOpMode'            : 0x01 , # operation mode
            'RegFrfMsb'            : 0x06 ,
            'RegFrfMid'            : 0x07 ,
            'RegFrfLsb'            : 0x08 ,
            'RegPaConfig'          : 0x09 ,
            'RegFifoTxBaseAddr'    : 0x0e ,
            'RegFifoRxBaseAddr'    : 0x0f ,
            'RegFifoAddrPtr'       : 0x0d ,
            'RegFifoRxCurrentAddr' : 0x10 ,
            'RegIrqFlags'          : 0x12 ,  
            'RegRxNbBytes'         : 0x13 , # Number of received bytes 
            'RegPktSnrValue'       : 0x19 ,
            'RegPktRssiValue'      : 0x1a ,
            'RegRssiValue'         : 0x1b ,
            'RegModemConfig1'      : 0x1d , 
            'RegModemConfig2'      : 0x1e , 
            'RegPreambleMsb'       : 0x20 , 
            'RegPreambleLsb'       : 0x21 ,
            'RegPayloadLength'     : 0x22 ,
            'RegModemConfig3'      : 0x26 , 
            'RegDioMapping1'       : 0x40 , 
            'RegVersion'           : 0x42 , 
            'RegPaDac'             : 0x4d  
        }
        
		self.Mode = { # see Table 16 LoRa ® Operating Mode Functionality 
            'SLEEP'        : 0b000,
            'STANDBY'      : 0b001,
            'TX'           : 0b011,
            'RXCONTINUOUS' : 0b101, 
            'RXSINGLE'     : 0b110,  
            'CAD'          : 0b111, 
        }  

        # Choose LoRa mode and Test write/read functions
		LongRangeMode = 0b1
        # Choose LoRa (instead of FSK) mode for SX1276 and put the module in sleep mode
		self.write('RegOpMode', self.Mode['SLEEP'] | LongRangeMode << 7) 
        # Test read function 
		assert self.read('RegOpMode') == (self.Mode['SLEEP'] | LongRangeMode << 7), "LoRa initialization failed"
         
        # Set modem config: bandwidth, coding rate, header mode, spreading factor, CRC, and etc.  
        # See 4.4. LoRa Mode Register Map 
		Bw                   = {'125KHz':0b0111, '500kHz':0b1001}
		CodingRate           = {5:0b001, 6:0b010, 7:0b011, 8:0b100}
		ImplicitHeaderModeOn = {'Implicit':0b1, 'Explicit':0b0}
		self.write('RegModemConfig1', Bw['125KHz'] << 4 | CodingRate[8] << 1 | ImplicitHeaderModeOn['Explicit'])
		SpreadingFactor  = {7:0x7, 9:0x9, 12:0xC}
		TxContinuousMode = {'normal':0b0, 'continuous':0b1}
		RxPayloadCrcOn   = {'disable':0b0, 'enable':0b1}
		self.write('RegModemConfig2', SpreadingFactor[12] << 4 | TxContinuousMode['normal'] << 3 | RxPayloadCrcOn['enable'] << 2 | 0x00) 
		LowDataRateOptimize = {'Disabled':0b0, 'Enabled':0b1}
		AgcAutoOn = {'register LnaGain':0b0, 'internal AGC loop':0b1}
		self.write('RegModemConfig3', LowDataRateOptimize['Enabled'] << 3 | AgcAutoOn['internal AGC loop'] << 2)  
        
        # Preamble length
		self.write('RegPreambleMsb', 0x0) # Preamble can be (2^15)kb long, much longer than payload
		self.write('RegPreambleLsb', 0x8) # but we just use 8-byte preamble
        
        # See 4.1.4. Frequency Settings
		FXOSC = 32e6 # Freq of XOSC
		FSTEP = FXOSC / (2**19)
		Frf = int(915e6 / FSTEP)
		self.write('RegFrfMsb', (Frf >> 16) & 0xff)
		self.write('RegFrfMid', (Frf >>  8) & 0xff)
		self.write('RegFrfLsb',  Frf        & 0xff)
        
        # Output Power
		'''
        If desired output power is within -4 ~ +15dBm, use PA_LF or PA_HF as amplifier. 
        Use PA_BOOST as amplifier to output +2 ~ +17dBm continuous power or up to 20dBm 
          peak power in a duty cycled operation.
        Here we will always use PA_BOOST. 
        Since we use PA_BOOST, Pout = 2 + OutputPower and MaxPower could be any number (Why not 0b111/0x7?)
		'''
		PaSelect    = {'PA_BOOST':0b1, 'RFO':0b0} # Choose PA_BOOST (instead of RFO) as the power amplifier
		MaxPower    = {'15dBm':0x7, '13dBm':0x2}  # Pmax = 10.8 + 0.6 * 7  
		OutputPower = {'17dBm':0xf, '2dBm':0x0}  
		self.write('RegPaConfig', PaSelect['PA_BOOST'] << 7 | MaxPower['15dBm'] << 4 | OutputPower['2dBm'])
        
        # Enables the +20dBm option on PA_BOOST pin.  
		if plus20dBm: # PA (Power Amplifier) DAC (Digital Analog Converter)
			PaDac = {'default':0x04, 'enable_PA_BOOST':0x07} # Can be 0x04 or 0x07. 0x07 will enables the +20dBm option on PA_BOOST pin
			self.write('RegPaDac', PaDac['enable_PA_BOOST'])  
        
        # FIFO data buffer 
		'''
        SX1276 has a 256 byte memory area as the FIFO buffer for Tx/Rx operations.
        How do we know which area is for Tx and which is for Rx.
        We must set the base addresses RegFifoTxBaseAddr and RegFifoRxBaseAddr independently.
        Since SX1276 work in a half-duplex manner, we better set both base addresses
        at the bottom (0x00) of the FIFO buffer so that we can buffer 256 byte data
        during transmition or reception.
		''' 
		self.Fifo_Bottom = 0x00 # We choose this value to max buffer we can write (then send out)
		self.write('RegFifoTxBaseAddr', self.Fifo_Bottom)
		self.write('RegFifoRxBaseAddr', self.Fifo_Bottom)
        
        ####################
        #                  #
        #    4.Interrupt   #
        #                  #
        ####################
		'''
        # This section is optional for Tx.
        # It enable an interrupt when Tx is done.
		'''
		self.DioMapping = {
            'Dio0' : {
                         'RxDone'           : 0b00 << 6,
                         'TxDone'           : 0b01 << 6,
                         'CadDone'          : 0b10 << 6
                     },
            'Dio1' : {
                         'RxTimeout'        : 0b00 << 4,
                         'FhssChangeChannel': 0b01 << 4,
                         'CadDetected'      : 0b10 << 4
                     },
            'Dio2' : {},
            'Dio3' : {},
            'Dio4' : {},
            'Dio5' : {},
        } 
         
		self.IrqFlags = {
            'RxTimeout'        : 0b1 << 7,
            'RxDone'           : 0b1 << 6,
            'PayloadCrcError'  : 0b1 << 5,
            'ValidHeader'      : 0b1 << 4,
            'TxDone'           : 0b1 << 3,
            'CadDone'          : 0b1 << 2,
            'FhssChangeChannel': 0b1 << 1,
            'CadDetected'      : 0b1 << 0, 
        }
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(DIO0_Pin, GPIO.IN)
		GPIO.add_event_detect(DIO0_Pin, GPIO.RISING, callback=self._irq_handler)
		#dio0_pin = GPIO.input(DIO0_Pin)
		#dio0_pin.irq(handler=self._irq_handler, trigger=Pin.IRQ_RISING)
        
		''' # interrupt flag mask: use to deactive a particular interrupt
        RegIrqFlagsMask = 0x11;
        IrqFlagsMask = {
            'RxTimeoutMask'        : 0b1 << 7,
            'RxDoneMask'           : 0b1 << 6,
            'PayloadCrcErrorMask'  : 0b1 << 5,
            'ValidHeaderMask'      : 0b1 << 4,
            'TxDoneMask'           : 0b1 << 3,
            'CadDoneMask'          : 0b1 << 2,
            'FhssChangeChannelMask': 0b1 << 1,
            'CadDetectedMask'      : 0b1 << 0
        }
        write(RegIrqFlagsMask, IrqFlagsMask['TxDoneMask'])  #  This will deactivate interrupt on TxDone.
		''' 
		self.write('RegOpMode', self.Mode['STANDBY'])      # Request Standby mode so SX1276 performs reception initialization.

	def write(self, reg, data):
		self.spi.xfer2([self.RegTable[reg] | 0x80, data])
		'''
			wb = bytes([self.RegTable[reg] | 0x80]) # Create a writing byte
			if isinstance(data, int):
				data = wb + bytes([data]) 
			elif isinstance(data, str):
				data = wb + bytes(data, 'utf-8')
			else:
				raise
			#self.cs_pin.value(0) # Bring the CS pin low to enable communication 
			self.spi.write(data)
			#self.cs_pin.value(1) # release the bus. 
		'''
	def read(self, reg=None, length=1):
		data = self.spi.xfer2([self.RegTable[reg] & 0x7F, 0x00])
		if length == 1:
			return data[1]
		else:
			return data[1:]
		'''
			#self.cs_pin.value(0)
			# https://docs.micropython.org/en/latest/library/machine.SPI.html#machine-softspi
		if length == 1:
			data = self.spi.read(length+1, self.RegTable[reg])[1]
		else:
			data = self.spi.read(length+1, self.RegTable[reg])[1:]
		#self.cs_pin.value(1)
		'''
		#return data[1]
		#print(data[1])
		#return data[1]
		

    
	def _irq_handler(self, pin): 
		irq_flags = self.read('RegIrqFlags') 
		self.write('RegIrqFlags', 0xff) # write anything could clear all types of interrupt flags  
		if irq_flags & self.IrqFlags['RxDone']:
			if irq_flags & self.IrqFlags['PayloadCrcError']: 
				print('PayloadCrcError')
			else:
				self.write('RegFifoAddrPtr', self.read('RegFifoRxCurrentAddr')) 
				packet     = self.read('RegFifo', self.read('RegRxNbBytes')) 
				packet3 = self.spi.xfer2([self.RegTable['RegFifo'] & 0x7F] + [0x00] * self.read('RegRxNbBytes'))
				#print("packet is " , packet)
				print("packet3 is ", packet3)
				packet_string = ''.join(chr(byte) for byte in packet3[4:-1])
				print("packet string= ", repr(packet_string))
				destAddress = packet[0]
				print("dest add", destAddress)
				RecAddress = packet3[0]
				print("rec address", RecAddress)
				PacketSnr  = self.read('RegPktSnrValue')
				SNR        = struct.unpack_from('b', bytes([PacketSnr]))[0] / 4
				PacketRssi = self.read('RegPktRssiValue')  
				if SNR < 0:
					RSSI = -157 + PacketRssi + SNR
				else:
					RSSI = -157 + 16 / 15 * PacketRssi 
				RSSI = round(RSSI, 2) # Table 7 Frequency Synthesizer Specification 
				self.packet_handler(packet_string, destAddress, RecAddress, SNR, RSSI)
		elif irq_flags & self.IrqFlags['TxDone']: 
			self.after_TxDone(self)
		else: 
			for i, j in self.IrqFlags.items():
				if irq_flags & j:
					print(i) 
                    
	def PrintReg(self):
		for reg_name, reg_address in lora.RegTable.items():
                                    # Get the value from RegValues dictionary if it exists, or set it to None
                                        #print(reg_name)
			reg_value = lora.read(reg_name)
                                    # Print the register name, address, and value
			print(f"Register: {reg_name}, Address: {hex(reg_address)}, Value: {hex(reg_value) if reg_value is not None else 'Not Read'}")

	def RxCont(self):    
		self.write('RegDioMapping1', self.DioMapping['Dio0']['RxDone'])  
		self.write('RegOpMode', self.Mode['RXCONTINUOUS']) # Request Standby mode so SX1276 send out payload   
        
	def Tx(self): 
		self.write('RegDioMapping1', self.DioMapping['Dio0']['TxDone'])   
    
	def send(self, data): 
		self.write('RegFifoAddrPtr', self.Fifo_Bottom) 
		self.write('RegFifo', data)            # Write Data FIFO 
		self.write('RegPayloadLength', len(data)) 
		self.write('RegOpMode', self.Mode['TX'])          # Request Standby mode so SX1276 send out payload  
 
	def packet_handler(self, packet, destAddress, recAddress, SNR, RSSI):
		print("ANYTHING")
		#print(self.DIO0_Pin)
		print(self.local_ADD)
		if destAddress == self.local_ADD:
			if packet:
				print(packet)
				match = re.search(r'zz(\d+)', packet)
				print(match)
		# Check if a match is found
				if match:
					isolated_part = match.group(1)
					print("Isolated Part:", isolated_part)
					current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
					str_current_datetime = str(current_datetime)
					with open('/home/mike/flasktest/static/logled.txt', 'a') as file:
						file.write(str_current_datetime + " " + isolated_part +"\n")
					if (int(isolated_part) > 16000):
					# Specify the Python script you want to run
						script_to_run = "/home/mike/flasktest/static/ValveOn60min.py"
						# Run the script
						try:
							print("ground is dry")
							print("running ValveOn60min.py")
							subprocess.run(["python", script_to_run], check=True)
						except subprocess.CalledProcessError as e:
							print(f"Error: {e}")
					elif ((int(isolated_part) <= 16000) and (int(isolated_part) >= 12000)):
						script_to_run = "/home/mike/flasktest/static/ValveOn10min.py"
						# Run the script if the ground is a little dry
						try:
							print("ground is a little dry")
							print("running ValveOn10min.py")
							subprocess.run(["python", script_to_run], check=True)
						except subprocess.CalledProcessError as e:
							print(f"Error: {e}")
					else:
						print(f"ground is wet")
				else:
					print("Pattern not found in the string.zz")
				match = 0
				match = re.search(r'!!!!zy(\d+)', packet)
				print(match)
				# Check if a match is found
				if match:
					isolated_part = match.group(1)
					print("Isolated Part:", isolated_part)
					current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
					str_current_datetime = str(current_datetime)
					with open('/home/mike/flasktest/static/CompostTempLog.txt', 'a') as file:
						file.write(str_current_datetime + " " + isolated_part +"\n")
				else:
					print("Pattern not found in the string.zy")



	def after_TxDone(self):
		pass  

if __name__ == "__main__":
    # RFM95W         Pico GPIO old
    LoRa_MISO_Pin  = 16
#    LoRa_CS_Pin    = 17
    LoRa_SCK_Pin   = 18
    LoRa_MOSI_Pin  = 19
    LoRa_G0_Pin    = 27 # DIO0_Pin
    LoRa_EN_Pin    = 21
    LoRa_RST_Pin   = 22
    SPI_CH         =  0  
    local_ADD = 2
    #Pin(LoRa_EN_Pin, Pin.OUT).on()
    lora = LoRa(LoRa_G0_Pin, local_ADD)

    #lora.packet_handler = lambda self, packet, SNR, RSSI: print(packet, SNR, RSSI)
    #lora.read
    lora.write('RegRxNbBytes', 0xff)

    #print("")
    while True:
        lora.RxCont()
    print("end2")
