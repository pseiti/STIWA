import exp1_stimuli as stim
import os
from tkinter import *
from PIL import ImageTk, Image
from tkVideoPlayer import TkinterVideo
import random
import numpy as np
import pandas as pd
import time
import scipy.stats as st
from scipy.stats import norm

class helper_functions:
	def close_window_fx(self, window):
		window.destroy()

	def activate_fx(self, btn):
		btn["state"] = "active"

	def toggle_fx(self, o, window):
		if o["state"]=="active" or o["state"]=="normal":
			o["state"] = "disabled"
		else:
			o["state"] = "active"
			window.destroy()
	
	def changeTxtColor_fx(self, o):
		o.config(fg = "black")

	def open_new_txtWindow_fx(self, window, title, txt1, txt2, txt3, dimensions):
		newWindow = Toplevel(window)
		newWindow.title(title)
		newWindow.configure(bg = "white")
		newWindow.geometry(dimensions)
		message = Label(newWindow, text = txt1)
		message.config(bg = "white", fg = "black")
		message.config(font = ("Arial", 16))
		message.pack()
		img_apotheke = Label(newWindow, image = logo_apotheke)
		img_apotheke.pack()
		message2 = Label(newWindow, text = txt2)
		message2.config(bg = "white", fg = "black")
		message2.config(font = ("Arial", 16))
		message2.pack()
		message3 = Label(newWindow, text = txt3)
		message3.config(bg = "white", fg = "black")
		message3.config(font = ("Arial", 16))
		message3.pack()
		if title=="Instructions":
			self.toggle_fx(o = instruction_btn, window = newWindow)
			consent_btn = Button(newWindow, text = "OK")
			consent_btn.config(highlightbackground = "white")
			consent_btn.config(command = lambda: [self.toggle_fx(o = instruction_btn, window = newWindow),
				self.activate_fx(btn = startPractice_btn)])
			consent_btn.pack()
			newWindow.protocol("WM_DELETE_WINDOW", lambda: self.toggle_fx(o = instruction_btn, window = newWindow))

	def evaluatePerformance_fx(self, df):
		nHits = len(df[df['respCat_sdt']=='Hit'])
		nMiss = len(df[df['respCat_sdt']=='Miss'])
		nCR = len(df[df['respCat_sdt']=='CR'])
		nFA = len(df[df['respCat_sdt']=='FA'])
		if np.sum([nHits, nMiss, nCR, nFA])==0:
			percentError = 0
		else:
			percentError = np.divide(np.sum([nMiss, nFA]),np.sum([nHits, nMiss, nCR, nFA]))*100
		if np.sum([nHits,nMiss])==0:
			hitRate = 1/np.sqrt(400)
		else:
			hitRate = np.divide(nHits,np.sum([nHits,nMiss]))
		if hitRate==1:
			hitRate = 1-1/np.sqrt(400)
		if hitRate==0:
			hitRate = 1/np.sqrt(400)
		if np.sum([nCR,nFA])==0:
			faRate = 1-1/np.sqrt(400)
		else:
			faRate = np.divide(nFA,np.sum([nCR,nFA]))
		if faRate==1:
			faRate = 1-1/np.sqrt(400)
		if faRate==0:
			faRate = 1/np.sqrt(400)
		dPrime = st.norm.ppf(hitRate) - st.norm.ppf(faRate)
		return [percentError, hitRate, faRate, dPrime]


