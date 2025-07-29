import pandas as pd
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk 
import random
import os



## Helpfer functions
def code_fx():

	letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q',
				'r','s','t','u','v','w','x','y','z']
	digits = [0,1,2,3,4,5,6,7,8,9]
	symbols = ['!','#']
	random.shuffle(letters)
	random.shuffle(digits)
	random.shuffle(symbols)

	word=letters[0]
	for x in range(1,3):
		word = word + letters[x]
	word = word + symbols[0]
	for x in range(3):
		word = word + str(digits[x])

	word_shuffled = []
	for x in word: word_shuffled.append(x)
	random.shuffle(word_shuffled)

	for x in word_shuffled:
		if x == word_shuffled[0]:
			word_shuffled2 = x
		else:
			word_shuffled2 = word_shuffled2 + x

	return word_shuffled2

def close_fx():
	win_main.destroy()

def text_fx(field_name,txt,state,fg,pady):
	field_name.tag_configure("center",justify="center")
	field_name.pack(pady=10)
	field_name.insert(1.0,txt)
	field_name.configure(state=state,fg=fg,pady=pady)
	field_name.tag_add("center","1.0","end")

def space_fx(frame,height,state):
	space = Text(frame,height=height, bd=0, bg="white", 
        fg="black",highlightthickness = 0, borderwidth=0)
	space.pack()
	space.configure(state=state)

def getInput():
        result = textbox.get("1.0","end")
        textbox.delete(1.0,"end")
        return result

def clear_content(field_names):
	for x in range(len(field_names)):
		field_names[x].delete("1.0",END)

def clear_frame(i):
	for widgets in q_frame.winfo_children():
		widgets.destroy()
	if i == len(QItems):
		LoG = globals()
		LoG["i"] = 0
		q_win.destroy()
	else:
		questionnaire_fx(i)
def storeData(data):
	data.to_csv(logfile_name)

def submit():
	LoG = globals(); i = LoG["i"]; data = LoG["data"]
	newInput = str.rstrip(getInput())
	if len(newInput)>0:
		i += 1; LoG["i"] = i
		data[columns[i]] = newInput
		LoG["data"]=data
		clear_frame(i)
	else:
		messagebox.showinfo(message="Kein Eintrag im Textfeld erkannt.")

def yes_fx():
	LoG = globals(); i = LoG["i"]; data = LoG["data"]
	i += 1; LoG["i"] = i
	data[columns[i]] = "Ja"
	LoG["data"]=data
	clear_frame(i)                

def no_fx():
	LoG = globals(); i = LoG["i"]; data = LoG["data"]
	i += 1; LoG["i"] = i
	data[columns[i]] = "Nein"
	LoG["data"]=data
	clear_frame(i)
def right_fx():
	LoG = globals(); i = LoG["i"]; data = LoG["data"]
	i += 1; LoG["i"] = i
	data[columns[i]] = "Rechts"
	LoG["data"]=data
	clear_frame(i)
def left_fx():
	LoG = globals(); i = LoG["i"]; data = LoG["data"]
	i += 1; LoG["i"] = i
	data[columns[i]] = "Links"
	LoG["data"]=data
	clear_frame(i)
def alwaysLeft_fx():
	LoG = globals(); i = LoG["i"]; data = LoG["data"]
	subFx(strength = 2)
	i += 1; LoG["i"] = i
	data[columns[i]] = "immer links"
	if i==(len(QItems)):
		positive=LoG["positive"]; negative=LoG["negative"]
		positive_sum=0
		negative_sum=0
		for x in positive:
			positive_sum += x
		negative_sum=0
		for x in negative:
			negative_sum += x
		messagebox.showinfo(message="Vielen Dank - Fragebogen vollständig ausgefüllt.")
		if (positive_sum+negative_sum)==0:
			LQ = 0
		else:
			LQ = ((positive_sum-negative_sum)/(positive_sum+negative_sum))*100
		print(LQ)
		data['LQ'] = LQ
		storeData(data)
	LoG["data"]=data
	clear_frame(i)
