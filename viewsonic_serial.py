import serial
import time
from typing import Optional, Dict
import os
import json

class TransmissionError(Exception):
    pass

class FunctionDisabled(Exception):
    pass

class ProjectorOFF(Exception):
    pass

class CommandFailed(Exception):
    pass

class HEADER:
    '''
    5-bytes headers for read/write queries and device responses.
    I added part of the command payload to the headers when it never changes.
    '''
    NUM_BYTES = 5
    WRITE = b'\x06\x14\x00\x04\x00' + b'\x34'
    READ = b'\x07\x14\x00\x05\x00' + b'\x34\x00\x00'
    READ_RESPONSE_ONE_BYTE = b'\x05\x14\x00\x03\x00' + b'\x00\x00'
    READ_RESPONSE_TWO_BYTE = b'\x05\x14\x00\x04\x00' + b'\x00\x00'
    ACK = b'\x03\x14\x00\x00\x00' + b'\x14'
    DISABLED = b'\x00\x14\x00\x00\x00' + b'\x14'
    PROJ_OFF = b'\x00\x00\x00\x00\x00' + b'\x00'

class CMD:
    REMOTE_KEY = b'\x02\x04'

    GAMMA = b'\x05\xca'
    
    # X = b'\x0c\x00'
    # X = b'\x0c\x01'
    # X = b'\x0c\x03'
    # X = b'\x0c\x04'
    RESET_TO_FACTORY_DEFAULT = b'\x0c\x08'
    # X = b'\x0c\x09'
    # X = b'\x0c\x0a'
    # X = b'\x0c\x0c'
    ERROR_STATUS =  b'\x0c\x0d'
    # X = b'\x0c\x0f'
    # X = b'\x0c\x11'
    # X = b'\x0c\x21'
    # X = b'\x0c\x23'
    # X = b'\x0c\x2f'
    # X = b'\x0c\x31'
    # X = b'\x0c\x34'
    # X = b'\x0c\x35'
    REMOTE_CONTROL_CODE = b'\x0c\x48'
    # X = b'\x0c\x4c'
    # X = b'\x0c\x4f'
    # X = b'\x0c\x50'
    # X = b'\x0c\x51'
    # X = b'\x0c\x53'
    # X = b'\x0c\x54'
    # X = b'\x0c\x60'
    # X = b'\x0c\x8e'
    # X = b'\x0c\x9d'
    # X = b'\x0c\xa7'
    # X = b'\x0c\xaa'
    # X = b'\x0c\xaf'
    # X = b'\x0c\xd7'
    # X = b'\x0c\xd9'

    POWER_ON = b'\x11\x00'
    POWER_OFF = b'\x11\x01'
    RESET_ALL_SETTINGS = b'\x11\x02'
    SPLASH_SCREEN = b'\x11\x0a'
    QUICK_POWEROFF = b'\x11\x0b'
    HIGH_ALTITUDE_MODE = b'\x11\x0c'
    LIGHT_SOURCE_MODE = b'\x11\x10'
    # X = b'\x11\x1a'
    # X = b'\x11\x1c'
    PROJECTOR_STATUS = b'\x11\x26'
    MESSAGE = b'\x11\x27'
    HDMI_FORMAT = b'\x11\x28'
    HDMI_RANGE = b'\x11\x29'
    RESET_COLOR_SETTINGS = b'\x11\x2a'
    CEC = b'\x11\x2b'
    EOTF = b'\x11\x2c'
    FRAME_INTERPOLATION = b'\x11\x2d'
    KEYSTONE_HORIZONTAL = b'\x11\x31'
    SCREEN_COLOR = b'\x11\x32'
    OVER_SCAN = b'\x11\x33'
    PROJ_360 = b'\x11\x36'
    LENS_FOCUS = b'\x11\x37'
    DIGITAL_LENS_SHIFT_VERTICAL = b'\x11\x39'
    DIGITAL_LENS_SHIFT_HORIZONTAL = b'\x11\x3a'

    PROJECTOR_POSITION = b'\x12\x00'
    CONTRAST =  b'\x12\x02'
    BRIGHTNESS =  b'\x12\x03'
    ASPECT_RATIO =  b'\x12\x04'
    AUTO_ADJUST =  b'\x12\x05'
    HORIZONTAL_POSITION =  b'\x12\x06'
    VERTICAL_POSITION =  b'\x12\x07'
    COLOR_TEMPERATURE =  b'\x12\x08'
    BLANK = b'\x12\x09'
    KEYSTONE_VERTICAL = b'\x12\x0a'
    COLOR_MODE = b'\x12\x0b'
    SHARPNESS = b'\x12\x0e'
    BRILLIANT_COLOR = b'\x12\x0f'
    PRIMARY_COLOR = b'\x12\x10'
    HUE_TINT = b'\x12\x11'
    SATURATION = b'\x12\x12'
    GAIN = b'\x12\x13'
    # X = b'\x12\x16'
    # X = b'\x12\x17'
    # X = b'\x12\x18'
    PROJECTOR_3D_SYNC =  b'\x12\x20'
    PROJECTOR_3D_SYNC_INVERT = b'\x12\x21'
    # X = b'\x12\x30'
    # X = b'\x12\x31'
    # X = b'\x12\x32'
    COLOR_MODE_CYCLE = b'\x13\x33'
    ISF_MODE = b'\x12\x38'
    HDR = b'\x12\x39'
    COLOR_TEMPERATURE_RED_GAIN_ADJUST = b'\x12\x3a\x00' #TODO header is b'\x06\x14\x00\x05\x00' + b'\x34'
    COLOR_TEMPERATURE_GREEN_GAIN_ADJUST = b'\x12\x3a\x01' #TODO header is b'\x06\x14\x00\x05\x00' + b'\x34'
    COLOR_TEMPERATURE_BLUE_GAIN_ADJUST = b'\x12\x3a\x02' #TODO header is b'\x06\x14\x00\x05\x00' + b'\x34'
    COLOR_TEMPERATURE_RED_GAIN = b'\x12\x3b'
    COLOR_TEMPERATURE_GREEN_GAIN = b'\x12\x3c'
    COLOR_TEMPERATURE_BLUE_GAIN = b'\x12\x3d'
    COLOR_TEMPERATURE_RED_OFFSET_ADJUST = b'\x12\x3e\x00' #TODO header is b'\x06\x14\x00\x05\x00' + b'\x34'
    COLOR_TEMPERATURE_GREEN_OFFSET_ADJUST = b'\x12\x3e\x01' #TODO header is b'\x06\x14\x00\x05\x00' + b'\x34'
    COLOR_TEMPERATURE_BLUE_OFFSET_ADJUST = b'\x12\x3e\x02' #TODO header is b'\x06\x14\x00\x05\x00' + b'\x34'
    COLOR_TEMPERATURE_RED_OFFSET = b'\x12\x3f'
    COLOR_TEMPERATURE_GREEN_OFFSET = b'\x12\x40'
    COLOR_TEMPERATURE_BLUE_OFFSET = b'\x12\x41'
    # X = b'\x12\x50'
    # X = b'\x12\x51'

    FREEZE =  b'\x13\x00'
    SOURCE_INPUT = b'\x13\x01'
    QUICK_AUTO_SEARCH = b'\x13\x02'
    ASPECT_RATIO_CYCLE =  b'\x13\x31'
    AUDIO_MODE_CYCLE = b'\x13\x35'
    LAMP_MODE_CYCLE = b'\x13\x36'

    MUTE = b'\x14\x00'
    VOLUME_UP = b'\x14\x01'
    VOLUME_DOWN = b'\x14\x02'
    VOLUME = b'\x14\x03' # check that 
    AUDIO_MODE = b'\x14\x05'

    LANGUAGE = b'\x15\x00'
    LIGHT_SOURCE_USAGE_TIME = b'\x15\x01'
    OPERATING_TEMPERATURE = b'\x15\x03'
    # X = b'\x15\x0a'
    # X = b'\x15\x42'
    # X = b'\x15\x43'
    # X = b'\x15\x44'
    # X = b'\x15\x45'
    # X = b'\x15\x49'

    # X = b'\x16\x01'
    # X = b'\x16\x40'
    # X = b'\x16\x41'
    # X = b'\x16\x8a'
    # X = b'\x16\x8b'
    # X = b'\x16\x8c'
    # X = b'\x16\x8d'
    # X = b'\x16\x8e'
    # X = b'\x16\x8f'
    # X = b'\x16\x99'
    # X = b'\x16\xa3'
    # X = b'\x16\xa4'

    # X = b'\x40\x87'
    # X = b'\x40\x89'

