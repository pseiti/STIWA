# region ------------------------------------------------------------------------------------ | Getter / Setter |
from src.commands import *
import time


def set_register(register_name: str, value: int, output_queue: Queue):

    if register_name not in PROTOCOL.commands:
        raise ValueError(f"Register '{register_name}' not found in protocol.")

    # Get the command byte for the register name
    command_byte = PROTOCOL.commands[register_name]

    # Check if the register has a conversion factor
    factor = PROTOCOL.conversion_factor_from_name.get(register_name)
    if factor:
        value = int(value * factor)  # Multiply the value by the factor before sending


    output_queue.put((command_byte, 0, value) if PROTOCOL.formats_from_command[command_byte] == '>BB' else (command_byte, value))
    # print(f"Set command for {register_name} (command {command_byte.hex()}) sent with value {value}.")



def get_register(register_name: str, output_queue: Queue, input_queue: Queue, timeout: float = 1.0) -> int:
    if register_name not in PROTOCOL.commands:
        raise ValueError(f"Register '{register_name}' not found in protocol.")

    # Get the command byte for the register name
    command_byte = PROTOCOL.commands[register_name]

    get_register_command_byte = PROTOCOL.commands['get_register_value']

    # Send the command to get the value
    output_queue.put((get_register_command_byte, 0, command_byte[0]))
    # print(f"Get command for {register_name} (command {command_byte.hex()}) sent.")

    # Wait for a response on the input queue
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if not input_queue.empty():
                messages = input_queue.get_nowait()
                for message in messages:
                    if message[0] == command_byte:
                        # Unpack and get the value
                        value = message[2 if PROTOCOL.formats_from_command[command_byte] == '>BB' else 1]

                        # Check if the register has a conversion factor
                        factor = PROTOCOL.conversion_factor_from_name.get(register_name)
                        if factor:
                            value = value / factor  # Divide the value by the factor after receiving

                        return value
        except Queue.Empty:
            pass
        sleep(0.1)

    raise TimeoutError(f"Timeout waiting for response for register '{register_name}'.")

def get_report_register(register_name: str, input_queue: Queue) -> int:
    if register_name not in PROTOCOL.commands:
        raise ValueError(f"Register '{register_name}' not found in protocol.")

    # Get the command byte for the register name
    command_byte = PROTOCOL.commands[register_name]

    # Wait for a response on the input queue
    try:
        if not input_queue.empty():
            # print("not empty")
            messages = input_queue.get_nowait()
            for message in messages:
                if message[0] == command_byte:
                    # Unpack and get the value
                    value = message[2 if PROTOCOL.formats_from_command[command_byte] == '>BB' else 1]

                    # Check if the register has a conversion factor
                    factor = PROTOCOL.conversion_factor_from_name.get(register_name)
                    if factor:
                        value = value / factor  # Divide the value by the factor after receiving

                    return value
    except Queue.Empty:
        pass
    sleep(0.1)

    #raise TimeoutError(f"Timeout waiting for response for register '{register_name}'.")

# endregion