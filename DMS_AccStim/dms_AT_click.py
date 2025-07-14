import module_waveforms as wf
import sounddevice as sd
import conditions as cx
import pandas as pd
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk, Image
import random
import numpy as np
import time
import os
import matplotlib.pyplot as plt

class helprs:

	def jitterFx(self, cur_amp):
		minmax = cur_amp*jitter
		jitter_x = np.random.uniform(low=-minmax,high=minmax,size=None)
		amp_jittered = round((cur_amp+jitter_x),2)
		return amp_jittered

	def stimfx(self, practice, questionType):
	        if practice == True:
	        	if questionType == "eq":
	        		stim_dict = cx.conditions_eq_pract
	        		random.shuffle(stim_dict)
	        	else:
	        		stim_dict = cx.conditions_uneq_pract
	        		random.shuffle(stim_dict)
	        else:
	        	if questionType == "uneq":
	        		stim_dict = cx.conditions_uneq
	        		random.shuffle(stim_dict)
	        	else:
	        		stim_dict = cx.conditions_eq
	        		random.shuffle(stim_dict)
	        for x in range(len(stim_dict)):
	                stim_x = stim_dict[x]
	                amp_T1 = self.jitterFx(stim_x.get("T1_amp"))
	                amp_T2 = self.jitterFx(stim_x.get("T2_amp"))
	                amp_P = self.jitterFx(stim_x.get("P_amp"))
	                amp_update = {"T1_amp":amp_T1,"T2_amp":amp_T2,"P_amp":amp_P}
	                stim_dict[x].update(amp_update)
	        return stim_dict

	def text_fx(self, field_name, txt, configureState, state):
		field_name['text'] = txt
		field_name.pack(fill=Y)
		if configureState:
			field_name.configure(state=state)
		
	def forget(self, objects):
		for x in objects:
			x.pack_forget()

	def remember(self, objects):
		for x in objects:
			x.pack()
			x.place()

	def tone_fx(self, vibHz, stereo, audioHz):
		if stereo:
			stereoData = np.column_stack([vibHz, audioHz])
			sd.play(stereoData,44100)
		else:
			audioHz = np.zeros(len(vibHz))
			stereoData = np.column_stack([vibHz, audioHz])
			sd.play(stereoData, 44100)
		sd.wait()

	def toggle_locked(self):
		LoG = globals()
		locked = LoG["locked"]
		locked=True if locked==False else False
		LoG["locked"] = locked

	def getTime_0(self):
		global ts_0
		ts_0 = time.time()

	def getTime_1(self):
		global rt
		LoG = globals()
		ts_1 = time.time()
		rt = ts_1-LoG["ts_0"]
		return rt


class trialFunctions:

	def __init__(self):
		self.H = helprs()

	def get_keypress_intro(self):
		win.bind("<Key>",self.compute_key_pressed_intro)

	def compute_key_pressed_intro(self, event):

		global list_trial_dicts
		LoG = globals()
		response = event.char
		
		if LoG["intro"]==True:

			if response=="i":
				win2 = Tk()
				win2.title("Instruction")
				win2.geometry("1600x800+0+0")
				frame2 = Frame(win2)
				frame2.pack(padx=20, pady=20)
				scrollbar = Scrollbar(frame2)
				scrollbar.pack(side=RIGHT, fill=Y)
				Instruction = Text(frame2, font=("f",20))
				Instruction.insert(END, instruction_practice_part1)
				Instruction.insert(END, instruction_practice_part2)
				Instruction.insert(END, instruction_practice_part3)
				scrollbar.config(command=Instruction.yview)
				Instruction.pack()
				zkg = Button(win2, text = "Ok", command = win2.destroy)
				zkg.place(relx=.5, rely=.95)

			elif response=="p":
				global ts_init, StimInfo, FaceLabel, FaceTxt
				LoG['ts_init'] = time.time()
				LoG['data'] = pd.DataFrame(columns=columnNames)
				LoG["intro_locked"] = True
				LoG["intro"] = False
				LoG["practice"] = True
				if AB_or_BA=="AB": 
					if block=="1":
						LoG["list_trial_dicts"] = list_trial_dicts_practice_eq
					else:
						LoG["list_trial_dicts"] = list_trial_dicts_practice_uneq
				else:
					if block=="1":
						LoG["list_trial_dicts"] = list_trial_dicts_practice_uneq
					else:
						LoG["list_trial_dicts"] = list_trial_dicts_practice_eq
				StimInfo = Label(frame, font=("Arial",25))
				FaceLabel = Label(frame, pady=50, borderwidth=50)
				FaceTxt = Label(frame, font=("Arial",18))
				self.H.forget([close_btn])
				self.H.forget([Text1, Text2])
				self.trial_fx(firstCall=False)

			elif response=="t":
				if LoG["test_locked"]==False:
					LoG["intro_locked"] = True
					LoG["intro"] = False
					LoG["practice"] = False
					if AB_or_BA=="AB":
						if block=="1":
							LoG["list_trial_dicts"] = list_trial_dicts_test_eq
						else:
							LoG["list_trial_dicts"] = list_trial_dicts_test_uneq
					else:
						if block=="1":
							LoG["list_trial_dicts"] = list_trial_dicts_test_uneq
						else:
							LoG["list_trial_dicts"] = list_trial_dicts_test_eq
					print(len(LoG["list_trial_dicts"]))
					self.H.forget([Text1,Text2])
					self.trial_fx(firstCall=False)
				else:
					messagebox.showinfo(parent=win,message="Practice session not completed.")

	def trial_fx(self, firstCall):

		LoG = globals()
		ts_cur = time.time()