def mostlyLeft_fx():
	#subFx(strength = -1)
	subFx(strength = 1)
	LoG = globals(); i = LoG["i"]; data = LoG["data"]
	i += 1; LoG["i"] = i
	data[columns[i]] = "meistens links"
	if i==(len(QItems)):
		positive=LoG["positive"]; negative=LoG["negative"]
		positive_sum=0
		negative_sum=0
		for x in positive:
			positive_sum += x
		negative_sum=0
		for x in negative:
			negative_sum += x
		messagebox.showinfo(message="Vielen Dank - Fragebogen vollständig ausgefüllt.")
		if (positive_sum+negative_sum)==0:
			LQ = 0
		else:
			LQ = ((positive_sum-negative_sum)/(positive_sum+negative_sum))*100
		print(LQ)
		data['LQ'] = LQ
		storeData(data)
	LoG["data"]=data
	clear_frame(i) 
def both_fx():
	LoG = globals(); i = LoG["i"]; data = LoG["data"]
	subFx(strength = 0)
	addFx(strength = 0)
	i += 1; LoG["i"] = i
	data[columns[i]] = "gleichermaßen"
	if i==(len(QItems)):
		positive=LoG["positive"]; negative=LoG["negative"]
		positive_sum=0
		negative_sum=0
		for x in positive:
			positive_sum += x
		negative_sum=0
		for x in negative:
			negative_sum += x
		messagebox.showinfo(message="Vielen Dank - Fragebogen vollständig ausgefüllt.")
		if (positive_sum+negative_sum)==0:
			LQ = 0
		else:
			LQ = ((positive_sum-negative_sum)/(positive_sum+negative_sum))*100
		print(LQ)
		data['LQ'] = LQ
		storeData(data)
	LoG["data"]=data
	clear_frame(i)
def mostlyRight_fx():
	LoG = globals(); i = LoG["i"]; data = LoG["data"]
	addFx(strength = 1)
	i += 1; LoG["i"] = i
	data[columns[i]] = "meistens rechts"
	if i==(len(QItems)):
		positive=LoG["positive"]; negative=LoG["negative"]
		positive_sum=0
		negative_sum=0
		for x in positive:
			positive_sum += x
		negative_sum=0
		for x in negative:
			negative_sum += x
		#negative_sum = negative_sum*-1
		messagebox.showinfo(message="Vielen Dank - Fragebogen vollständig ausgefüllt.")
		if (positive_sum+negative_sum)==0:
			LQ = 0
		else:
			LQ = ((positive_sum-negative_sum)/(positive_sum+negative_sum))*100
		data['LQ'] = LQ
		storeData(data)
	LoG["data"]=data
	clear_frame(i)
def alwaysRight_fx():
	LoG = globals(); i = LoG["i"]; data = LoG["data"]
	addFx(strength = 2)
	i += 1; LoG["i"] = i
	data[columns[i]] = "immer rechts"
	if i==(len(QItems)):
		positive=LoG["positive"]; negative=LoG["negative"]
		positive_sum=0
		negative_sum=0
		for x in positive:
			positive_sum += x
		negative_sum=0
		for x in negative:
			negative_sum += x
		messagebox.showinfo(message="Vielen Dank - Fragebogen vollständig ausgefüllt.")
		if (positive_sum+negative_sum)==0:
			LQ = 0
		else:
			LQ = ((positive_sum-negative_sum)/(positive_sum+negative_sum))*100
		data['LQ'] = LQ
		storeData(data)
	LoG["data"]=data
	clear_frame(i)

def addFx(strength):
	LoG = globals()
	positive = LoG["positive"] 
	positive.append(strength)
	LoG["positive"] = positive

def subFx(strength):
	LoG = globals()
	negative = LoG["negative"] 
	negative.append(strength)
	LoG["negative"] = negative