class trial_functions:

	def __init__(self, phase, stimuli):
		self.phase = phase
		self.stimuli = stimuli

	# def countdown_fx(self, count):
	# 	global Label_countdown, start_time
	# 	if count > 0:
	# 		Label_countdown['text'] = count
	# 		sessionWindow.after(1000, self.countdown_fx, count-1)
	# 	else:
	# 		# Label_countdown['text'] = stimClass
	# 		Label_countdown.config(fg = "white")
	# 		sessionWindow.after(1000, vid_player.play)
	# 		start_time = time.time()

	# def startButton_fx(self,tvar):
	# 	global start_time, scrolling_started, mouseWheelLogging_muted, count
	# 	tvar.set(1)
	# 	start_time = time.time()
	# 	mouseWheelLogging_muted = False
	# 	scrolling_started = False
	# 	count = 0

	def playVideo(self):
		sessionWindow.bind("<MouseWheel>", self.mouse_wheel)
		vid_player.bind("<<Ended>>", self.destroyVideo)
		vid_player.pack(expand=True, fill="both")
		vid_player.load(stim_movie)
		vid_player.play()

	def destroyVideo(self, event):
		global Label_response
		vid_player.destroy()
		if scrolling_completed==False:
			Label_response = Label(sessionWindow, text = "?")
			Label_response.config(font = ("Arial", 28), bg = "white", fg = "white")
			Label_response.place(relx = .5, rely = .5, anchor = CENTER)
			sessionWindow.after(250, lambda: H.changeTxtColor_fx(o = Label_response))

	def open_sessionWindow_fx(self, window, dimensions):
		global sessionWindow, mouseWheelLogging_muted, t
		mouseWheelLogging_muted = True
		sessionWindow = Toplevel(window)
		sessionWindow.config(cursor = "none")
		sessionWindow.title("Experiment 1")
		sessionWindow.geometry(dimensions)
		sessionWindow.configure(bg = "white")
		sessionWindow["bg"] = "white"
		if self.phase=="practice":
			H.toggle_fx(o = startPractice_btn, window = sessionWindow)
		else:
			H.toggle_fx(o = startTest_btn, window = sessionWindow)
		t = 0
		self.present_stimulus()
		if self.phase=="practice":
			sessionWindow.protocol("WM_DELETE_WINDOW", 
				lambda: H.toggle_fx(o = startPractice_btn, window = sessionWindow))

	def present_stimulus(self): 
		global t, stimClass, Label_feedback, Label_continue 
		global zoomIn_or_zoomOut, Absent_or_present, Slow_or_fast, stim_movie
		if t > 1:
			for widget in sessionWindow.winfo_children():
		    					widget.destroy()
		stim = self.stimuli[t]
		t += 1
		stim_movie = stim.get("clip")
		stimClass = stim.get("condi")
		zoomIn_or_zoomOut = stimClass[0]
		Absent_or_present = stimClass[1]
		Slow_or_fast = stimClass[2]
		Label_continue = Label(sessionWindow)
		Label_continue.config(font = ("Arial", 18))
		Label_continue.config(bg = "white", fg = "black")
		Label_continue["text"] = "Press the space bar to start the clip."
		Label_continue.place(relx = .5, rely = .5, anchor = CENTER)
		Label_feedback = Label(sessionWindow)
		Label_feedback.config(font = ("Arial", 18))
		Label_feedback.config(bg = "white", fg = "black")
		sessionWindow.bind("<space>", self.keypress_fx)
	
	def keypress_fx(self, event):
		global start_time, scrolling_started, scrolling_completed, count, vid_player, mouseWheelLogging_muted
		Label_continue.destroy()
		sessionWindow.unbind("<space>")
		Label_feedback.place(relx = .5, rely = .5, anchor = CENTER)
		start_time = time.time()
		mouseWheelLogging_muted = False
		scrolling_started = False
		scrolling_completed = False
		count = 0
		Label_fixationCross = Label(sessionWindow, text = "+", bg = "white", fg = "black")
		Label_fixationCross.config(font = ("Arial", 50))
		Label_fixationCross.place(relx=.5, rely=.5, anchor = CENTER)
		sessionWindow.after(500, Label_fixationCross.destroy)
		vid_player = TkinterVideo(scaled=True, master=sessionWindow)
		sessionWindow.after(501, self.playVideo)

	def mouse_wheel(self, event):
	    global count, mouseWheelLogging_muted, scrolling_started, scrolling_completed, start_time, RT, start_time_wheel, tick_RTs
	    global Label_response, Label_feedback, block_now, nPracticeCycles, t
	    percentError, hitRate, faRate, dPrime = np.array([np.nan,np.nan,np.nan,np.nan])
	    Label_response.destroy()
	    if not scrolling_started:
	    	RT = time.time()-start_time
	    	scrolling_started = True
	    	start_time_wheel = time.time()
	    	tick_RTs = []
	    	count = 0
	    if not mouseWheelLogging_muted:
	    	towards_or_away = np.nan
	    	if event.delta <=-1:
	    		count -= 1
	    		towards_or_away = "towards"
	    		tick_RTs.append(time.time()-start_time_wheel)
	    	elif event.delta >= 1:
	    		count += 1 # Scrolling away from screen
		    	towards_or_away = "away"
		    	tick_RTs.append(time.time()-start_time_wheel)
	    	if count == 5 or count == -5:
	    		scrolling_completed = True
	    		RT_Wheel = time.time()-start_time_wheel
	    		feedback = np.nan
	    		mouseWheelLogging_muted = True
	    		sessionWindow.unbind("<MouseWheel>")
		    	respCat_sdt = np.nan
		    	if compatibility=="C" and towards_or_away=="towards" and Absent_or_present=="P":
			    	feedback = "Hit. The target was present."
			    	respCat_sdt = "Hit"
			    	Label_feedback.config(fg = "green")	
		    	elif compatibility=="C" and towards_or_away=="away" and Absent_or_present=="P":
			    	feedback = """Miss. The target was present.
Please wait..."""
			    	respCat_sdt = "Miss"
			    	Label_feedback.config(fg = "red")	
		    	elif compatibility=="C" and towards_or_away=="towards" and Absent_or_present=="A":
			    	feedback = """False alarm. The target was not present.
Please wait..."""
			    	respCat_sdt = "FA"
			    	Label_feedback.config(fg = "red")
		    	elif compatibility=="C" and towards_or_away=="away" and Absent_or_present=="A":
			    	feedback = "Correct rejection. The target was not present."
			    	respCat_sdt = "CR"
			    	Label_feedback.config(fg = "green")
		    	elif compatibility=="I" and towards_or_away=="towards" and Absent_or_present=="P":
			    	feedback = """Miss. The target was present.
Please wait..."""
			    	respCat_sdt = "Miss"
			    	Label_feedback.config(fg = "red")	
		    	elif compatibility=="I" and towards_or_away=="away" and Absent_or_present=="P":
			    	feedback = "Hit. The target was present."
			    	respCat_sdt = "Hit"
			    	Label_feedback.config(fg = "green")
		    	elif compatibility=="I" and towards_or_away=="towards" and Absent_or_present=="A":
			    	feedback = """Correct rejection. The target was not present."""
			    	respCat_sdt = "CR"
			    	Label_feedback.config(fg = "green")
		    	elif compatibility=="I" and towards_or_away=="away" and Absent_or_present=="A":
			    	feedback = """False alarm. The target was not present.
Please wait..."""
			    	respCat_sdt = "FA"
			    	Label_feedback.config(fg = "red")
		    	if respCat_sdt in ["FA", "Miss"]:
		    		Label_feedback['text'] = feedback
		    		feedback_presTime = 2000
		    	else:
		    		feedback_presTime = 250
		    	
		    	if self.phase == "test":
		    		test_res_df = res_df[res_df["Phase"]=="test"]
		    		if np.isin([t],[newBlock_trials]):
		    			fileName = code + "_results.csv"
		    			res_df.to_csv(fileName)
		    			block_now += 1
		    			percentError, hitRate, faRate, dPrime = H.evaluatePerformance_fx(df = test_res_df)
		    			Label_feedback.config(fg = "white")
		    			Label_pause = Label(sessionWindow, text = """Pause – please tell the experimenter.
Your current percent error is: """)
		    			Label_pause.config(bg = "white", fg = "black", font = ("Arial", 18))
		    			Label_pause.place(relx=.5, rely=.5, anchor = CENTER)
		    			Label_percent = Label(sessionWindow, text = str(np.around(percentError)))
		    			Label_percent.config(font=("Arial", 18), bg="white", fg="black")
		    			Label_percent.place(relx=.5, rely=.6, anchor = CENTER)
		    			Label_response.destroy()	    			
		    			input("Press Enter to continue testing.")
		    			Label_pause.destroy()
		    			Label_percent.destroy()
		    		if t == len(stim.stimuli_test):
		    			percentError, hitRate, faRate, dPrime = H.evaluatePerformance_fx(df = test_res_df)
		    			Label_feedback.config(fg = "white")
		    			Label_pause = Label(sessionWindow, text = """Test completed – Thank you very much!
Your percent error is: """)
		    			Label_pause.config(bg = "white", fg = "black", font = ("Arial", 18))
		    			Label_pause.place(relx=.5, rely=.5, anchor = CENTER)
		    			Label_percent = Label(sessionWindow, text = str(np.around(percentError)))
		    			Label_percent.config(font=("Arial", 18), bg="white", fg="black")
		    			Label_percent.place(relx=.5, rely=.6, anchor = CENTER)
		    			Label_response.destroy()    			
		    			input("Press Enter to save the data!")
		    			sessionWindow.destroy()
		    	elif self.phase == "practice":
		    		percentError, nHits, nMiss, nCR, nFA = [0, 0, 0, 0, 0]
		    		if t == len(stim.stimuli_practice):
		    			practice_res_df = res_df[res_df["PracticeCycle"]==nPracticeCycles]
		    			percentError, hitRate, faRate, dPrime = H.evaluatePerformance_fx(df = practice_res_df)
		    			print("d' = ", np.around(dPrime,2))
		    			if dPrime > 2:
		    				H.activate_fx(btn = startTest_btn)
		    				Label_feedback.config(fg = "white")
		    				Label_pause = Label(sessionWindow, text = """Pause – please tell the experimenter.
Your percent error is: """)
		    				Label_pause.config(bg = "white", fg = "black", font = ("Arial", 18))
		    				Label_pause.place(relx=.5, rely=.5, anchor = CENTER)
		    				Label_percent = Label(sessionWindow, text = str(np.around(percentError)))
		    				Label_percent.config(font=("Arial", 18), bg="white", fg="black")
		    				Label_percent.place(relx=.5, rely=.6, anchor = CENTER)
		    				Label_response.destroy()    			
		    				input("Press Enter to continue to the test phase.")
		    				sessionWindow.destroy()
		    			else:
		    				nPracticeCycles += 1
		    				H.activate_fx(btn = startPractice_btn)
		    				Label_feedback.config(fg = "white")
		    				Label_pause = Label(sessionWindow, text = """Pause – please tell the experimenter.
Your current percent error is: """)
		    				Label_pause.config(bg = "white", fg = "black", font = ("Arial", 18))
		    				Label_pause.place(relx=.5, rely=.5, anchor = CENTER)
		    				Label_percent = Label(sessionWindow, text = str(np.around(percentError)))
		    				Label_percent.config(font=("Arial", 18), bg="white", fg="black")
		    				Label_percent.place(relx=.5, rely=.6, anchor = CENTER)
		    				Label_response.destroy()  			
		    				input("Press Enter to continue practicing.")
		    				# Label_pause.destroy()
		    				# Label_percent.destroy()
		    				sessionWindow.destroy()
		    				# for widget in sessionWindow.winfo_children():
		    				# 	widget.destroy()

		    	Code = code
		    	Phase = self.phase
		    	Block = block_now
		    	TrialNr = t
		    	IV1_presence = Absent_or_present
		    	IV2_zooming = zoomIn_or_zoomOut
		    	IV3_rateOfChange = Slow_or_fast
		    	IV4_compatibility = compatibility
		    	DV1_scrolling = towards_or_away
		    	DV2_RT = RT
		    	DV3_TickRTs = str(tick_RTs)
		    	respCat_sdt = respCat_sdt
		    	PracticeCycle = nPracticeCycles
		    	res_df.loc[len(res_df.index)] = [Code, Phase, PracticeCycle, Block, TrialNr, IV1_presence, 
		    	IV2_zooming, IV3_rateOfChange, IV4_compatibility, DV1_scrolling, DV2_RT, DV3_TickRTs,
		    	respCat_sdt, percentError, hitRate, faRate, dPrime]

		    	if self.phase == "practice":
		    		if t == len(stim.stimuli_practice):
		    			fileName = code + "_" + partOfSession + "_results.csv"
		    			res_df.to_csv(fileName)
		    	if self.phase == "test":
		    		if t == len(stim.stimuli_test):
		    			fileName = code + "_" + partOfSession + "_results.csv"
		    			res_df.to_csv(fileName)

		    	if t<len(stim.stimuli_test):
		    		sessionWindow.after(feedback_presTime, self.present_stimulus)