# 		if (ts_cur-LoG["ts_init"])>duration_break:
# 			mb = messagebox.showinfo(parent=win, message="""
#  Time for a break?
#  Press the Enter key or click on the OK button, 
#    but only if you feel sufficiently focused: When you close the window, 
#    the pause ends immediately and the next trial begins.
# """)
# 			LoG["ts_init"] = time.time()
		if firstCall==True:
			LoG["trial"] = 0
			LoG["trials_to_feedback"] = 8
		if intro==True:
			global Text1, Text2
			Text1 = Label(frame, font=("Arial bold", 25))
			Text2 = Label(frame, font=("Arial", 25))
			self.H.text_fx(Text1,"How to proceed",False,None)
			self.H.text_fx(Text2, """

 1. Press I to open and read the instructions

 2. Press P to start the practice session.

 3. Press T to start the test session.""", False, None)
			self.get_keypress_intro()
		else:
			global Countr, StimInfo, cur_trial_dict
			Countr = Text(frame)
			StimInfo = Label(frame, font=("Arial bold",25))
			StimInfo.pack()
			cur_trial_dict = list_trial_dicts[(LoG["trial"]-1)]
			self.present_trialStims()

	def present_trialStims(self):
		
		LoG = globals()
		LoG["locked"] = True # to lock functions 'compute_key_pressed()' and 'present_compute_rating()'
		# nToQuit = 5 if LoG["practice"]==True else 10
		nToQuit = len(list_trial_dicts)
		print(LoG["trial"])
		if LoG["trial"]==nToQuit:
			LoG["intro"]=True
			self.thxPage()
			self.trial_fx(firstCall=True)
		else:
			F1 = wf.soundGene2(44100,1,cur_trial_dict.get("T1_hz"),cur_trial_dict.get("T1_amp"))
			F2 = wf.soundGene2(44100,1,cur_trial_dict.get("T2_hz"),cur_trial_dict.get("T2_amp"))
			F3 = wf.soundGene2(44100,1,cur_trial_dict.get("P_hz"),cur_trial_dict.get("P_amp"))
			F_accessory = wf.soundGene2(44100,.05,3000,cur_trial_dict.get("P_amp")) # https://www.sfu.ca/sonic-studio-webdav/handbook/Click.html
			F_zero = wf.soundGene2(44100,1,0,0)
			len_accessory = len(F_accessory)
			len_tactile = len(F1)
			stp = np.divide(len_tactile,2)-np.divide(len_accessory,2)
			zerosH1 = np.zeros(int(stp))
			F_accessory = np.append(zerosH1, F_accessory)
			zerosH2 = np.zeros(len(F1) - len(F_accessory))
			F_accessory = np.append(F_accessory, zerosH2)
			# plt.plot(F1)
			# plt.plot(F_accessory)
			# plt.axvline(stp+np.divide(len_accessory,2))
			# plt.show()
			curAccessoryPosition = cur_trial_dict.get("AccessoryPosition")

			Accessory_OnOrOff = [False, False, False]
			if curAccessoryPosition==1:
				Accessory_OnOrOff[0] = True
			else:
				Accessory_OnOrOff[1] = True

			# nPracOrTest = nTest if LoG["practice"]==False else nPractice
			cur_question = cur_trial_dict.get("question")
			cur_prompt = """


""" + cur_question + """

""" + fj_message
			frame.after(500, self.H.text_fx, StimInfo, """



((( T1 )))""", False, None)
			frame.after(600, self.H.tone_fx, F1, Accessory_OnOrOff[0], F_accessory)
			frame.after(1600, self.H.forget, [StimInfo])
			frame.after(2600, self.H.text_fx, StimInfo, """



((( T2 )))""", False, None)
			frame.after(2700, self.H.tone_fx, F2, Accessory_OnOrOff[1], F_accessory)
			frame.after(3700, self.H.forget, [StimInfo])
			frame.after(4700, self.H.text_fx, StimInfo, """



((( P )))""", False, None)
			frame.after(4800, self.H.tone_fx, F3, Accessory_OnOrOff[2], F_accessory)		
			frame.after(5800, self.H.forget, [StimInfo])
			frame.after(5800, self.H.text_fx, StimInfo, cur_prompt, False, None)
			frame.after(5800, self.H.toggle_locked) # var locked toggled to False
			frame.after(5800, self.H.getTime_0)
			frame.after(5800, self.get_keypress)

	def get_keypress(self):
		win.bind("<Key>",self.compute_key_pressed)

	def compute_key_pressed(self, event):
		global rt
		LoG = globals()
		locked = LoG["locked"]
		
		if locked==False:
		 	response = event.char
		 	
		 	if response=="f" or response=="j":
		 		LoG["rt"] = self.H.getTime_1()
		 		LoG["trial"] += 1
		 		if LoG["practice"]==False:
		 			LoG["trials_to_feedback"] -= 1

		 		self.H.forget([Countr,StimInfo])
		 		response_v = meaning_f if response == "f" else meaning_j
		 		cur_question = cur_trial_dict.get("question")

		 		equal_question = False if "!" in cur_question else True 
		 		if equal_question:
		 			requestedTarget = int(cur_question[5])
		 		else:
		 			requestedTarget = int(cur_question[6])
		 		cur_TargetPosition = cur_trial_dict.get("TargetPosition")
		 		
		 		if cur_TargetPosition==0:
		 			cur_TargetPosition = requestedTarget	
		 		
		 		if equal_question:
		 			if requestedTarget==1:
		 				if cur_TargetPosition==1:
		 					resp_sdt = "hit" if response_v=="Yes" else "miss"
		 				else:
		 					resp_sdt = "cr" if response_v=="No" else "fa"
		 			else:
		 				if cur_TargetPosition==2:
		 					resp_sdt = "hit" if response_v=="Yes" else "miss"
		 				else:
		 					resp_sdt = "cr" if response_v=="No" else "fa" 
		 		else:
		 			if requestedTarget==1:
		 				if cur_TargetPosition==1:
		 					resp_sdt = "cr" if response_v=="No" else "fa"
		 				else:
		 					resp_sdt = "hit" if response_v=="Yes" else "miss"
		 			else:
		 				if cur_TargetPosition==2:
		 					resp_sdt = "cr" if response_v=="No" else "fa"
		 				else:
		 					resp_sdt = "hit" if response_v=="Yes" else "miss" 