def questionnaire_fx(i):
	global question, prompt, textbox
	if i==0:
		global q_frame, q_win
		q_win = Tk()
		q_win.title("Fragebogen")
		q_win.configure(background='white')
		q_win.attributes('-fullscreen',True)
		q_frame = Frame(q_win,bg='white')
		q_frame.pack(padx=20, pady=20)
		
	question = Text(q_frame,height=2,width=100,font=("Arial bold",20),highlightthickness=0,borderwidth=0) 
	prompt = Text(q_frame,height=2,width=100,font=("Arial",15),highlightthickness=0,borderwidth=0)
	text_fx(field_name=question, txt=QItems[i].get('question'), state="disabled",fg="black",pady=100)
	text_fx(field_name=prompt, txt=QItems[i].get('prompt'), state="disabled",fg="black",pady=0)
	LoG = globals()

	resp_format = QItems[i].get('type')
	if resp_format=="openQ":
		textbox = Text(q_frame,height = 2,width = QItems[i].get("width"),borderwidth = 2)
		textbox.focus_force()
		textbox.pack()
		space_fx(q_frame,5,"normal")
		submit_button = Button(q_frame, command=submit,
			height=2, width=8, font=("Arial",15),text="Weiter")
		submit_button.pack()
	if resp_format=="r_or_l":
		space_fx(q_frame,4,"normal")
		b_l = Button(q_frame, command=left_fx, height=2, width=8, font=("Arial",15),
			text="Links")
		b_l.place(relx = 0.4, rely = .8, anchor = CENTER)
		b_r = Button(q_frame, command=right_fx, height=2, width=8, font=("Arial",15),
			text="Rechts")
		b_r.place(relx = 0.6, rely = .8, anchor = CENTER)
	if resp_format=="y_or_n":
		space_fx(q_frame,4,"normal")
		b_y = Button(q_frame, command=yes_fx, height=2, width=8, font=("Arial",15),
			text="Ja")
		b_y.place(relx = 0.4, rely = .8, anchor = CENTER)
		b_n = Button(q_frame, command=no_fx, height=2, width=8, font=("Arial",15),
			text="Nein")
		b_n.place(relx = 0.6, rely = .8, anchor = CENTER)
	if resp_format=="likert": 
		space_fx(q_frame,4,"normal")
		b_alwaysLeft = Button(q_frame, command=alwaysLeft_fx, height=2, width=15, font=("Arial",15),
			text="immer links")
		b_alwaysLeft.place(relx = 0.1, rely = .8, anchor = CENTER)
		b_mostlyLeft = Button(q_frame, command=mostlyLeft_fx, height=2, width=15, font=("Arial",15),
			text="meistens links")
		b_mostlyLeft.place(relx = 0.3, rely = .8, anchor = CENTER)
		b_both = Button(q_frame, command=both_fx, height=2, width=15, font=("Arial",15),
			text="gleich oft l/r")
		b_both.place(relx = 0.5, rely = .8, anchor = CENTER)
		b_mostlyRight = Button(q_frame, command=mostlyRight_fx, height=2, width=15, font=("Arial",15),
			text="meistens rechts")
		b_mostlyRight.place(relx = 0.7, rely = .8, anchor = CENTER)
		b_alwaysRight = Button(q_frame, command=alwaysRight_fx, height=2, width=15, font=("Arial",15),
			text="immer rechts")
		b_alwaysRight.place(relx = 0.9, rely = .8, anchor = CENTER)

	i = LoG["i"]; data = LoG["data"]

