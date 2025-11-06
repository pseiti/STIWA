import exp1_stimuli as stim
import os
from tkinter import *
from PIL import ImageTk, Image
from tkvideo import tkvideo
import random
import numpy as np
import pandas as pd
import time
import scipy.stats as st
from scipy.stats import norm

class helpr_functions:

	def __init__(self, font, fontSize):
		self.font = font
		self.fontSize = fontSize

	def open_txtWindow_fx(self, window, title, txt, dimensions):
		newWindow = Toplevel(window)
		newWindow.title(title)
		newWindow.geometry(dimensions)
		message = Label(newWindow, text = txt)
		message.config(font = (self.font, self.fontSize))
		message.pack()


class main_functions:

	def __init__(self,phase,stimuli):
		self.phase = phase
		self.stimuli = stimuli


H = helpr_functions(font = "Arial", fontSize = 16)
root = Tk()
root.title("FFG-STIWA, Experiment 1.2")
root.geometry("400x400+50+150")
intro_message = Label(root, text = """Please click on the instructions button
and read the information carefully!""")
intro_message.config(font=("Arial",16))
intro_message.pack(pady=10)
instruction_btn = Button(root, text = "Instructions")
instruction_btn.config(command = lambda: H.open_txtWindow_fx(
	window = root, title = "Instruction", txt = "...", 
	dimensions = "600x400+500+50"))
instruction_btn.pack()

root.mainloop()