# columnNames = ['pcode','practice','#trial','#block','questionType'
# 'condition','question','PTS','TargetPosition','AccessoryPosition','TNS',
# 'T1_hz','T1_amp','T2_hz','T2_amp','P_hz','P_amp',
# 'response_dicho','response_rating','response_sdt','rt','P_correct']

	 			data = LoG['data']

	 			data.loc[len(data)] = [pcode, LoG['practice'], LoG["trial"], LoG["block"], LoG["questionType"],
	 				cur_trial_dict.get("condition"),
	 				cur_trial_dict.get("question"),
	 				cur_trial_dict.get("PTS"),
	 				cur_trial_dict.get("TargetPosition"),
	 				cur_trial_dict.get("AccessoryPosition"),
	 				cur_trial_dict.get("TNS"),
	 				cur_trial_dict.get("T1_hz"),
	 				cur_trial_dict.get("T1_amp"),
	 				cur_trial_dict.get("T2_hz"),
	 				cur_trial_dict.get("T2_amp"),
	 				cur_trial_dict.get("P_hz"),
	 				cur_trial_dict.get("P_amp"),
	 				response_v,'NA',resp_sdt,LoG["rt"],'NA']

		 		self.H.remember([rating_label])
		 		rating_label['text'] = KeyMapReminder
		 		self.get_keypress_rating()

	def get_keypress_rating(self):
		win.bind("<Key>", self.present_compute_rating)

	def killFeedback(self, event):
		win.unbind("<Key>")
		self.H.forget([StimInfo, FaceLabel, FaceTxt])
		self.trial_fx(False)

	def present_compute_rating(self, event):
		LoG = globals()
		locked = LoG["locked"]
		data = LoG["data"]
		if locked==False:
			response = event.char
			included = False
			for x in rating_keys:
				if response==x:
					included = True
					if x==sure_key:
						data.loc[[len(data)-1],"response_rating"] = "sure"
					elif x==unsure_key:
						data.loc[[len(data)-1],"response_rating"] = "unsure"
					elif x==quiteSure_key:
						data.loc[[len(data)-1],"response_rating"] = "quiteSure"
					break
			if included==True:
				self.H.forget([Countr,StimInfo,rating_label])
				if LoG["practice"]==True or LoG["trials_to_feedback"]==0:
					FaceTxt['text'] = "Press space bar to continue."
					if LoG["practice"]==True:
						data = LoG["data"]
						list_resp_sdt = list(data.response_sdt)
						cur_resp_sdt = list_resp_sdt[-1]
						if cur_resp_sdt in ["hit","cr"]:
							face_image = happyFace
							FaceLabel["bg"] = "green"
						else:
							face_image = sadFace
							FaceLabel["bg"] = "red"
					else:
						LoG["trials_to_feedback"] = 8
						cur_accuracy_measures = self.compute_data()
						corrected_percentCorrect = cur_accuracy_measures[2]
						pc_asString = str(np.around(corrected_percentCorrect*100))
						if corrected_percentCorrect < .4:
							mssg = "Try to improve your performance. Your accuracy is " + pc_asString + "%."
							face_image = sadFace
							FaceLabel["bg"] = "red"
						else:
							if corrected_percentCorrect < .6:
								mssg = "Your performance level is okay. Accuray is " + pc_asString + "%."
								face_image = neutralFace
								FaceLabel["bg"] = "orange"
							else:
								mssg = "Keep up the good work. Accuray is " + pc_asString + "%."
								face_image = happyFace
								FaceLabel["bg"] = "green"
					FaceLabel["image"] = face_image
					FaceLabel.pack()
					FaceTxt.pack()
					win.bind("<Key>", self.killFeedback)
				elif np.mod(LoG["trial"],36) == 0:
					mssg = """
Time for a break?
Continue by pressing the space bar.
"""
					self.H.remember([StimInfo])
					self.H.text_fx(StimInfo,mssg,False,None)
					win.bind("<Key>", self.killFeedback)
				else:
					self.trial_fx(False)
			else:
				self.get_keypress_rating()

	def compute_data(self):
		LoG = globals()
		data = LoG["data"]
		list_resp_sdt = list(data.response_sdt)
		if LoG["practice"]==False:
			list_resp_sdt2 = []
			practice_list = list(data.practice)
			for x in range(len(practice_list)):
				if practice_list[x]==False:
					list_resp_sdt2.append(list_resp_sdt[x])
			list_resp_sdt = list_resp_sdt2
			list_resp_sdt = list_resp_sdt[-8:]
		nHit = 0; nMiss = 0; nCr = 0; nFa = 0
		for x in list_resp_sdt:
			if x == "hit":
				nHit += 1
			elif x == "miss":
				nMiss += 1
			elif x == "cr":
				nCr += 1
			elif x == "fa":
				nFa += 1
		N = 60
		Hit_Rate = 1 - 1/(2*N) if (nHit+nMiss)==0 else nHit/(nHit+nMiss) # https://stats.stackexchange.com/questions/134779/d-prime-with-100-hit-rate-probability-and-0-false-alarm-probability
		Fa_Rate = 1/(2*N) if (nFa+nCr)==0 else nFa/(nFa+nCr)
		P_correct = np.divide((nHit + nCr),(nHit + nCr + nMiss + nFa))
		P_error = np.divide((nFa + nMiss),(nHit + nCr + nMiss + nFa))
		P_correct_corrected = P_correct - P_error # https://www.researchgate.net/profile/Stephen-Link-2/publication/232548798_Correcting_response_measures_for_guessing_and_partial_information/links/0a85e53bc1e2d5f277000000/Correcting-response-measures-for-guessing-and-partial-information.pdf
		return np.array([Hit_Rate, Fa_Rate, P_correct_corrected])

	def thxPage(self):
		LoG = globals()
		LoG["intro_locked"] = False
		win_thx = Tk()
		win_thx.title("Feedback")
		win_thx.geometry("700x400")
		frame_thx = Frame(win_thx)
		frame_thx.pack(padx=20, pady=20)
		data = LoG["data"]

		T = Text(frame_thx,font=("Arial",25))
		T.pack(side=LEFT, fill=Y)
		if LoG['practice']==True:
			p_correct_practice_raw = self.compute_data()[2]
			nRows = len(list(data.practice))
			data.at[nRows-1,'P_correct']=p_correct_practice_raw
			data.to_csv(logfile_name)
			LoG["data"] = data
			p_correct_practice_txt = round(100*round(p_correct_practice_raw,2))
			if p_correct_practice_raw > accu_thres:
				LoG['test_locked'] = False
				quote = """
 Thank you – practice session completed.
 Your percentage correct answers (""" + str(p_correct_practice_txt) + """%) 
 is above chance.
"""
			else:
				quote = """
 Please repeat the practice session.
 Your percentage of correct answers (""" + str(p_correct_practice_txt) + """%) 
 is not above chance.
"""
		else:
			nRows = len(list(data.practice))
			data.at[nRows-1,'P_correct']= self.compute_data()[2]
			data.to_csv(logfile_name)
			LoG["data"] = data
			quote = """
 Thank you – test session completed."""
		
		T.insert(END, quote)

		zkg = Button(win_thx, text = "Close", command = win_thx.destroy)
		zkg.place(relx=.45, rely=.80)