def projectInfo(win_name,frame_name,title,dimensions):
		win_name = Tk()
		win_name.title(title)
		win_name.geometry(dimensions)
		frame_name = Frame(win_name)
		frame_name.pack(padx=2, pady=20)
		S = Scrollbar(frame_name)
		T = Text(frame_name,height=20, width=160, font=("Arial",15), 
			fg = 'black', highlightthickness = 1, borderwidth=1,relief="groove")
		S.pack(side=RIGHT, fill=Y)
		T.pack(side=LEFT, fill=Y)
		S.config(command=T.yview)
		T.config(yscrollcommand=S.set)
		T.insert(END,'\nTactile Short-Term Memory\n', 'big')
		quote = """
		\n Der Tastsinn ist eine wesentliche Wahrnehmungsmodalität der meisten Lebewesen und essentiell für die Interaktion mit der Umwelt. \n Obwohl die taktile Wahrnehmung fundamentaler ist, z.B. ontogenetisch früher reift, als die visuelle oder die auditive Wahrnehmung, \n ist sie vergleichsweise wenig erforscht worden, insbesondere von der kognitionspsychologischen Grundlagenforschung.\n Das Ziel unseres Projekts („Audio-Tactile Short-Term Memory“, gefördert vom Fond zur Förderung der wissenschaftlichen Forschung,\n ist es zunächst, in diese Forschungslücke zu stoßen. Im Anschluss werden wir in weiteren Experimenten die sensorische Integration\n von taktiler und auditiver Wahrnehmung untersuchen.
		\n Ein aktiver Teil der Wahrnehmung ist das Gedächtnis. Es beeinflusst, was wahrgenommen wird und wie die Wahrnehmungsinhalte verarbeitet \n und gespeichert werden. Damit leistet es einen entscheidenden Beitrag zu Top-down-Prozessen der Wahrnehmung. \n Bancrofts (2016) Arbeit legt nahe, dass im taktilen Sinn prinzipiell ein (Kurzzeit )Gedächtnis vorhanden ist, das ähnliche Eigenschaften\n wie das auditorische und visuelle Kurzzeitgedächtnis aufweist. Ein Schwerpunkt der vorliegenden Studie liegt darauf, diese Ergebnisse zu replizieren \n sowie die Beständigkeit taktiler Gedächtnisrepräsentationen experimentell zu ergründen und die empirischen Daten mit den Ergebnissen \n modellbasierter Simulationen von Verhaltensdaten zum Zwecke einer Modellvalidierung abzugleichen.
		
		\n Als theoretische Grundlage für das Modell dient das Temporal Context-Modell (Kahana, 2020), das annimmt, dass Wahrnehmungsinhalte einer \n peripheren Ebene der Reizverarbeitung, der sogenannten Itemebene, auf eine zentralere (d.h. modalitätsübergreifende) \n Kontextebene projiziert, aufrechterhalten und durch neu eintreffende Iteminformationen aktualisiert werden. Auf Basis dieser \n Theorie versuchen wir verschiedene Ursachen für Interferenzmechanismen zu finden und mit Limitationen der taktilen Gedächtniskapazität \n in Beziehung zu setzen. Um dies zu untersuchen, sollen in einem Experiment Sequenzen von vibro-taktilen Stimuli mit unterschiedlichen Frequenzen \n dargeboten werden. Die Aufgabe dabei ist es, die Frequenzen zu unterscheiden und anzugeben, ob ein Probe-Stimulus \n derselbe ist wie einer der beiden vorigen Target-Stimuli.
		\n Typischerweise werden unterschiedliche Frequenzen (z.B. im taktilen und auditiven Bereich), auch wenn sie mit physikalisch identer Intensität (= Amplitude) \n präsentiert werden, nicht als subjektiv gleich intensiv wahrgenommen. Eine schnellere Frequenz wird \n beispielsweise als intensiver (z.B. lauter) wahrgenommen als eine langsamere Frequenz, wenn die Amplituden beider \n Frequenzen gleich sind. Um unerwünschte Effekte zu vermeiden, müssen die Amplituden der verschiedenen Frequenzen aufeinander abgestimmt \n werden, damit alle Frequenzen subjektiv als gleich intensiv wahrgenommen werden. Das ist das Ziel dieses Vorexperiments. Die hier gewonnen Daten können \n dann für die Hauptexperimente des Projekts verwendet werden.

		\n Vielen Dank für die Teilnahme an unserer Studie! Falls Sie weitere Fragen haben, kontaktieren Sie uns gerne. Bei weiterem Interesse verweisen wir außerdem \n auf die Projektseite (https://osf.io/5hpe3/).

		\n Das Projektteam besteht aus:
		\n Paul Seitlinger \n (paul.seitlinger@univie.ac.at) \n Marie-Luise Augsten \n (marie-luise.augsten@univie.ac.at) \n Bernhard Laback \n (bernhard.laback@oeaw.ac.at) \n Ulrich Ansorge \n (ulrich.ansorge@univie.ac.at)

		\n Literatur
		\n Bancroft, T. (2016). Scalar short-term memory (Publication No. 1825) [Doctoral dissertation, Wilfrid Laurier University].\n Theses and Dissertations (comprehensive). https://scholars.wlu.ca/etd/1825. 
		\n Kahana, M. J. (2020). Computational models of memory search. Annual Review of Psychology, 71, 107-138.\n https://doi.org/10.1146/annurev-psych-010418-103358.

		"""
		T.insert(END, quote)
		
		zkg = Button(win_name, text = "Zur Kenntnis genommen",command = win_name.destroy)
		zkg.place(relx=.01,rely=.8)

