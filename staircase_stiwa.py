import numpy as np
import pandas as pd
from tkinter import *
import random
import module_waveforms as wf
from src.haptic_core_serial import *
import os

ports = {'hcc1': 'COM3'}
protocol_version = '1.0'
stop_event = threading.Event()
input_queues = {hcc: Queue() for hcc in ports.keys()}
output_queues = {hcc: Queue() for hcc in ports.keys()}
threads: list[threading.Thread] = []


## helper functions

class helprs():

	def text_fx(self, field_name, txt, configureState, state):
		field_name["text"] = txt
		field_name.pack()
		if configureState:
			field_name.configure(state = state)

	# def forget(self, objects):
	# 	for x in objects:
	# 		x.pack_forget()

	# def remember(self, objects):
	# 	for x in objects:
	# 		x.pack()

	def stopThreads(self):
		stop_event.set()
		for thread in threads:
			thread.join()

class trialFunctions:

	def __init__(self):
		self.H = helprs()

	def destroyWidgets_nextTrial(self):
		for widgets in frame.winfo_children():
			widgets.destroy()
		self.trial_fx(firstCall=False)

	def change_ang(self, cur_back_ang, button_value):
		LoG = globals()
		cur_back_ang += button_value
		if cur_back_ang > 20:
			cur_back_ang = 20
		if cur_back_ang < 1:
			cur_back_ang = 1
		set_register('ticke_angle_ccw', cur_back_ang, output_queues['hcc1'])
		cur_compStim["cur_back_ang"] = cur_back_ang
	
	def storeChange_fx(self, clicked_direction):
		LoG = globals()
		cur_compStim = LoG["cur_compStim"]
		rev = cur_compStim.get("rev")
		if cur_compStim.get("trial") == 1:
			LoG["up"]=True if clicked_direction=="up" else False
		if cur_compStim.get("trial") > 1:
			if LoG["up"] == False:
				if clicked_direction=="up":
					rev += 1
					LoG["up"]=True 	
			elif LoG["up"] == True:
				if clicked_direction == "down":
					rev += 1
					LoG["up"]=False
		cur_compStim["rev"] = rev
		LoG["cur_compStim"] = cur_compStim
		data.loc[len(data)] = [pcode, LoG["practice"], cur_compStim.get("A_or_B"),cur_compStim.get("cur_back_ang"),
			cur_compStim.get("trial"), LoG["cur_compStim"].get("rev"), LoG["cur_compStim"].get("run"),
			(LoG["indx_curStim"]+1)*LoG["cur_compStim"].get("run")]
		self.destroyWidgets_nextTrial()

	def button_fx(self, cur_back_ang):
		global b1, b2, b3, b4, b5, b6, bB
		LoG = globals()
		# b1 = Button(frame, font=("Arial",15), text="<<<",
		# 	command = lambda:[self.change_ang(cur_back_ang = cur_back_ang, button_value = -5),
		# 	self.storeChange_fx("down")])
		# b1.place(relx = 0.3, rely = .5, anchor = CENTER)
		# b2 = Button(frame, font=("Arial",15), text="<<",
		# 	command = lambda:[self.change_ang(cur_back_ang = cur_back_ang, button_value = -3),
		# 	self.storeChange_fx("down")])
		# b2.place(relx = 0.35, rely = .5, anchor = CENTER)
		b3 = Button(frame, font=("Arial",15), text="<",
			command = lambda:[self.change_ang(cur_back_ang = cur_back_ang, button_value = -1),
			self.storeChange_fx("down")])
		b3.place(relx = 0.45, rely = .4, anchor = CENTER)
		b4 = Button(frame, font=("Arial",15), text=">",
			command = lambda:[self.change_ang(cur_back_ang = cur_back_ang, button_value = 1),
			self.storeChange_fx("up")])
		b4.place(relx = 0.55, rely = .4, anchor = CENTER)
		# b5 = Button(frame, font=("Arial",15), text=">>", 
		# 	command = lambda:[self.change_ang(cur_back_ang = cur_back_ang, button_value = 3),
		# 	self.storeChange_fx("up")])
		# b5.place(relx = 0.65, rely = .5, anchor = CENTER)
		# b6 = Button(frame, font=("Arial",15), text=">>>", 
		# 	command = lambda:[self.change_ang(cur_back_ang = cur_back_ang, button_value = 5),
		# 	self.storeChange_fx("up")])
		# b6.place(relx = 0.7, rely = .5, anchor = CENTER)

	def get_keypress_intro(self):
		win.bind("<Key>", self.compute_key_pressed_intro)
	
	def compute_key_pressed_intro(self, event):
		response = event.char
		
		if response=="i":
			win2 = Tk()
			win2.title("Instruction")
			win2.geometry("1000x500+0+0")
			frame2 = Frame(win2)
			frame2.pack(padx=20, pady=20)
			scrollbar = Scrollbar(frame2)
			scrollbar.pack(side=RIGHT, fill=Y)
			Instruction = Text(frame2, font=("f", 20))
			Instruction.insert(END, "...")
			scrollbar.config(command=Instruction.yview)
			Instruction.pack()	

		if response=='p':
			for widgets in frame.winfo_children():
				widgets.destroy()
			self.trial_fx(firstCall = False)

		elif response=='t':
			LoG = globals()
			LoG["practice"]=False
			for widgets in frame.winfo_children():
				widgets.destroy()
			list_compStims = self.stimfx(practice=False, jitter=.15)
			LoG['list_compStims'] = list_compStims
			LoG['cur_compStim'] = list_compStims[0]
			LoG['indx_curStim'] = 0
			self.trial_fx(firstCall = False)

	def application_tick(self, init_angle):
		cur_angle = get_register('report_encoder_angle', output_queues['hcc1'], input_queues['hcc1'])
		diff_to_init = cur_angle - init_angle
		return [cur_angle, diff_to_init]

	def wheel_tracking_fx(self):
		LoG = globals()
		init_angle = get_register('report_encoder_angle', output_queues['hcc1'], input_queues['hcc1'])
		LoG["init_angle"] = init_angle
		while True:
			appl_tick_out = self.application_tick(LoG["init_angle"])
			cur_diff_to_init = appl_tick_out[1]
			if np.absolute(cur_diff_to_init) > 5:
				if cur_diff_to_init < 0:
					if LoG["forward"]==False:
						LoG["fwdBwd_revs"] += 1
					LoG["forward"] = True
				else:
					if LoG["forward"]==True:
						LoG["fwdBwd_revs"] += 1
					LoG["forward"] = False
				init_angle = get_register('report_encoder_angle', output_queues['hcc1'], input_queues['hcc1'])
				LoG["init_angle"] = init_angle
			print()
			print("Number reversals: ", LoG["fwdBwd_revs"])
			if LoG["fwdBwd_revs"] > rev_max:
				LoG["forward"] = np.nan
				LoG["fwdBwd_revs"] = 0
				break
		cur_back_ang = cur_compStim.get("cur_back_ang")
		self.button_fx(cur_back_ang = cur_back_ang)

	def trial_fx(self, firstCall):
		LoG = globals()
		if firstCall==True:
			LoG["practice"] = True
			LoG["intro"] = True
			LoG["indx_curStim"] = 0
			LoG["list_compStims"] = self.stimfx(practice = True, jitter = .15)
			LoG["cur_compStim"] = LoG["list_compStims"][0]
			set_register('ticke_angle_ccw', LoG["cur_compStim"].get("cur_back_ang"), output_queues['hcc1'])
			LoG["up"] = np.nan
			LoG["forward"] = np.nan
			LoG["fwdBwd_revs"] = 0
		if LoG["intro"]==True:
			global Text1, Text2
			LoG["intro"] = False
			for widgets in frame.winfo_children():
				widgets.destroy()
			Text1 = Label(frame, font=("Arial", 20))
			Text2 = Label(frame, font=("Arial", 20))
			H.text_fx(Text1, "How to proceed", False, None)
			H.text_fx(Text2, """

 1. Press I to open and read the instructions

 2. Press P to start the practice session.

 3. Press T to start the test session.""", False, None)
			self.get_keypress_intro()
		else:
			global Reversal_Label, Run_Label, FwdBwdInstrctn_Label
			LoG = globals()
			stimChange = False
			continue_procedure = True
			frame.pack(side="top", expand=True, fill="both")
			Run_Label = Label(frame, font = ("Arial bold", 20))
			Reversal_Label = Label(frame, font = ("Arial", 20))
			FwdBwdInstrctn_Label = Label(frame, font = ("Arial bold", 20))

			if LoG["cur_compStim"].get("rev") > rev_max: # Next run
				stimChange = True
				runNr = LoG["cur_compStim"].get("run")
				runNr += 1
				LoG["cur_compStim"]["run"] = runNr
				LoG["indx_curStim"] += 1
				if LoG["indx_curStim"] < len(LoG["list_compStims"])*nRunsPerCompStim:
					LoG["cur_compStim"] = LoG["list_compStims"][LoG["indx_curStim"]]
					set_register('ticke_angle_ccw', LoG["cur_compStim"].get("cur_back_ang"), output_queues['hcc1'])
				else:
					continue_procedure = False
					H.text_fx(field_name = Run_Label, txt = """
Showend! """, configureState = True, state = "normal")
					print(LoG["data"])
					data.to_csv(logfile_name)
					H.stopThreads()
					closeBtn = Button(win, text = "Close", command = win.destroy)
					closeBtn.place(relx=.5, rely=.8)

			if continue_procedure:
				if stimChange:
					pass
				trialNr = LoG["cur_compStim"].get("trial")
				trialNr += 1
				LoG["cur_compStim"]["trial"] = trialNr
				H.text_fx(field_name = Run_Label, txt = """
# Runs = """ + str((LoG["indx_curStim"]+1))*LoG["cur_compStim"].get("run"), configureState = True, state = "normal")
				H.text_fx(field_name = Reversal_Label, txt = """
# Reversals = """ + str(LoG["cur_compStim"].get("rev")), configureState = True, state = "normal")
				H.text_fx(field_name = FwdBwdInstrctn_Label, txt = """
Continue forward-backward scrolling... """, configureState = True, state = "normal")
				frame.after(10, self.wheel_tracking_fx)


	def stimfx(self, practice, jitter):

	        if practice == True:
	                list_compStims = [
	                {"A_or_B": "A", "cur_back_ang":1, "trial":0, "rev":0, "run": 1},
	                {"A_or_B": "B", "cur_back_ang":15, "trial":0, "rev":0, "run": 1}
	                ]
	                random.shuffle(list_compStims)
	        else:
	                list_compStims = [
	                {"A_or_B": "A", "cur_back_ang":1, "trial":0, "rev":0, "run": 1},
	                {"A_or_B": "B", "cur_back_ang":15, "trial":0, "rev":0, "run": 1}
	                ]
	                random.shuffle(list_compStims)
	        # jitter
	        for x in range(len(list_compStims)):
	                stim_x = list_compStims[x]
	                ang_stim_x = stim_x.get("cur_back_ang")
	                minmax = ang_stim_x*jitter
	                jitter_x = np.random.uniform(low=-minmax, high=minmax, size=None)
	                ang_jittered = round((ang_stim_x+jitter_x),2)
	                list_compStims[x]["cur_back_ang"] = ang_jittered

	        return list_compStims