EMPTY = b'\x00'

class Gamma:
    GAMMA_1_8 = b'0x00'
    GAMMA_2 = b'0x01'
    GAMMA_2_2 = b'0x02'
    GAMMA_2_35 = b'0x03'
    GAMMA_2_5 = b'0x04'
    GAMMA_sRGB = b'0x05'
    GAMMA_Cubic = b'0x06'

class AudioMode:
    MOVIE = b'0x04'
    MUSIC = b'0x05'
    USER = b'0x06'

class PowerStatus:
    '''
    Power On: System is finished all HW/FW settings and ready to work.
    Warm Up: System is at initial stage to set and check HW/FW environment. Please do not perform other commands.
    Cool Down: System is at final stage to close HW/FW environment. Please do not perform other commands.
    Power Off: System is turned off all HW/FW except MCU or LAN functions with LAN standy setting.
    '''
    WARM_UP = 2
    COOL_DOWN = 3
    ON = 1
    OFF = 0

class Bool:
    OFF = b'\x00'
    ON = b'\x01'

class Adjustment:
    DECREASE = b'\x00'
    INCREASE = b'\x01'
   
class SplashScreen:
    BLACK = b'\x00'
    BLUE = b'\x01'
    VIEWSONIC = b'\x02'
    SCREENCAPTURE = b'\x03'
    OFF = b'\x04'

