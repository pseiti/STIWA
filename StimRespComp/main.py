from src.haptic_core_serial import *

def initialization():
    #All set/get commands that need to be executed once, can be placed inside this function according to be following scheme:
    #set_register(<Register_Name>, <Value>, output_queues['hcc1'])                  ---> available register names can be found in the set_versions function in commands.py
    #set_register('tick_mode', 2, output_queues['hcc1'])                            ---> Example Command

    #get_register(<Register_Name>, output_queues['hcc1'], input_queues['hcc1'])     ---> available register names can be found in the set_versions function in commands.py
    #get_register('tick_current', 2, output_queues['hcc1'], input_queues['hcc1'])   ---> Example Command

    tick_current_value = get_register('tick_current', output_queues['hcc1'], input_queues['hcc1'])
    print(f"The value of 'tick_current' is: {tick_current_value}")

def application_tick():
    #All get commands that need to constantly return REPORT REGISTERS, can be placed inside this function according to be following scheme:
    #get_report_register(<Register_Name>, input_queues['hcc1'])                     ---> available register names can be found in the set_versions function in commands.py (on)
    print(get_report_register('report_encoder_angle', input_queues['hcc1']))              #---> Example Command

    #To terminate this function hit Ctrl + C in the terminal
    pass


if __name__ == "__main__":
    # load settings
    ports = {
        'hcc1': 'COM3' #Edit according to connection port
    }
    protocol_version = '1.0'


    # region ----------------------------------------------------- | Serial Communication |
    stop_event = threading.Event()
    input_queues = {hcc: Queue() for hcc in ports.keys()}
    output_queues = {hcc: Queue() for hcc in ports.keys()}
    threads: list[threading.Thread] = []

    for hcc in ports.keys():
        threads.append(threading.Thread(
            target=process_serial_data,
            args=(ports[hcc], protocol_version, stop_event, input_queues[hcc], output_queues[hcc])
        ))
    # endregion


    # region --------------------------------------------------------------------- | Main |
    try:
        for thread in threads:
            print(thread)
            thread.start()
        print('Initialized')

        initialization()
        while True:
            application_tick()
            sleep(0.1)
  

    except KeyboardInterrupt:
        print("Program terminated by user")
        stop_event.set()
        for thread in threads:
            thread.join()

    finally:
        stop_event.set()
        for thread in threads:
            thread.join()
    # endregion