for hcc in ports.keys():
	threads.append(
		threading.Thread(target=process_serial_data,
		args=(ports[hcc], protocol_version, stop_event, input_queues[hcc], output_queues[hcc])
        ))
for thread in threads:
	thread.start()

# cur_back_ang = 15
set_register('tick_angle_cw', 10, output_queues['hcc1'])

pcodefile = open("p_code.txt","r")
pcode = pcodefile.read()
pcodefile.close()
logfile_path = os.getcwd() + "/"
logfile_name = "{}_{}.csv".format(logfile_path, pcode)

H = helprs()

win = Tk()
win.title("Staircase")
win.attributes('-fullscreen', True)
#win.geometry("1000x500+0+0")
closeBtn = Button(win, text = "Exit", command = win.destroy)
# closeBtn.pack(side=BOTTOM, pady = 25)
frame = Frame(win)
frame.pack()
# The test run concluded when the change in the amplitude of the
# comparison stimulus reversed a total of 12 times. We then computed the geometric
# mean of the comparison stimulus amplitudes on the last ten trials of the run. 

columns = ['pcode','practice','A_or_B','cur_back_ang','trial','rev','run','track']
data = pd.DataFrame(columns = columns)

rev_max = 2
nRunsPerCompStim = 1
TF = trialFunctions()
nPractice = len(TF.stimfx(practice = True, jitter = .0)) # jitter = .15
nTest = len(TF.stimfx(practice = False, jitter = .0)) # jitter = .15
TF.trial_fx(firstCall = True)
win.mainloop()