def dataMngt(win_name,frame_name,title):
		win_name = Tk()
		win_name.title(title)
		#win_name.geometry(dimensions)
		win_name.attributes('-fullscreen',True)
		frame_name = Frame(win_name)
		frame_name.pack(padx=2, pady=20)
		S = Scrollbar(frame_name)
		T = Text(frame_name,height=20, width=140, font=("Arial",15), fg = 'black')#,
		 #highlightthickness = 1, borderwidth=1, relief="groove")
		S.pack(side=RIGHT, fill=Y)
		T.pack(side=LEFT, fill=Y)
		S.config(command=T.yview)
		T.config(yscrollcommand=S.set)
		T.insert(END,'\nDatenmanagement und Rechte\n', 'big')
		quote = """
		\nSie sind dazu eingeladen, an der Studie AllgBioPsych_21WS_Tactile Amplitude Balancing als Versuchsperson teilzunehmen.
		\nIhre Rechte: Selbstverständlich können Sie vor und jederzeit während der Studie weitere Informationen über Zweck, Ablauf etc. der Studie von den \n studiendurchführenden Personen erfragen. Nach Durchführung des Experiments erhalten Sie in jedem Fall eine ausführliche schriftliche Information.\n Gerne werden Sie auch nach Ende der Studie über die Ergebnisse der Untersuchung informiert.\n Sie können die Untersuchung jederzeit ohne Angabe von Gründen von sich aus abbrechen. 
		\nDatenschutz: Sämtliche Ihre Person betreffenden Daten werden getrennt von den erhobenen Daten aufbewahrt, sodass Ihre Anonymität gewährt bleibt.\n Aus Gründen transparenter Wissenschaftspraxis werden die erhobenen Daten in anonymisierter Form online und frei zugänglich für die weitere Nutzung \n zur Verfügung gestellt (open science). Es ist geplant, die im Rahmen der Untersuchung erhobenen Daten in einer wissenschaftlichen Zeitschrift \n zu veröffentlichen. 
		\nVergütung: Sie erhalten für Ihre Teilnahme LABS Credits. 
		"""
		T.insert(END, quote)
		
		zkg2 = Button(win_name, text = "Zur Kenntnis genommen",command = win_name.destroy)
		zkg2.place(relx=.01,rely=.8)

def get_keypress():
	win_main.bind("<Key>",open_win)
def open_win(event):
	LoG = globals()
	response = event.char
	if response == "b":
		projectInfo(win_name="project_win",frame_name="project_frame",
			title="Projektinformationen",dimensions="1100x500+750+200")
	elif response == "d":
		dataMngt(win_name="dm_win",frame_name="dm_frame",
			title="Datenmanagement")
	elif response == "q":
		questionnaire_fx(i=0)