class LightSourceMode:
    NORMAL = b'\x00'
    ECO = b'\x01'
    DYNAMIC_ECO = b'\x02'
    SUPER_ECO = b'\x03'

class ProjectorPosition:
    FRONT_TABLE = b'\x00'
    REAR_TABLE = b'\x01'
    FRONT_CEILING = b'\x02'
    REAR_CEILING = b'\x03'

class Projector3DSync:
    PROJECTOR_3D_SYNC_OFF =  b'\x00'
    PROJECTOR_3D_SYNC_AUTO =  b'\x01'
    PROJECTOR_3D_SYNC_FRAME_SEQUENTIAL =  b'\x02'
    PROJECTOR_3D_SYNC_FRAME_PACKING =  b'\x03'
    PROJECTOR_3D_SYNC_TOP_BOTTOM =  b'\x04'
    PROJECTOR_3D_SYNC_SIDE_BY_SIDE =  b'\x05'

class AspectRatio:
    AR_AUTO = b'\x00'
    AR_4_TO_3 = b'\x02'
    AR_16_TO_9 = b'\x03'
    AR_16_TO_10 = b'\x04'
    AR_ANAMORPHIC = b'\x05'
    AR_WIDE = b'\x06'
    AR_2_35_TO_1 = b'\x07'
    AR_PANORAMA = b'\x08'
    AR_NATIVE = b'\x09'

# TODO
class CornerAdjust:
    TOP_RIGHT = b''
    TOP_LEFT = b''
    BOTTOM_RIGHT = b''
    BOTTOM_LEFT = b''

class HorizontalPosition:
    SHIFT_LEFT = b'\x00'
    SHIFT_RIGHT = b'\x01'
    
class VerticalPosition:
    SHIFT_UP = b'\x00'
    SHIFT_DOWN = b'\x01'

class ColorTemperature:
    WARM = b'\x00'
    NORMAL = b'\x01'
    NEUTRAL = b'\x02'
    COOL = b'\x03'

class ColorMode:
    BRIGHTEST = b'\x00'
    MOVIE = b'\x01'
    STANDARD = b'\x04'
    sRGB = b'\x05'
    DYNAMIC = b'\x08'
    Rec709 = b'\x09'
    DICOM_SIM = b'\x0a'
    SPORTS = b'\x11'
    PHOTO = b'\x13'
    PRESENTATION = b'\x14'
    GAMING = b'\x12'
    VIVID = b'\x15'
    ISF_DAY = b'\x16'
    ISF_NIGHT = b'\x17'

class HDR:
    AUTO = b'\x00'
    SDR = b'\x01'

class PrimaryColor:
    R = b'\x00'
    G = b'\x01'
    B = b'\x02'
    C = b'\x03'
    M = b'\x04'
    Y = b'\x05'

class SourceInput:
    D_SUB_COMP1 = b'\x00'
    D_SUB_COMP2 = b'\x08'
    HDMI1 = b'\x03'
    HDMI2 = b'\x07'
    HDMI3 = b'\x09'
    HDMI_MHL4 = b'\x0e'
    COMPOSITE = b'\x05'
    S_VIDEO = b'\x06'
    DVI = b'\x0a'
    COMPONENT = b'\x0b'
    HDBaseT = b'\x0c'
    USB_C = b'\x0f'
    USB_Reader = b'\x1a'
    LAN_WIFI_Display = b'\x1b'
    USB_Display = b'\x1c'