## Global variables

instruction_practice_part1 = """
 Dear participant, 
 
 thank you for participating in the experiment.

 The experiment consists of two blocks with practice sessions before each block
 to get familiar with the task. You can have breaks every 36 trials. 
 In total, the experiment will last about 2 hours.

 Please put the over-ear headphones on and the index finger of your
 non-dominant hand on the vibration device in the box. Again, please just rest 
 your finger on it and don’t exert any pressure.

 On each trial, you will receive three vibration impulses.
 The first two vibrations are the targets (T1 and T2) and the third vibration is the probe (P).
 P can be similar to only T1 or only T2, similar to both, or different from both.
 Additionally, a quiet click tone is presented via the earphones, either during T1- or T2-
 presentation.
 
 After the presentation of the three vibrations you are presented with one of four questions:

  (1) P = T1?      (Was P the same as T1?) 
  (2) P = T2?      (Was P the same as T2?) 
  (3) P != T1?     (Was P different from T1?) 
  (4) P != T2?     (Was P different from T2?)
  """

response_keys = ["f","j"]
random.shuffle(response_keys)
if response_keys[0]=="j":
	fj_message = "F = 'No'   J = 'Yes'"
	meaning_f, meaning_j = ["No","Yes"]
else:
	fj_message = "F = 'Yes'   J = 'No'"
	meaning_f, meaning_j = ["Yes","No"]

