import os
import random
import time
import numpy as np
import pandas as pd
import scipy.stats as st
from scipy.stats import norm
from tkinter import *
from PIL import ImageTk, Image
from tkvideo import tkvideo
from src.haptic_core_serial import *
import exp1_stimuli as stim

#### STIWA Hapticore settings and threading ####

ports = {'hcc1': 'COM3'}
protocol_version = '1.0'
stop_event = threading.Event()
input_queues = {hcc: Queue() for hcc in ports.keys()}
output_queues = {hcc: Queue() for hcc in ports.keys()}
threads: list[threading.Thread] = []
for hcc in ports.keys():
	threads.append(
		threading.Thread(target=process_serial_data,
		args=(ports[hcc], protocol_version, stop_event, input_queues[hcc], output_queues[hcc])
        ))
for thread in threads:
	thread.start()
set_register('tick_angle_cw', 3, output_queues['hcc1'])

#################################################

class HelperFunctions:
    """GUI helper functions for opening additional windows."""

    def __init__(self, font="Arial", font_size=16):
        self.font = font
        self.font_size = font_size

    def open_text_window(self, parent, title, text, geometry):
        """Open a simple popup window containing text."""
        window = Toplevel(parent)
        window.title(title)
        window.geometry(geometry)

        label = Label(window, text=text, font=(self.font, self.font_size))
        label.pack(padx=10, pady=10)

    def application_tick(self, init_angle):
    	cur_angle = get_register("report_encoder_angle", output_queues["hcc1"], input_queues["hcc1"])
    	diff_to_init = cur_angle - init_angle
    	print()
    	print(diff_to_init)
    	print()
    	return [cur_angle, diff_to_init]

    def stopThreads(self):
        stop_event.set()
        for thread in threads:
        	thread.join()

init_angle = get_register('report_encoder_angle', output_queues['hcc1'], input_queues['hcc1'])

class MainFunctions:
    """Main experiment controller (placeholder for expansion)."""

    def __init__(self, phase, stimuli):
        self.phase = phase
        self.stimuli = stimuli


# -------------------------------------------------------
# Main GUI
# -------------------------------------------------------

DEFAULT_FONT = ("Arial", 16)
helper = HelperFunctions(*DEFAULT_FONT)

root = Tk()
root.title("FFG-STIWA, Experiment 1.2")
root.geometry("400x400+50+150")

intro_message = Label(
    root,
    text="Please click on the instructions button\nand read the information carefully!",
    font=DEFAULT_FONT
)
intro_message.pack(pady=10)

def combi():
	helper.application_tick(init_angle)
	root.quit()

instruction_btn = Button(
    root,
    text="Instruction",
    font=DEFAULT_FONT,
    command=lambda: helper.open_text_window(
        parent=root,
        title="Instruction",
        text="...",
        geometry="600x400+500+50"
    )
)
instruction_btn.pack(pady=10)

practice_btn = Button(
    root,
    text="Start Practice",
    font=DEFAULT_FONT
)
practice_btn.pack(pady=10)

stopThreading_btn = Button(
	root,
	text="Stop Threading",
	font=DEFAULT_FONT,
	command=helper.stopThreads)
stopThreading_btn.pack(pady=10)

quit_btn = Button(
	root,
	text = "Close",
	font = DEFAULT_FONT,
	command = combi)
quit_btn.pack()

root.mainloop()
