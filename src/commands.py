from functools import reduce
from operator import xor
from dataclasses import dataclass, field
from time import sleep
from queue import Queue
import serial
import struct
import threading



# region ---------------------------------------------------------------------- | Communication Protocol |
@dataclass(slots=True)
class CommunicationProtocol:
  protocol_version              : str                = field(init=True, default='1.0')
  start_byte                    : bytes              = field(init=False)
  stop_byte                     : bytes              = field(init=False)
  names                         : dict[bytes, str  ] = field(init=False)
  commands                      : dict[str  , bytes] = field(init=False)
  formats_from_command          : dict[bytes, str  ] = field(init=False)
  formats_from_name             : dict[str  , int  ] = field(init=False)
  conversion_factor_from_command: dict[bytes, str  ] = field(init=False)
  conversion_factor_from_name   : dict[str  , int  ] = field(init=False)
  lengths_from_command          : dict[bytes, int  ] = field(init=False)
  lengths_from_name             : dict[str  , int  ] = field(init=False)
  min_length                    : int                = field(init=False)
  max_length                    : int                = field(init=False)


  def __post_init__(self):
    self.set_version(self.protocol_version)


  def lrc(self, byte_string: bytes) -> bytes:
    return reduce(xor, byte_string).to_bytes(1, 'big')


  def set_version(self, version: str) -> None:
    match version:
      case '1.0':
        tuples = (
          (b'\x03', 'get_register_value',                   '>BB', None),
          (b'\x70', 'tick_mode',                            '>BB', None),
          (b'\x71', 'tick_enable',                          '>BB', None),
          (b'\x72', 'tick_current',                         '>h', 1000),
          (b'\x73', 'tick_angle_cw',                        '>H', 10),
          (b'\x74', 'tick_duration_min',                    '>H', 1000),
          (b'\x75', 'tick_duration_max',                    '>H', 1000),
          (b'\x76', 'tick_velocity_factor',                 '>h', 1000),
          (b'\x77', 'tick_index_window',                    '>H', 10),
          (b'\x78', 'tick_stickiness_prevention_factor',    '>H', 100),
          (b'\x79', 'ticke_angle_ccw',                      '>H', 10),
          (b'\x7A', 'tick_active_direction',                '>BB', None),
          (b'\x7B', 'tick_freewheeling_velocity_threshold', '>H', 10),
          (b'\x7C', 'tick_freewheeling_extension_time',     '>H', 1000),
          (b'\x7D', 'tick_window',                          '>H', 10),
          (b'\x7E', 'tick_start_angle',                     '>h', 10),
          (b'\x7F', 'tick_stop_angle',                      '>h', 10),
          (b'\xE0', 'report_encoder_angle',                 '>H', 100),
          (b'\xE1', 'report_encoder_velocity',              '>h', 1),
          (b'\xE5', 'report_encoder_multi_turn_counter',    '>h', 1),
        )

      case _:
        raise ValueError(f'`{version}` is not a valid Version.')

    self.protocol_version = version
    self.start_byte = b'\x26'
    self.stop_byte  = b'\x0D'

    # conversion between command names and command bytes
    self.names    = {cmd : name for cmd, name, format, factor in tuples}
    self.commands = {name: cmd  for cmd, name, format, factor in tuples}

    # get formating information from command byte or command name
    self.formats_from_command = {cmd : format for cmd, name, format, factor in tuples}
    self.formats_from_name    = {name: format for cmd, name, format, factor in tuples}

    # get command length from command byte or command name
    self.lengths_from_command = {cmd: struct.calcsize(format) + 4 for cmd, name, format, factor in tuples}
    self.lengths_from_name    = {cmd: struct.calcsize(format) + 4 for cmd, name, format, factor in tuples}

    # get conversion factor
    self.conversion_factor_from_command = {cmd : factor for cmd, name, format, factor in tuples}
    self.conversion_factor_from_name    = {name: factor for cmd, name, format, factor in tuples}

    # calc min and max length of all commands
    self.min_length = min(self.lengths_from_command.values())
    self.max_length = max(self.lengths_from_command.values())

PROTOCOL = CommunicationProtocol()
# endregion



# region ------------------------------------------------------------------------------------ | Input Queue |
def read_from_port(ser: serial.Serial, buffer: bytes) -> bytes:
  bytes_arr = bytearray(buffer)
  while ser.in_waiting > 0:
    bytes_arr.extend(ser.read(10000))
  return bytes(bytes_arr)



def validate_message(buffer: bytes) -> tuple[bytes | None, int]:
  idx = lambda i: slice(i, i + 1)

  # Valid command type
  type_byte = buffer[idx(1)]
  if type_byte not in PROTOCOL.formats_from_command.keys():
    return None, 0

  # Incomplete Message
  buffer_size = len(buffer)
  cmd_len = PROTOCOL.lengths_from_command[type_byte]
  if buffer_size < cmd_len:
    return None, 0
  
  # Incorrect stop byte
  if buffer[idx(cmd_len-1)] != PROTOCOL.stop_byte:
    return None, 0

  # Longitudinal redundancy ckeck
  lrc_byte     = buffer[idx(cmd_len-2)]
  command_body = buffer[1:cmd_len-2]
  if lrc_byte != PROTOCOL.lrc(command_body):
    return None, 0

  return buffer[:cmd_len], cmd_len



def slice_messages(buffer: bytes) -> tuple[list[bytes], bytes]:
  messages = []
  buffer_size = len(buffer)

  i = 0
  while i < buffer_size + 1 - PROTOCOL.min_length:
    if buffer[i:i+1] == PROTOCOL.start_byte:
      message, message_length = validate_message(buffer[i:i + PROTOCOL.max_length])
    else:
      message = None

    if message is not None:
      messages.append(message)
      i += message_length
    else:
      i += 1

  return messages, buffer[i:]



def unpack_messages(messages: list[bytes]) -> list[tuple[bytes, ...]]:
  return [(msg[1:2], *struct.unpack(PROTOCOL.formats_from_command[msg[1:2]], msg[2:-2])) for msg in messages]



def deserialize(ser: serial.Serial, buffer: bytes, queue: Queue):
  buffer = read_from_port(ser, buffer)
  messages, buffer = slice_messages(buffer)
  messages = unpack_messages(messages)
  #print(messages)
  if len(messages) > 0: queue.put(messages)
  return buffer
# endregion



# region ------------------------------------------------------------------------------------ | Ouput Queue |
def pack_command(*args) -> bytes:
  body = args[0] + struct.pack(PROTOCOL.formats_from_command[args[0]], *args[1:])
  lrc_byte = PROTOCOL.lrc(body)
  return b''.join([PROTOCOL.start_byte, body, lrc_byte, PROTOCOL.stop_byte])



def serialize(ser: serial.Serial, queue: Queue) -> None:
  buffer = bytearray()
  while queue.qsize() > 0:
    buffer.extend(pack_command(*queue.get_nowait()))
  ser.write(buffer)
# endregion



# region ------------------------------------------------------------------------------------ | Serial Data |
def process_serial_data(
  port            : str,
  protocol_version: str,
  stop_event      : threading.Event,
  input_queue     : Queue,
  output_queue    : Queue,
):
  sleep_time = 0.1
  timeout = 0.1

  try:
    with serial.Serial(port, 115200, timeout=timeout) as ser:
      PROTOCOL.set_version(protocol_version)
      buffer = bytes()

      while not stop_event.is_set():
        buffer = deserialize(ser, buffer, input_queue)
        serialize(ser, output_queue)
        sleep(sleep_time)
  except serial.SerialException as e:
    print(f"Error with {port}: {e}")
# endregion

