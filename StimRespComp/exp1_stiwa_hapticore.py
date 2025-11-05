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

class main_functions:

	def __init__(self,phase,stimuli):
		self.phase = phase
		self.stimuli = stimuli

root = Tk()
root.title("FFG-STIWA, Experiment 1.2")
root.geometry("400x500+50+250")
intro_message = Label(root, text = """Please click on the instructions button
and read the information carefully!""")
intro_message.config(font=("Arial",16))
intro_message.pack()

root.mainloop()