sure_key = ["v","n"]
random.shuffle(sure_key)
sure_key = sure_key[0]
quiteSure_key = "b"
unsure_key = "n" if sure_key == "v" else "v"
rating_keys = np.array([sure_key, quiteSure_key, unsure_key])
KeyMapReminder = """



V = Sure, B = Quite sure, N = Unsure"""
if sure_key=="n":
	KeyMapReminder = """



V = Unsure, B = Quite sure, N = Sure"""


instruction_practice_part2 = """
Your task is to respond to the question by pressing:
    """ + response_keys[0].capitalize() + """ for 'yes' and 
    """ + response_keys[1].capitalize() + """ for 'no'.

It is important to note that the answer to the questions is not logically exclusive, for example: 
If the question is 'P = T1?' and P is similar to T1, the correct answer is 'yes'. 
If the question is 'P = T1?' and P is similar to both T1 and T2, the correct answer is also 'yes'!

The type of question (same/different) is blocked such that in one block either only same (=) 
or only different (!=) questions are asked. Continue with the space bar."""

instruction_practice_part3 = """

In addition to the yes/no response you give a three-point confidence rating 
regarding the certainty of your response as follows: 
""" + sure_key.capitalize() + """ = 'very sure', B = 'quite sure', """ + unsure_key.capitalize() + """ = 'unsure'.

In the practice sessions, you get trial-by-trial feedback. 
In the experimental sessions you get feedback every eight trials 
regarding your overall performance in the last eight trials 
as indicated by different faces (happy, neutral, sad). 
The feedback only refers to the yes/no response, not to your rating.

If you have any questions, please ask the experimenter.

When you are ready you can start the practice session by closing this window 
and starting the practice session.

"""