class Language:
    ENGLISH = b'\x00'
    FRENCH = b'\x01'
    GERMAN = b'\x02'
    ITALIAN = b'\x03'
    SPANISH = b'\x04'
    RUSSIAN = b'\x05'
    CHINESE = b'\x06'
    SIMPLIFIED_CHINESE = b'\x07'
    JAPANESE = b'\x08'
    KOREAN = b'\x09'
    SWEDISH = b'\x0a'
    DUTCH = b'\x0b'
    TURKISH = b'\x0c'
    CZECH = b'\x0d'
    PORTUGESE = b'\x0e'
    THAI = b'\x0f'
    POLISH = b'\x10'
    FINNISH = b'\x11'
    ARABIC = b'\x12'
    INDONESIAN = b'\x13'
    HINDI = b'\x14'
    VIETNAMESE = b'\x15'

class HDMIFormat:
    RGB = b'\x00'
    YUV = b'\x01'
    AUTO = b'\x02'

class HDMIRange:
    ENHANCED = b'\x00'
    NORMAL = b'\x01'
    AUTO = b'\x02'

class BrilliantColor:
    COLOR_01 = b'\x01'
    COLOR_02 = b'\x02'
    COLOR_03 = b'\x03'
    COLOR_04 = b'\x04'
    COLOR_05 = b'\x05'
    COLOR_06 = b'\x06'
    COLOR_07 = b'\x07'
    COLOR_08 = b'\x08'
    COLOR_09 = b'\x09'
    COLOR_10 = b'\x0a'

class RemoteControlCode:
    CODE_01 = b'\x00'
    CODE_02 = b'\x01'
    CODE_03 = b'\x02'
    CODE_04 = b'\x03'
    CODE_05 = b'\x04'
    CODE_06 = b'\x05'
    CODE_07 = b'\x06'
    CODE_08 = b'\x07'

class ScreenColor:
    OFF = b'\x00'
    BLACKBOARD = b'\x01'
    GREENBOARD = b'\x02'
    WHITEBOARD = b'\x03'
    BLUEBOARD = b'\x04'

class OverScan:
    OFF = b'\x00'
    VALUE_01 = b'\x01'
    VALUE_02 = b'\x02'
    VALUE_03 = b'\x03'
    VALUE_04 = b'\x04'  
    VALUE_05 = b'\x05' 

class RemoteKey:
    MENU = b'\x0f'
    EXIT = b'\x13'
    TOP = b'\x0b'
    BOTTOM = b'\x0c'
    LEFT = b'\x0d'
    RIGHT = b'\x0e'
    SOURCE = b'\x04'
    ENTER = b'\x15'
    AUTO = b'\x08'
    MY_BUTTON = b'\x11'
    BLUETOOTH = b'\x26'
    RETURN = b'\x27'
    NEXT_TRACK = b'\x28'
    PREVIOUS_TRACK = b'\x29'
    PLAY = b'\x2a'
    SUB_MENU = b'\x2b'

RESPONSE_INT_TO_ONE_BYTE = {
    i: HEADER.READ_RESPONSE_ONE_BYTE + bytes([i, (0x17 + i) % 256]) for i in range(256)
}
RESPONSE_ONE_BYTE_TO_INT = {v: k for k,v in RESPONSE_INT_TO_ONE_BYTE.items()}

RESPONSE_INT_TO_TWO_BYTE = {
    i: (HEADER.READ_RESPONSE_TWO_BYTE + bytes([i, 0x00, (0x18 + i) % 256])
    if i >= 0
    else HEADER.READ_RESPONSE_TWO_BYTE + bytes([i + 256, 0xFF, (0x17 + i) % 256]))
    for i in range(-255, 256)
}
RESPONSE_TWO_BYTE_TO_INT = {v: k for k,v in RESPONSE_INT_TO_TWO_BYTE.items()}

def checksum(packet: bytes) -> bytes:
    '''compute checksum as the sum of bytes 1 to end'''
    return (sum(packet[1:]) % 256).to_bytes()

def payload_length(header: bytes) -> int:
    '''get payload length from header (data + checksum)'''
    lsb = header[3] 
    msb = header[4]
    ck = 1 # 1-byte checksum at the end
    return lsb + (msb << 8) + ck

