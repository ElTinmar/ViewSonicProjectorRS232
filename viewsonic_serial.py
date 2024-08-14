import serial

WRITE_HEADER = b'\x06\x14\x00\x04\x00\x34'
READ_HEADER = b'\x07\x14\x00\x05\x00\x34\x00\x00'
READ_RESPONSE_ONE_BYTE_HEADER = b'\x05\x14\x00\x03\x00\x00\x00'
READ_RESPONSE_TWO_BYTE_HEADER = b'\x05\x14\x00\x04\x00\x00\x00'

RESPONSE_MAPPING_ONE_BYTE = {
    i: READ_RESPONSE_ONE_BYTE_HEADER + bytes([i, (0x17 + i) % 256]) for i in range(256)
}

RESPONSE_MAPPING_TWO_BYTE = {
    i: (READ_RESPONSE_TWO_BYTE_HEADER + bytes([i, 0x00, (0x18 + i) % 256])
    if i >= 0
    else READ_RESPONSE_TWO_BYTE_HEADER + bytes([i + 256, 0xFF, (0x17 + i) % 256]))
    for i in range(-255, 256)
}

class WRITE_COMMAND:
    POWER_ON = WRITE_HEADER + b'\x11\x00\x00\x5d'
    POWER_OFF = WRITE_HEADER + b'\x11\x01\x00\x5e'

    RESET_ALL_SETTINGS = WRITE_HEADER + b'\x11\x02\x00\x5f'

    RESET_COLOR_SETTINGS = WRITE_HEADER + b'\x11\x2a\x00\x87'

    SPLASH_SCREEN_BLACK = WRITE_HEADER + b'\x11\x0a\x00\x67'
    SPLASH_SCREEN_BLUE = WRITE_HEADER + b'\x11\x0a\x01\x68'
    SPLASH_SCREEN_VIEWSONIC = WRITE_HEADER + b'\x11\x0a\x02\x69'
    SPLASH_SCREEN_SCREENCAPTURE = WRITE_HEADER + b'\x11\x0a\x03\x6a'
    SPLASH_SCREEN_OFF = WRITE_HEADER + b'\x11\x0a\x04\x6b'

    QUICK_POWEROFF_OFF = WRITE_HEADER + b'\x11\x0b\x00\x68'
    QUICK_POWEROFF_ON = WRITE_HEADER + b'\x11\x0b\x01\x69'

    HIGH_ALTITUDE_MODE_OFF = WRITE_HEADER + b'\x11\x0c\x00\x69'
    HIGH_ALTITUDE_MODE_ON = WRITE_HEADER + b'\x11\x0c\x01\x6a'

    LIGHT_SOURCE_MODE_NORMAL = WRITE_HEADER + b'\x11\x10\x00\x6d'
    LIGHT_SOURCE_MODE_ECO = WRITE_HEADER + b'\x11\x10\x01\x6e'
    LIGHT_SOURCE_MODE_DYNAMIC_ECO = WRITE_HEADER + b'\x11\x10\x02\x6f'
    LIGHT_SOURCE_MODE_SUPER_ECO = WRITE_HEADER + b'\x11\x10\x03\x70'

    MESSAGE_OFF = WRITE_HEADER + b'\x11\x27\x00\x84'
    MESSAGE_ON = WRITE_HEADER + b'\x11\x27\x01\x85'

    PROJECTOR_POSITION_FRONT_TABLE = WRITE_HEADER + b'\x12\x00\x00\x5e'
    PROJECTOR_POSITION_REAR_TABLE = WRITE_HEADER + b'\x12\x00\x01\x5f'
    PROJECTOR_POSITION_FRONT_CEILING = WRITE_HEADER + b'\x12\x00\x02\x60'
    PROJECTOR_POSITION_REAR_CEILING = WRITE_HEADER + b'\x12\x00\x03\x61'

    PROJECTOR_3D_SYNC_OFF = WRITE_HEADER + b'\x12\x20\x00\x7e'
    PROJECTOR_3D_SYNC_AUTO = WRITE_HEADER + b'\x12\x20\x01\x7f'
    PROJECTOR_3D_SYNC_FRAME_SEQUENTIAL = WRITE_HEADER + b'\x12\x20\x02\x80'
    PROJECTOR_3D_SYNC_FRAME_PACKING = WRITE_HEADER + b'\x12\x20\x03\x81'
    PROJECTOR_3D_SYNC_TOP_BOTTOM = WRITE_HEADER + b'\x12\x20\x04\x82'
    PROJECTOR_3D_SYNC_SIDE_BY_SIDE = WRITE_HEADER + b'\x12\x20\x05\x83'

class WRITE_RESPONSE:
    ACK = b'\x03\x14\x00\x00\x00\x14'
    DISABLED = b'\x00\x14\x00\x00\x00\x14'

class READ_COMMAND:
    POWER_STATUS = READ_HEADER + b'\x11\x00\x5e'
    PROJECTOR_STATUS = READ_HEADER + b'\x11\x26\x84'
    SPLASH_SCREEN_STATUS = READ_HEADER + b'\x11\x0a\x68'
    QUICK_POWEROFF_STATUS = READ_HEADER + b'\x11\x0b\x69'
    HIGH_ALTITUDE_MODE_STATUS = READ_HEADER + b'\x11\x0c\x6a'
    LIGHT_SOURCE_MODE_STATUS = READ_HEADER + b'\x11\x10\x6e'
    MESSAGE_STATUS = READ_HEADER + b'\x11\x27\x85'
    PROJECTOR_POSITION_STATUS = READ_HEADER + b'\x12\x00\x5f'
    PROJECTOR_3D_SYNC_STATUS = READ_HEADER + b'\x12\x20\x7f'