partOfSession = input("Participation first time (1) or second time (2)? ")
nPracticeCycles = 0
if partOfSession=="1":
	letters = ["A","B","C","D","E","F","G","H","I","J","K",
	"L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
	code_letters = list(np.random.choice(letters,2))
	code_integers = list(np.random.choice(10,6))
	code_elements = code_letters + code_integers
	for x in range(len(code_elements)-1):
		if x == 0:
			code = code_elements[x]
		else:
			code = code + str(code_elements[x])
elif partOfSession=="2":
	code = input("Insert the code: ")

print()
print(code)
print()
compatibility = input("Type C or I (for compatible or incompatible): ")
print()

main_conditions = [
"IAFC", "IAFI", "IASC", "IASI", "IPFC", "IPFI", "IPSC", "IPSI",
"OAFC", "OAFI", "OASC", "OASI", "OPFC", "OPFI", "OPSC","OPSI"]
# First letter: I or O = Zoom In or zoom Out,
# Second letter: A or P = Absent or Present, Third letter: F or S = Fast or Slow,
# Fourth letter: C or I = Compatible or incompatible,


data_columns = ["Code", "Phase", "PracticeCycle","Block", "TrialNr", 
"IV1_presence", "IV2_zooming", "IV3_rateOfChange", "IV4_scrolling", 
"DV1_scrolling", "DV2_RT", "DV3_TickRTs","respCat_sdt", "percentError", "hitRate", "faRate", "dPrime"]
block_now = 1
# newBlock_trials = np.array([81,161,241,321])
newBlock_trials = np.array([201])
res_df = pd.DataFrame(columns=data_columns)
H = helper_functions()
T_practice = trial_functions(phase = "practice", stimuli = stim.stimuli_practice)
T_test = trial_functions(phase = "test", stimuli = stim.stimuli_test)
root = Tk()
root['padx'] = 5
root['pady'] = 5
root.title("FFG-STIWA, Experiment 1")
root.configure(background = "white")
root["bg"] = "white"
root.minsize(200, 200)
root.maxsize(500, 500)
root.geometry("400x250+50+250")
intro_message = Label(root, text = """Please click on the instructions button
and read the information carefully!""")
intro_message.config(bg = "white", fg = "black")
intro_message.config(font = ("Arial", 16))
intro_message.pack(pady = 10)
# exit_btn = Button(root, text = "Exit")
# exit_btn.config(highlightbackground = "white")
# exit_btn.config(command = lambda: H.close_window_fx(window = root))
# exit_btn.pack()
instruction_btn = Button(root, text = "Instructions")
instruction_btn.config(highlightbackground="white")
instr_Procedure_and_Task_1 = """
It follows a sequence of """ + str(len(stim.stimuli_test)) + """ trials, which are short video clips.
Each clip shows a moving map that is simultaneously zoomed in or out.
The clips differ in whether or not the so-called target object
-- a pharmacy symbol, as displayed below --
appears or does not appear at some point during zooming.
"""
# Below are four example clips (please watch each of them), which differ 
# in whether or not the so-called target object - a pharmacy symbol, 
# as displayed below - appears or not at some point during zooming.
logo_apotheke = Image.open("Apotheke_Logo.png")
logo_apotheke = logo_apotheke.resize((50, 50))
logo_apotheke = ImageTk.PhotoImage(logo_apotheke)
if compatibility=="C":
	instr_Procedure_and_Task_2 = """
Your task is to indicate the presence or absence of the 
target by scrolling the mouse wheel forward (towards the 
screen) or backward (away from the screen)."""
elif compatibility=="I":
	instr_Procedure_and_Task_2 = """
Your task is to indicate the presence or absence of the 
target by scrolling the mouse wheel backward (away from 
the screen) or forward (towards the screen)."""
instr_Procedure_and_Task_3="""
Before the actual test phase with its """ + str(len(stim.stimuli_test)) + """ trials starts, 
you go through a brief, self-paced sequence of practice trials, which is
completed as soon as your accuracy level certifies you a 
sufficiently accurate response behavior.

Please consider, the level of accuracy is determined
by comparing your hits (trials, where the target is present 
and you 'hit' the right mouse wheel direction) against your 
false alarms (trials, where the target is absent but you 
falsely indicate its presence). 

Try to be as fast and accurate as you can!

	"""

instruction_btn.config(command = lambda: H.open_new_txtWindow_fx(window = root, 
	title = "Instructions", txt1 = instr_Procedure_and_Task_1, txt2 = instr_Procedure_and_Task_2,
	txt3 = instr_Procedure_and_Task_3,
	 dimensions = "600x700+600+250"))
instruction_btn.pack(pady = 10)

startPractice_btn = Button(root, text = "Start Practice")
startPractice_btn.config(command = lambda: T_practice.open_sessionWindow_fx(window = root, dimensions = "600x500+600+250"))
startPractice_btn["state"] = "disabled"
startPractice_btn.config(highlightbackground = "white")
startPractice_btn.pack(pady = 10)

startTest_btn = Button(root, text = "Start Test")
startTest_btn.config(command = lambda: T_test.open_sessionWindow_fx(window = root, dimensions = "600x500+600+250"))
startTest_btn["state"] = "disabled"
startTest_btn.config(highlightbackground = "white")
startTest_btn.pack(pady = 10)

root.mainloop()