instruction_blockChange = """
In the next block the type of question changes.
You first get 16 practice trials to get familiar with the type of question.
You can have a break before you continue.

When you are ready press the space bar to start.
"""

instruction_startTest = """
You finished the practice part. In the following test session,
the type of question remains the same.

To continue, press the space bar. 
"""


intro_locked = False
test_locked = True
locked = True
intro = True
practice = True
trial = 0
jitter = 0.15
accu_thres = 0.5 
ts_init = time.time()
# duration_break = 1*60*15 # minutes
# NTrialsTillFeedback = 2

H = helprs()
TF = trialFunctions()

while True:
	print()
	AB_or_BA = input("Which sequence (AB vs. BA)? ")
	print()
	block = input("Which block (1 vs. 2)? ")
	print()
	if AB_or_BA=="AB":
		if block=="1":
			questionType="equal"
			break
		elif block=="2":
			questionType="unequal"
			break
	elif AB_or_BA=="BA":
		if block=="1":
			questionType="unequal"
			break
		elif block=="2":
			questionType="equal"
			break


win = Tk()
win.attributes("-fullscreen")
win.title("DMS")
win.geometry("750x500+000+000")
close_btn = Button(win, text = "Close", command = win.destroy)
close_btn.pack(side=BOTTOM, pady=25)
frame = Frame(win)
frame.pack(padx=20, pady=20)
rating_label = Label(frame, font=("Arial bold", 25)) 

happyFace = ImageTk.PhotoImage(Image.open("happy.png"))
neutralFace = ImageTk.PhotoImage(Image.open("neutral.png"))
sadFace = ImageTk.PhotoImage(Image.open("sad.png"))

pcodefile = open("p_code.txt","r")
pcode = pcodefile.read()
pcodefile.close()

columnNames = ['pcode','practice','trial','block','questionType',
'condition','question','PTS','TargetPosition','AccessoryPosition','TNS',
'T1_hz','T1_amp','T2_hz','T2_amp','P_hz','P_amp',
'response_dicho','response_rating','response_sdt','rt','P_correct']

logfile_path = os.getcwd() + "/"
logfile_name = "{}dms_{}_{}.csv".format(logfile_path, pcode, block)
# nTest = len(conditions_test)
list_trial_dicts_practice_eq = H.stimfx(practice=True, questionType="eq")
list_trial_dicts_test_eq = H.stimfx(practice=False, questionType="eq")
list_trial_dicts_practice_uneq = H.stimfx(practice=True, questionType="uneq")
list_trial_dicts_test_uneq = H.stimfx(practice=False, questionType="uneq")
print(len(list_trial_dicts_test_eq), len(list_trial_dicts_test_uneq), 
	len(list_trial_dicts_practice_eq), len(list_trial_dicts_practice_uneq))

TF.trial_fx(firstCall=True)

win.mainloop()
