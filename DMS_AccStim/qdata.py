import pandas as pd
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk 
import random
import os
import time


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
        messagebox.showinfo(message="Your input has not been recognized.")

def yes_fx():
    LoG = globals(); i = LoG["i"]; data = LoG["data"]
    i += 1; LoG["i"] = i
    data[columns[i]] = "Yes"
    LoG["data"]=data
    clear_frame(i)                

def no_fx():
    LoG = globals(); i = LoG["i"]; data = LoG["data"]
    i += 1; LoG["i"] = i
    data[columns[i]] = "No"
    LoG["data"]=data
    clear_frame(i)
def right_fx():
    LoG = globals(); i = LoG["i"]; data = LoG["data"]
    i += 1; LoG["i"] = i
    data[columns[i]] = "Right"
    LoG["data"]=data
    clear_frame(i)
def left_fx():
    LoG = globals(); i = LoG["i"]; data = LoG["data"]
    i += 1; LoG["i"] = i
    data[columns[i]] = "Left"
    LoG["data"]=data
    clear_frame(i)
def alwaysLeft_fx():
    LoG = globals(); i = LoG["i"]; data = LoG["data"]
    subFx(strength = 2)
    i += 1; LoG["i"] = i
    data[columns[i]] = "Always left"
    if i==(len(QItems)):
        positive=LoG["positive"]; negative=LoG["negative"]
        positive_sum=0
        negative_sum=0
        for x in positive:
            positive_sum += x
        negative_sum=0
        for x in negative:
            negative_sum += x
        messagebox.showinfo(message="Thank you - you completed the questionnaire.")
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
    data[columns[i]] = "Usually left"
    if i==(len(QItems)):
        positive=LoG["positive"]; negative=LoG["negative"]
        positive_sum=0
        negative_sum=0
        for x in positive:
            positive_sum += x
        negative_sum=0
        for x in negative:
            negative_sum += x
        messagebox.showinfo(message="Thank you - you completed the questionnaire.")
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
    data[columns[i]] = "No preference"
    if i==(len(QItems)):
        positive=LoG["positive"]; negative=LoG["negative"]
        positive_sum=0
        negative_sum=0
        for x in positive:
            positive_sum += x
        negative_sum=0
        for x in negative:
            negative_sum += x
        messagebox.showinfo(message="Thank you - you completed the questionnaire.")
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
    data[columns[i]] = "Usually right"
    if i==(len(QItems)):
        positive=LoG["positive"]; negative=LoG["negative"]
        positive_sum=0
        negative_sum=0
        for x in positive:
            positive_sum += x
        negative_sum=0
        for x in negative:
            negative_sum += x
        #neative_sum = negative_sum*-1
        messagebox.showinfo(message="Thank you - you completed the questionnaire.")
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
    data[columns[i]] = "Always right"
    if i==(len(QItems)):
        positive=LoG["positive"]; negative=LoG["negative"]
        positive_sum=0
        negative_sum=0
        for x in positive:
            positive_sum += x
        negative_sum=0
        for x in negative:
            negative_sum += x
        messagebox.showinfo(message="Thank you - you completed the questionnaire.")
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
        q_win.title("Questionnaire")
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
            height=2, width=8, font=("Arial",15),text="Continue")
        submit_button.pack()
    if resp_format=="r_or_l":
        space_fx(q_frame,4,"normal")
        b_l = Button(q_frame, command=left_fx, height=2, width=8, font=("Arial",15),
            text="Left")
        b_l.place(relx = 0.4, rely = .8, anchor = CENTER)
        b_r = Button(q_frame, command=right_fx, height=2, width=8, font=("Arial",15),
            text="Right")
        b_r.place(relx = 0.6, rely = .8, anchor = CENTER)
    if resp_format=="y_or_n":
        space_fx(q_frame,4,"normal")
        b_y = Button(q_frame, command=yes_fx, height=2, width=8, font=("Arial",15),
            text="Yes")
        b_y.place(relx = 0.4, rely = .8, anchor = CENTER)
        b_n = Button(q_frame, command=no_fx, height=2, width=8, font=("Arial",15),
            text="No")
        b_n.place(relx = 0.6, rely = .8, anchor = CENTER)
    if resp_format=="likert": 
        space_fx(q_frame,4,"normal")
        b_alwaysLeft = Button(q_frame, command=alwaysLeft_fx, height=2, width=15, font=("Arial",15),
            text="Always left")
        b_alwaysLeft.place(relx = 0.1, rely = .8, anchor = CENTER)
        b_mostlyLeft = Button(q_frame, command=mostlyLeft_fx, height=2, width=15, font=("Arial",15),
            text="Usually left")
        b_mostlyLeft.place(relx = 0.3, rely = .8, anchor = CENTER)
        b_both = Button(q_frame, command=both_fx, height=2, width=15, font=("Arial",15),
            text="No preference")
        b_both.place(relx = 0.5, rely = .8, anchor = CENTER)
        b_mostlyRight = Button(q_frame, command=mostlyRight_fx, height=2, width=15, font=("Arial",15),
            text="Usually right")
        b_mostlyRight.place(relx = 0.7, rely = .8, anchor = CENTER)
        b_alwaysRight = Button(q_frame, command=alwaysRight_fx, height=2, width=15, font=("Arial",15),
            text="Always right")
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
        \n The tactile sense is part of the human sensory system and essential for interacting with the environment. \n Although tactile perception is more fundamental than visual or auditory perception (e.g., tactile perception is the first sense to develop), little research has been \n done on tactile perception in the context of memory. \n Therefore, the aim of the present project („Audio-Tactile Short-Term Memory“, funded by the Austrian Science Fund (FWF)),\n is to investigate the tactile short-term memory and its role in tactile-auditory integration.
        \n Memory is an active part of perception as it influences which information is processed and stored preferentially. \n Therefore, memory plays an important role in the top-down modulation of sensory processing. \n According to Bancroft (2016), tactile perception is supported \n by short-term memory structures that are comparable to memory structures of the visual and auditory domain. \n One aim of the present project is to replicate previous results on the nature and quality of tactile short-term memory \n by using a combined experimental and computational approach.
        \n The theoretical foundation of our study is the Temporal Context Model (Kahana, 2020) which suggests that input from \n a peripheral sensory level (i.e., item layer) is projected to a (cross-modal) central \n sensory level (i.e., context layer) where it is maintained and \n updated based on incoming (sensory) item information. \n Accordingly, we aim to identify factors causing interference in tactile short-term memory that may contribute to short-term memory capacity limits. \n To examine this question, participants are presented with vibro-tactile stimuli with varying frequencies. \n Then, the participants must decide whether the frequency of a target vibration was either identical or different from the frequency of a probe.
        \n Typically, different frequencies (e.g., in the tactile and auditory domain) are not perceived as equally intense \n - not even if they are presented with the same physical intensity (= amplitude). For example, \n higher frequencies \n are perceived as more intense (e.g., louder) \n than lower frequencies with identical amplitudes. \n To reduce confounding effects in the main experiment, we must adapt the amplitudes of different frequencies in such a way that all frequencies are perceived as equally intense. This is subject to the pre-experiment. 

        \n Thank you for participating in our study! Please feel free to contact us in case of further questions. If you are interested, we invite you to visit \n our website (https://osf.io/5hpe3/).

        \n The project team consists of:
        \n Paul Seitlinger \n (paul.seitlinger@univie.ac.at) \n Marie-Luise Augsten \n (marie-luise.augsten@univie.ac.at) \n Bernhard Laback \n (bernhard.laback@oeaw.ac.at) \n Ulrich Ansorge \n (ulrich.ansorge@univie.ac.at)

        \n Literature
        \n Bancroft, T. (2016). Scalar short-term memory (Publication No. 1825) [Doctoral dissertation, Wilfrid Laurier University].\n Theses and Dissertations (comprehensive). https://scholars.wlu.ca/etd/1825. 
        \n Kahana, M. J. (2020). Computational models of memory search. Annual Review of Psychology, 71, 107-138.\n https://doi.org/10.1146/annurev-psych-010418-103358.

        """
        T.insert(END, quote)
        
        zkg = Button(win_name, text = "Took note",command = win_name.destroy)
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
        T.insert(END,'\nData management and rights\n', 'big')
        quote = """
        \nYou are invited to participate in the study AllgBioPsych_21WS_Tactile Amplitude Balancing.
        \nRights: If you have any questions concerning this study (e.g., aim, procedure), you can ask the experimenter at any time before or during the experiment. \n After you completed the study, you will be provided with comprehensive written information. \n If requested, you will be provided with the results of the experiment after the study is completed.\n You are free to withdraw at any time, without giving a reason and without cost. 
        \nPrivacy statement: All information you provide will remain confidential and will not be associated with your name.\n For reasons of scientific transparency, the de-identified data may be shared publicly for further use (open science). \n The data collected as part of this study may be published in a scientific journal.
        \nCompensation: Your participation will be compensated by LABS credits.
        """
        T.insert(END, quote)
        
        zkg2 = Button(win_name, text = "I understand my rights and agree to participate in the study",command = win_name.destroy)
        zkg2.place(relx=.01,rely=.8)

def get_keypress():
    win_main.bind("<Key>",open_win)
def open_win(event):
    LoG = globals()
    response = event.char
    if response == "b":
        projectInfo(win_name="project_win",frame_name="project_frame",
            title="Project information",dimensions="1100x500+750+200")
    elif response == "d":
        dataMngt(win_name="dm_win",frame_name="dm_frame",
            title="Data management")
    elif response == "q":
        questionnaire_fx(i=0)

QItems = [
        {'question':'How old are you?',
            'type': 'openQ',
            'prompt': 'Please enter only natural numbers (e.g., 23)',
            'width': 3},
        {'question':'What is your sex / gender?',
            'type': 'openQ',
            'prompt': 'e.g., f, m, other, not specified',
            'width': 20},
        {'question':'Are you left-handed or right-handed?',
            'type': 'r_or_l',
            'prompt': '',
            'width': ''},
        {'question':'Are you suffering from a condition \n that may impair your tactile sensation?',
            'type': 'y_or_n',
            'prompt': '',
            'width': ''},
        {'question':'Have you ever had any hand injuries \n and / or hand surgeries?',
            'type': 'y_or_n',
            'prompt': '',
            'width': ''},
        {'question':'Have you ever been exposed to high and / or sustained hand-arm vibrations\n'
            + '(e.g., constructional work)?',
            'type': 'y_or_n',
            'prompt': '',
            'width': ''},
        {'question':'Have you recently been exposed to high and / or sustained hand-arm vibrations?',
            'type': 'y_or_n',
            'prompt': '',
            'width': ''},
        {'question':"When you are writing, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are drawing, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are throwing, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are using scissors, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are holding a comb, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are holding your toothbrush, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are using a knife (without a fork), then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are holding a spoon, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are using a hammer, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are using a screwdriver, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are holding a tennis racket, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are using a knife (with a fork), then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are striking a match, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are opening a box, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are dealing with cards, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''},
        {'question':"When you are threading a needle, then...",
            'type': 'likert',
            'prompt': '',
            'width': ''}
        ]

columns = ['pcode','age','gender','handedness','tactile-related issues',
        'hand injury','long vibration exposure','recent vibration exposure',
        'Writing','Drawing','Throwing','Scissors','Comb','Toothbrush','Knife',
        'Spoon','Hammer','Screwdriver','Tennis racket','Knife (with fork)',
        'Match','Box','Cards','Needle','LQ']
data = pd.DataFrame(columns=columns)

pcode = code_fx()
data.at[len(data)-1,"pcode"] = pcode
pcodefile = open("p_code.txt","w+")
pcodefile.write(pcode)
pcodefile.close()

# tsmpFile = open("p_tsmp.txt","w+")
# start_tsmp = time.time()
# tsmpFile.write(str(start_tsmp))
# tsmpFile.close()

curdir = os.getcwd()
curdir_split = curdir.split("/")
file_path = ""
for x in range(len(curdir_split)):
   file_path = file_path + curdir_split[x] + "/" 
file_path = file_path + "qdata"

logfile_name = "{}_{}.csv".format(file_path, pcode)

i = 0
positive = []
negative = []
## Start page
win_main = Tk()
win_main.title("Background information & questionnaire")
win_main.configure(background='white')
win_main.attributes('-fullscreen',True)
frame_main = Frame(win_main)
frame_main.pack(padx=20, pady=20)
  
T = Text(frame_main, font=("Arial",15), fg = 'black', highlightthickness = 0, borderwidth=0, wrap=WORD) 
T.pack(side=LEFT)#, fill=Y)
T.insert(END,'\nDear participant\n', 'big')
quote = """
The study consists of multiple parts: a questionnaire, multiple pre-tests and the main experiment.
\nBefore each part, you will receive either written or verbal instructions by the experimenter. You can take breaks between the parts and during the main experiment.
\n\n1.Please read the participant information carefully and sign the consent form. 
\n\n2.Please fill out the questionnaire which can be opened by pressing 'Q'. 
"""
T.insert(END,quote)
endBtn = Button(win_main,padx=7, pady=10, height=1, width=8, 
    font=("Arial",15), text="Finish",command=close_fx)
endBtn.place(relx = 0.5, rely = .9, anchor = CENTER)
get_keypress()
win_main.mainloop()