class ViewSonicProjector:
    '''
    Requires a crossover (null modem) cable for use with PC
    Only 3 pins need to be connected (RX,TX and GND)
    '''

    VALID_BAUD_RATES = [2400,4800,9600,14400,19200,38400,115200]

    def __init__(
        self,
        port: str = '/dev/ttyUSB0',
        baudrate: int = 115200,
        data_byte_length = serial.EIGHTBITS,
        parity_check = serial.PARITY_NONE,
        num_stop_bit: int = serial.STOPBITS_ONE,
        timeout: Optional[float] = 10.0,
        write_timeout: Optional[float] = 1.0,
        flow_control: bool = False,
        verbose: bool = False
        ):

        if baudrate not in self.VALID_BAUD_RATES:
            raise ValueError(f'Supported baud rates are: {self.VALID_BAUD_RATES}')
        
        self.port = port
        self.baudrate = baudrate
        self.data_byte_length = data_byte_length
        self.parity_check = parity_check
        self.num_stop_bit = num_stop_bit
        self.timeout = timeout
        self.write_timeout = write_timeout
        self.flow_control = flow_control
        self.verbose = verbose

        self.ser = serial.Serial(
            port = port,
            baudrate = baudrate,
            bytesize = data_byte_length,
            parity = parity_check,
            stopbits = num_stop_bit,
            timeout = timeout,
            write_timeout= write_timeout,
            rtscts = flow_control
        )

    def __del__(self):
        self.ser.close()

    def power_on(self):
        self._send_write_packet(CMD.POWER_ON + EMPTY)

        while True:
            res = self.get_power_status()
                
            if res == PowerStatus.WARM_UP:
                time.sleep(1)

            elif res == PowerStatus.ON:
                break

            else:
                raise ValueError

    
    def power_off(self):
        self._send_write_packet(CMD.POWER_OFF + EMPTY)

        # Wait until the projector has cooled down
        while True:
            res = self.get_power_status()

            if res == PowerStatus.COOL_DOWN:
                time.sleep(1)

            elif res == PowerStatus.OFF:
                break
            
            else:
                raise ValueError 
            
    def set_gamma(self, data: Gamma):
        self._send_write_packet(CMD.GAMMA + data)

    def get_gamma(self) -> int:
        return self._send_read_packet_one_byte(CMD.GAMMA)

    def set_audio_mode(self, data: AudioMode):
        self._send_write_packet(CMD.AUDIO_MODE + data)

    def get_audio_mode(self) -> int:
        return self._send_read_packet_one_byte(CMD.AUDIO_MODE)
    
    def get_power_status(self) -> int:
        return self._send_read_packet_one_byte(CMD.POWER_ON)
    
    def get_projector_status(self) -> int:
        return self._send_read_packet_one_byte(CMD.PROJECTOR_STATUS)
    
    def reset_all_settings(self):
        self._send_write_packet(CMD.RESET_ALL_SETTINGS + EMPTY)

    def reset_color_settings(self):
        self._send_write_packet(CMD.RESET_COLOR_SETTINGS + EMPTY)

    def set_splash_screen(self, data: SplashScreen):
        self._send_write_packet(CMD.RESET_COLOR_SETTINGS + data)

    def set_quick_poweroff(self, data: Bool):
        self._send_write_packet(CMD.QUICK_POWEROFF + data)

    def get_quick_poweroff(self) -> int:
        return self._send_read_packet_one_byte(CMD.QUICK_POWEROFF)
    
    def set_high_altitude_mode(self, data: Bool):
        self._send_write_packet(CMD.HIGH_ALTITUDE_MODE + data)

    def get_high_altitude_mode(self) -> int:
        return self._send_read_packet_one_byte(CMD.HIGH_ALTITUDE_MODE)
    
    def set_light_source_mode(self, data: LightSourceMode):
        self._send_write_packet(CMD.LIGHT_SOURCE_MODE + data)

    def get_light_source_mode(self) -> int:
        return self._send_read_packet_one_byte(CMD.LIGHT_SOURCE_MODE)
    
    def set_message(self, data: Bool):
        self._send_write_packet(CMD.MESSAGE + data)

    def get_message(self) -> int:
        return self._send_read_packet_one_byte(CMD.MESSAGE)

    def set_projector_position(self, data: ProjectorPosition):
        self._send_write_packet(CMD.PROJECTOR_POSITION + data)

    def get_projector_position(self) -> int:
        return self._send_read_packet_one_byte(CMD.PROJECTOR_POSITION)
    
    def set_projector_3d_sync(self, data: Projector3DSync):
        self._send_write_packet(CMD.PROJECTOR_3D_SYNC + data)

    def get_projector_3d_sync(self) -> int:
        return self._send_read_packet_one_byte(CMD.PROJECTOR_3D_SYNC)
    
    def set_projector_3d_sync_invert(self, data: Bool):
        self._send_write_packet(CMD.PROJECTOR_3D_SYNC_INVERT + data)

    def get_projector_3d_sync_invert(self) -> int:
        return self._send_read_packet_one_byte(CMD.PROJECTOR_3D_SYNC_INVERT)    
    
    def adjust_contrast(self, data: Adjustment):
        self._send_write_packet(CMD.CONTRAST + data)

    def get_contrast(self) -> int:
        return self._send_read_packet_two_byte(CMD.CONTRAST)
 
    def adjust_brightness(self, data: Adjustment):
        self._send_write_packet(CMD.BRIGHTNESS + data)

    def get_brightness(self) -> int:
        return self._send_read_packet_two_byte(CMD.BRIGHTNESS)
    
    def set_aspect_ratio(self, data: AspectRatio):
        self._send_write_packet(CMD.ASPECT_RATIO + data)

    def get_aspect_ratio(self) -> int:
        return self._send_read_packet_one_byte(CMD.ASPECT_RATIO)
    
    def cycle_aspect_ratio(self):
        self._send_write_packet(CMD.ASPECT_RATIO_CYCLE + EMPTY)

    def auto_adjust(self):
        self._send_write_packet(CMD.AUTO_ADJUST + EMPTY)

    def set_horizontal_position(self, data: HorizontalPosition):
        self._send_write_packet(CMD.HORIZONTAL_POSITION + data)

    def get_horizontal_position(self) -> int:
        return self._send_read_packet_one_byte(CMD.HORIZONTAL_POSITION)

    def set_vertical_position(self, data: VerticalPosition):
        self._send_write_packet(CMD.VERTICAL_POSITION + data)

    def get_vertical_position(self) -> int:
        return self._send_read_packet_one_byte(CMD.VERTICAL_POSITION)

    def set_color_temperature(self, data: ColorTemperature):
        self._send_write_packet(CMD.COLOR_TEMPERATURE + data)

    def get_color_temperature(self) -> int:
        return self._send_read_packet_one_byte(CMD.COLOR_TEMPERATURE)

    def set_blank(self, data: Bool):
        self._send_write_packet(CMD.BLANK + data)

    def get_blank(self) -> int:
        return self._send_read_packet_one_byte(CMD.BLANK)

    def adjust_vertical_keystone(self, data: Adjustment):
        self._send_write_packet(CMD.KEYSTONE_VERTICAL + data)

    def get_vertical_keystone(self) -> int:
        return self._send_read_packet_one_byte(CMD.KEYSTONE_VERTICAL)

    def adjust_horizontal_keystone(self, data: Adjustment):
        self._send_write_packet(CMD.KEYSTONE_HORIZONTAL + data)

    def get_horizontal_keystone(self) -> int:
        return self._send_read_packet_one_byte(CMD.KEYSTONE_HORIZONTAL)

    def set_color_mode(self, data: ColorMode):
        self._send_write_packet(CMD.COLOR_MODE + data)

    def get_color_mode(self) -> int:
        return self._send_read_packet_one_byte(CMD.COLOR_MODE)
    
    def cycle_color_mode(self):
        self._send_write_packet(CMD.COLOR_MODE_CYCLE + EMPTY)

    def set_ISF_mode(self, data: Bool):
        self._send_write_packet(CMD.ISF_MODE + data)

    def get_ISF_mode(self) -> int:
        return self._send_read_packet_one_byte(CMD.ISF_MODE)

    def set_HDR(self, data: HDR):
        self._send_write_packet(CMD.HDR + data)

    def get_HDR(self) -> int:
        return self._send_read_packet_one_byte(CMD.HDR)

    def set_primary_color(self, data: PrimaryColor):
        self._send_write_packet(CMD.PRIMARY_COLOR + data)

    def get_primary_color(self) -> int:
        return self._send_read_packet_one_byte(CMD.PRIMARY_COLOR)

    def adjust_hue(self, data: Adjustment):
        self._send_write_packet(CMD.HUE_TINT + data)

    def get_hue(self) -> int:
        return self._send_read_packet_two_byte(CMD.HUE_TINT)

    def adjust_saturation(self, data: Adjustment):
        self._send_write_packet(CMD.SATURATION + data)

    def get_saturation(self) -> int:
        return self._send_read_packet_two_byte(CMD.SATURATION)

    def adjust_gain(self, data: Adjustment):
        self._send_write_packet(CMD.GAIN + data)

    def get_gain(self) -> int:
        return self._send_read_packet_two_byte(CMD.GAIN)
    
    def adjust_sharpness(self, data: Adjustment):
        self._send_write_packet(CMD.SHARPNESS + data)

    def get_sharpness(self) -> int:
        return self._send_read_packet_two_byte(CMD.SHARPNESS)

    def set_freeze(self, data: Bool):
        self._send_write_packet(CMD.FREEZE + data)

    def get_freeze(self) -> int:
        return self._send_read_packet_one_byte(CMD.FREEZE)

    def set_source_input(self, data: SourceInput):
        self._send_write_packet(CMD.SOURCE_INPUT + data)

    def get_source_input(self) -> int:
        return self._send_read_packet_one_byte(CMD.SOURCE_INPUT)        

    def set_quick_autosearch(self, data: Bool):
        self._send_write_packet(CMD.QUICK_AUTO_SEARCH + data)

    def get_quick_autosearch(self) -> int:
        return self._send_read_packet_one_byte(CMD.QUICK_AUTO_SEARCH)

    def set_mute(self, data: Bool):
        self._send_write_packet(CMD.MUTE + data)

    def get_mute(self) -> int:
        return self._send_read_packet_one_byte(CMD.MUTE)
    
    def volume_up(self):
        self._send_write_packet(CMD.VOLUME_UP + EMPTY)

    def volume_down(self):
        self._send_write_packet(CMD.VOLUME_DOWN + EMPTY)

    # CHECK THIS, THE DOC IS WEIRD 
    # is it setting the volume to eleven ? 
    # should I supply an integer ? 
    # What's the volume range ?
    def set_volume(self):
        self._send_write_packet(CMD.VOLUME + b'\x11')

    def get_volume(self):
        return self._send_read_packet_one_byte(CMD.VOLUME)

    def get_sharpness(self) -> int:
        return self._send_read_packet_two_byte(CMD.SHARPNESS)

    def set_language(self, data: Language):
        self._send_write_packet(CMD.LANGUAGE + data)

    def get_language(self) -> int:
        return self._send_read_packet_one_byte(CMD.LANGUAGE)    
        
    def reset_light_source_usage_time(self):
        self._send_write_packet(CMD.LIGHT_SOURCE_USAGE_TIME + EMPTY)

    def get_light_source_usage_time(self):
        # special case
        response = self._send_read_packet(CMD.LIGHT_SOURCE_USAGE_TIME)
        usage_time = int.from_bytes(response[7:11],byteorder='little')
        return usage_time

    def set_HDMI_format(self, data: HDMIFormat):
        self._send_write_packet(CMD.HDMI_FORMAT + data)

    def get_HDMI_format(self) -> int:
        return self._send_read_packet_one_byte(CMD.HDMI_FORMAT)           

    def set_HDMI_range(self, data: HDMIRange):
        self._send_write_packet(CMD.HDMI_RANGE + data)

    def get_HDMI_range(self) -> int:
        return self._send_read_packet_one_byte(CMD.HDMI_RANGE)

    def set_CEC(self, data: Bool):
        self._send_write_packet(CMD.CEC + data)

    def get_CEC(self) -> int:
        return self._send_read_packet_one_byte(CMD.CEC)
    
    def get_error_status(self):
        # special case
        response = self._send_read_packet(CMD.ERROR_STATUS)
        error_status = response[7:31]
        err = {}
        err['lamp_fail_count'] = error_status[0]
        err['lamp_lit_error_count'] = error_status[1]
        err['fan1_error_count'] = error_status[2]
        err['fan2_error_count'] = error_status[3]
        err['fan3_error_count'] = error_status[4]
        err['fan4_error_count'] = error_status[5]
        err['diode1_open_error_count'] = error_status[6]
        err['diode2_open_error_count'] = error_status[7]
        err['diode1_short_error_count'] = error_status[8]
        err['diode2_short_error_count'] = error_status[9]
        err['temperature1_error_count'] = error_status[10]
        err['temperature2_error_count'] = error_status[11]
        err['fan_IC1_error_count'] = error_status[12]
        err['color_wheel_error_count'] = error_status[13]
        err['color_wheel_startup_error_count'] = error_status[14]
        err['UART1_error_count'] = error_status[15]
        err['abnormal_powerdown'] = error_status[16]
        err['first_burn_in'] = int.from_bytes(error_status[17:21], byteorder='little')
        err['lamp_status'] = error_status[21]
        err['lamp_error_status'] = error_status[22:24]
        return err

    
    def set_brilliant_color(self, data: BrilliantColor):
        self._send_write_packet(CMD.BRILLIANT_COLOR + data)

    def get_brilliant_color(self) -> int:
        return self._send_read_packet_one_byte(CMD.BRILLIANT_COLOR)       

    def set_remote_control_code(self, data: RemoteControlCode):
        self._send_write_packet(CMD.REMOTE_CONTROL_CODE + data)

    def get_remote_control_code(self) -> int:
        return self._send_read_packet_one_byte(CMD.REMOTE_CONTROL_CODE)       

    def set_screen_color(self, data: ScreenColor):
        self._send_write_packet(CMD.SCREEN_COLOR + data)

    def get_screen_color(self) -> int:
        return self._send_read_packet_one_byte(CMD.SCREEN_COLOR)       

    def set_overscan(self, data: OverScan):
        self._send_write_packet(CMD.OVER_SCAN + data)

    def get_overscan(self) -> int:
        return self._send_read_packet_one_byte(CMD.OVER_SCAN)       

    def set_remote_key(self, data: RemoteKey):
        self._send_write_packet(CMD.REMOTE_KEY + data)

    def get_remote_key(self) -> int:
        return self._send_read_packet_one_byte(CMD.REMOTE_KEY)   
    
    def get_operating_temperature(self) -> float:
        # special case
        response = self._send_read_packet(CMD.OPERATING_TEMPERATURE)
        temperature = int.from_bytes(response[7:11],byteorder='little')/10
        return temperature

    def cycle_lamp_mode(self):
        self._send_write_packet(CMD.LAMP_MODE_CYCLE + EMPTY)

    def cycle_audio_mode(self):
        self._send_write_packet(CMD.AUDIO_MODE_CYCLE + EMPTY)

    def _send_packet(self, packet: bytes) -> bytes:

        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

        query = packet + checksum(packet)

        if self.verbose:
            print('>> ' + query.hex(' '))

        self.ser.write(query)

        response_header = self.ser.read(HEADER.NUM_BYTES)
        
        if len(response_header) != HEADER.NUM_BYTES:
            raise TransmissionError('failed to read response header')
        
        payload_num_bytes = payload_length(response_header)
        response_payload = self.ser.read(payload_num_bytes)

        if len(response_payload) != payload_num_bytes:
            raise TransmissionError('payload size mismatch')

        response = response_header + response_payload

        if self.verbose:
            print(response.hex(' '))
            print()
        
        if checksum(response[:-1]) != response[-1:]:
            raise TransmissionError('invalid checksum')

        if response == HEADER.DISABLED:
            raise FunctionDisabled
        
        if response == HEADER.PROJ_OFF:
            raise ProjectorOFF

        return response

    def _send_write_packet(self, packet: bytes):

        response = self._send_packet(HEADER.WRITE + packet)

        if response != HEADER.ACK:
            raise CommandFailed

    def _send_read_packet(self, packet: bytes) -> bytes:

        response = self._send_packet(HEADER.READ + packet)
        return response

    def _send_read_packet_one_byte(self, packet: bytes) -> int:

        response = self._send_read_packet(packet)        
        return RESPONSE_ONE_BYTE_TO_INT[response]
    
    def _send_read_packet_two_byte(self, packet: bytes) -> int:

        response = self._send_read_packet(packet)
        return RESPONSE_TWO_BYTE_TO_INT[response]