QItems = [
		{'question':'Wie alt sind Sie?',
			'type': 'openQ',
			'prompt': 'Bitte nur natürliche Zahlen eintippen (z. B. 23)',
			'width': 3},
		{'question':'Was ist Ihr Geschlecht / Gender?',
			'type': 'openQ',
			'prompt': 'z. B. weiblich, männlich, anderes, keine Angabe',
			'width': 20},
		{'question':'Sind Sie links- oder rechtshändig?',
			'type': 'r_or_l',
			'prompt': '',
			'width': ''},
		{'question':'Leiden Sie an etwas,\n das Ihren Berührungssinn beeinträchtigen könnte?',
			'type': 'y_or_n',
			'prompt': '',
			'width': ''},
		{'question':'Hatten Sie irgendwelche Verletzungen \n und / oder Operationen an den Händen?',
			'type': 'y_or_n',
			'prompt': '',
			'width': ''},
		{'question':'Waren Sie Phasen starker und / oder langer Vibration \n'
 			+ 'der Hände ausgesetzt (z.B. bei Bauarbeiten)?',
			'type': 'y_or_n',
			'prompt': '',
			'width': ''},
		{'question':'Waren sie vor Kurzem einer Vibration der Hände ausgesetzt',
			'type': 'y_or_n',
			'prompt': '',
			'width': ''},
		{'question':"Wenn Sie schreiben, dann...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Wenn Sie zeichnen, dann...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Wenn Sie etwas werfen, dann...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Eine Schere benutzen Sie...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Einen Kamm halten Sie...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Die Zahnbürste halten Sie...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Ein Messer (ohne Gabel) halten Sie...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Den Löffel halten Sie...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Wenn Sie einen Hammer benutzen, dann...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Einen Schraubendreher halten Sie...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Den Tennisschläger halten Sie...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Wenn Sie ein Messer (mit Gabel) verwenden, dann...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Wenn Sie ein Streichholz anzünden, dann...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Wenn Sie eine Schachtel (mit Deckel) öffnen, dann...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Die Karten mischen Sie...",
			'type': 'likert',
			'prompt': '',
			'width': ''},
		{'question':"Einen Faden in das Nadelöhr fädelen Sie ein...",
			'type': 'likert',
			'prompt': '',
			'width': ''}
		]

columns = ['pcode','age','gender','handedness','tactile-related issues',
        'hand injury','long vibration exposure','recent vibration exposure',
        'Schreiben','Zeichnen','Werfen','Schere',"Kamm",'Zahnbürste',"Messer",
        'Löffel','Hammer','Schraubendreher','Tennisschläger','Messer (mit Gabel)',
        'Streichholz','Schachtel','Karten','Faden','LQ']
data = pd.DataFrame(columns=columns)

pcode = code_fx()
#pcode='!' ##
data.loc[len(data)] = pcode
#data = data.append({columns[0]:pcode},ignore_index=True)
pcodefile = open("p_code.txt","w+")
pcodefile.write(pcode)
pcodefile.close()

i = 0
positive = []
negative = []
## Start page
win_main = Tk()
win_main.title("Hintergrundinformationen & Fragebogen")
win_main.configure(background='white')
win_main.attributes('-fullscreen',True)
frame_main = Frame(win_main)
frame_main.pack(padx=20, pady=20)

logfile_path = "C:/Users/a47_nb_admin/Documents/GitHub/STIWA/"
logfile_name = "qdata_{}.csv".format(pcode)
  
T = Text(frame_main, font=("Arial",15), fg = 'black', highlightthickness = 0, borderwidth=0) 
T.pack(side=LEFT)#, fill=Y)
T.insert(END,'\nLiebe*r Versuchsteilnehmer*in!\n', 'big')
quote = """
\nDie Studie besteht aus drei Teilen: einem Fragebogen, einem auditiven und einem taktilen Test.\nZwischen den Teilen und während des letzten Teils können Sie Pausen machen.
\n\n1. Machen Sie sich bitte zunächst mit unserem Datenmanagement vertraut sowie Ihren Rechten\n    (Taste 'D').\n2. Im Falle Ihres Einverständnisses, unterschreiben Sie bitte das ausgedruckte Blatt
    zur informierten Einwilligung.\n3. Füllen Sie den Fragebogen aus, den Sie mit der Taste 'Q' öffnen. 
"""
T.insert(END,quote)
endBtn = Button(win_main,padx=7, pady=10, height=1, width=8, 
	font=("Arial",15), text="Beenden",command=close_fx)
endBtn.place(relx = 0.5, rely = .9, anchor = CENTER)
get_keypress()
win_main.mainloop()