class READ_RESPONSE:
    POWER_STATUS_ON = RESPONSE_MAPPING_ONE_BYTE[1]
    POWER_STATUS_OFF = RESPONSE_MAPPING_ONE_BYTE[0]

    PROJECTOR_STATUS_WARM_UP = RESPONSE_MAPPING_ONE_BYTE[1]
    PROJECTOR_STATUS_COOL_DOWN = RESPONSE_MAPPING_ONE_BYTE[3]
    PROJECTOR_STATUS_POWER_ON = RESPONSE_MAPPING_ONE_BYTE[2]
    PROJECTOR_STATUS_POWER_DOWN = RESPONSE_MAPPING_ONE_BYTE[0]

    SPLASH_SCREEN_STATUS_BLACK = RESPONSE_MAPPING_ONE_BYTE[0]
    SPLASH_SCREEN_STATUS_BLUE = RESPONSE_MAPPING_ONE_BYTE[1]
    SPLASH_SCREEN_STATUS_VIEWSONIC = RESPONSE_MAPPING_ONE_BYTE[2]
    SPLASH_SCREEN_STATUS_SCREENCAPTURE = RESPONSE_MAPPING_ONE_BYTE[3]
    SPLASH_SCREEN_STATUS_OFF = RESPONSE_MAPPING_ONE_BYTE[4]

    QUICK_POWEROFF_STATUS_OFF = RESPONSE_MAPPING_ONE_BYTE[0]
    QUICK_POWEROFF_STATUS_ON = RESPONSE_MAPPING_ONE_BYTE[1]

    HIGH_ALTITUDE_MODE_STATUS_OFF = RESPONSE_MAPPING_ONE_BYTE[0]
    HIGH_ALTITUDE_MODE_STATUS_ON = RESPONSE_MAPPING_ONE_BYTE[1]

    LIGHT_SOURCE_MODE_STATUS_NORMAL = RESPONSE_MAPPING_ONE_BYTE[0]
    LIGHT_SOURCE_MODE_STATUS_ECO = RESPONSE_MAPPING_ONE_BYTE[1]
    LIGHT_SOURCE_MODE_STATUS_DYNAMIC_ECO = RESPONSE_MAPPING_ONE_BYTE[2]
    LIGHT_SOURCE_MODE_STATUS_SUPER_ECO = RESPONSE_MAPPING_ONE_BYTE[3]

    MESSAGE_STATUS_OFF = RESPONSE_MAPPING_ONE_BYTE[0]
    MESSAGE_STATUS_ON = RESPONSE_MAPPING_ONE_BYTE[1]

    PROJECTOR_POSITION_STATUS_FRONT_TABLE = RESPONSE_MAPPING_ONE_BYTE[0]
    PROJECTOR_POSITION_STATUS_REAR_TABLE = RESPONSE_MAPPING_ONE_BYTE[1]
    PROJECTOR_POSITION_STATUS_FRONT_CEILING = RESPONSE_MAPPING_ONE_BYTE[2]
    PROJECTOR_POSITION_STATUS_REAR_CEILING = RESPONSE_MAPPING_ONE_BYTE[3]

    PROJECTOR_3D_SYNC_STATUS_OFF = RESPONSE_MAPPING_ONE_BYTE[0]
    PROJECTOR_3D_SYNC_STATUS_AUTO = RESPONSE_MAPPING_ONE_BYTE[1]
    PROJECTOR_3D_SYNC_STATUS_FRAME_SEQUENTIAL = RESPONSE_MAPPING_ONE_BYTE[2]
    PROJECTOR_3D_SYNC_STATUS_FRAME_PACKING = RESPONSE_MAPPING_ONE_BYTE[3]
    PROJECTOR_3D_SYNC_STATUS_TOP_BOTTOM = RESPONSE_MAPPING_ONE_BYTE[4]
    PROJECTOR_3D_SYNC_STATUS_SIDE_BY_SIDE = RESPONSE_MAPPING_ONE_BYTE[5]

class ViewSonicProjector:
    '''
    Requires a crossovcer (null modem) cable for use with PC
    '''

    VALID_BAUD_RATES = [2400,4800,9600,14400,19200,38400,115200]


    def __init__(
        self,
        port: str = '/dev/ttyS0',
        baudrate: int = 115200,
        data_byte_length = serial.EIGHTBITS,
        parity_check = serial.PARITY_NONE,
        num_stop_bit: int = serial.STOPBITS_ONE,
        timeout: float = 1.0,
        flow_control: bool = False
        ):

        if baudrate not in self.VALID_BAUD_RATES:
            raise ValueError(f'Supported baud rates are: {self.VALID_BAUD_RATES}')
        
        self.port = port
        self.baudrate = baudrate
        self.data_byte_length = data_byte_length
        self.parity_check = parity_check
        self.num_stop_bit = num_stop_bit
        self.timeout = timeout
        self.flow_control = flow_control

        self.ser = serial.Serial(
            port = port,
            baudrate = baudrate,
            bytesize = data_byte_length,
            parity = parity_check,
            stopbits = num_stop_bit,
            timeout = timeout,
            rtscts = flow_control
        )

    def __del__(self):
        self.ser.close()

    def write_packet(
        self,
        cmd2,
        cmd3,
        data,
        ):
        '''
        LSB = length(low byte)
        MSB = length(high byte)
        '''
        data = WRITE_CMD + 
        self.ser.write(data)

    def read_packet(
        self,
        lsb,
        msb,
        cmd2,
        cmd3,
        data,
        checksum
        ):
        pass

    def write_response_packet(self):
        pass

    def read_response_packet(self):
        pass

if __name__ == '__main__':

    proj = ViewSonicProjector()