SCANFILE = 'scan.json'

def scan(proj: ViewSonicProjector) -> Dict:

    res = {}

    if os.path.exists(SCANFILE):

        print('scan file found, loading commands')

        with open(SCANFILE,'r') as f:
            commands = json.load(f)

        for hex in commands.keys():
            cmd = bytes.fromhex(hex)
            try:
                response = proj._send_read_packet(cmd)
                res[cmd.hex(' ')] = response.hex(' ')
            except FunctionDisabled:
                pass

    else:

        print('scan file not found, performing an exhaustive scan')

        for cmd2 in range(256): 
            for cmd3 in range(256):
                cmd = bytes([cmd2, cmd3])
                try:
                    response = proj._send_read_packet(cmd)
                    res[cmd.hex(' ')] = response.hex(' ')
                except FunctionDisabled:
                    pass
        
        with open(SCANFILE,'w') as f:
            commands = json.dump(res,f)
        
    return res    

def reverse_engineer(proj: ViewSonicProjector):
    '''reverse engineer command codes
       - exhaustive scan of cmd2/cmd3 space using read query (should be safe)
       - modify setting with projector OSD
       - exhaustive scan of cmd2/cmd3 space using read query
       - check which values have changed (hopefully only one, but some OSD settings might alter several registers at once)
    '''

    
    scan1 = scan(proj)
    input('Change function on the projector using OSD. Press Enter when done')
    scan2 = scan(proj)
    diff = set(scan1.items()) ^ set(scan2.items()) 
    return diff
    
if __name__ == '__main__':

    proj = ViewSonicProjector(verbose=True)
    proj.power_on()
    time.sleep(20)
    proj.power_off()