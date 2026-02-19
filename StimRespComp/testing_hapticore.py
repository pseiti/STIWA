import threading
from src.haptic_core_serial import *
import time

ports = {'hcc1': 'COM4'}
protocol_version = '1.0'
input_queues = {hcc: Queue() for hcc in ports.keys()}
output_queues = {hcc: Queue() for hcc in ports.keys()}

class Hapticore:
    def __init__(self, ports, protocol_version="1.0"):
        self.ports = ports
        self.protocol_version = protocol_version
        self.stop_event = threading.Event()
        
        self.input_queues = {name: Queue() for name in ports}
        self.output_queues = {name: Queue() for name in ports}
        self.threads = []

        for name, port in ports.items():
            thread = threading.Thread(
                target=process_serial_data,
                args=(
                    port,
                    protocol_version,
                    self.stop_event,
                    self.input_queues[name],
                    self.output_queues[name],
                ),
                daemon=True,
            )
        self.threads.append(thread)
        thread.start()

    def read_angle(self, device="hcc1"):
        return get_register(
            'report_encoder_angle', 
            self.output_queues[device], 
            self.input_queues[device]
            )

    def read_multiturn(self, device="hcc1"):
        return get_register(
            'report_encoder_multi_turn_counter',
            self.output_queues[device],
            self.input_queues[device]
            )


    def stop(self):
        self.stop_event.set()
        for t in self.threads:
            t.join(timeout=1)

    def application_tick(self):
        current = self.read_angle()
        diff = current - init_angle
        multiturn = self.read_multiturn()
        # print(f"Current angle: {current: .2f}, Diff: {diff:.2f}")
        return current, diff, multiturn

haptics = Hapticore({"hcc1": "COM3"})#

# report_encoder_multi_turn_counter

start_time = time.time()
stop_event = threading.Event()
init_angle = haptics.read_angle()
i = 0
while True:
    cur_ang, cur_dif, multiturn = haptics.application_tick()
    print(cur_ang, cur_dif, multiturn)
    # if abs(cur_dif)>200:
    #     d = input("Threshold exceeded, press Enter to proceed.")
    #     init_angle = haptics.application_tick()[0]
    #     i += 1
    # if i == 3: break