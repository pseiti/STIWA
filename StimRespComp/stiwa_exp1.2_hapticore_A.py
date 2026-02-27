import os
import random
import time
import numpy as np
import pandas as pd
import scipy.stats as st
from scipy.stats import norm
from tkinter import *
from tkVideoPlayer import TkinterVideo
from PIL import ImageTk, Image
from queue import Queue
import threading
from pynput import mouse  # <-- needed for mocking
import exp1_stimuli
from src.haptic_core_serial import *
import string

n_stimuli_practice = len(exp1_stimuli.stimuli_practice)
n_stimuli_test = len(exp1_stimuli.stimuli_test)
fwd_means_present = True

# ---------------------------
# Hapticore
# ---------------------------
ports = {'hcc1': 'COM4'}
protocol_version = '1.0'
input_queues = {hcc: Queue() for hcc in ports.keys()}
output_queues = {hcc: Queue() for hcc in ports.keys()}
set_register('tick_angle_cw', 0, output_queues['hcc1'])
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
        # return self.angle

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
        
# class MouseHapticMock:
#     def __init__(self):
#         self.angle = 0
#         self.tick_angle = 3
#         self.listener = mouse.Listener(on_scroll=self._on_scroll)
#         self.listener.start()

#     def _on_scroll(self, x, y, dx, dy):
#         self.angle += dy * self.tick_angle
        
#     def read_angle(self, device="hcc1"):
#         return self.angle

#     def set_tick_angle(self, angle): #, device="hcc1"):
#         self.tick_angle = angle

#     def stop(self):
#         self.listener.stop()

# ---------------------------
# Helper Functions
# ---------------------------

class HelperFunctions:
    def __init__(self, font="Arial", font_size=16, pad_x=10, pad_y=10,
                 ms_fixcross=1000, haptics=None):

        self.font = font
        self.font_size = font_size
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.ms_fixcross = ms_fixcross
        self.haptics = haptics

        self.cur_set_of_stimuli = []
        self.trial_index = None
        self.session_window = None
        self.label_hit_the_spacebar = None
        self.init_angle = 0 

        # threading control
        self.monitor_thread = None
        self.stop_event = None

        # 
        self.video_player = None
        self.time_vidStarted = None

        #
        self.practice = None
        self.n_stimuli = None

        self.intro_win = None
        self.instru_win = None

        self.label_feedback = None

    # --- GUI helpers ---

    def present_introduction(self, parent, title, txt):
        
        self.intro_win = Toplevel(parent)
        self.intro_win.title(title)
        self.intro_win.attributes("-fullscreen", True)
        self.intro_win.bind("<space>", self.close_intro)
        self.intro_win.attributes("-topmost", True)
        self.intro_win.focus()

        frame = Frame(self.intro_win)
        frame.pack(padx=20, pady=20)
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        message = Text(frame, font=("f",20))
        message.insert(END, INTRODUCTION)
        message.pack()
        message.config(state=DISABLED)

    def close_intro(self, event):
        self.intro_win.destroy()

    def close_instru(self, event):
        self.instru_win.destroy()

    def present_instruction(self, parent, title, txt):
        
        self.instru_win = Toplevel(parent)
        self.instru_win.title(title)
        self.instru_win.attributes("-fullscreen", True)
        self.instru_win.focus()
        self.instru_win.bind("<space>", self.close_instru)

        logo_img = Image.open("Apotheke_Logo.png").resize((50,50))
        logo_tk = ImageTk.PhotoImage(logo_img)
        img_apotheke = Label(self.instru_win, image=logo_tk)
        img_apotheke.image = logo_tk
        img_apotheke.pack()
        
        frame = Frame(self.instru_win)
        frame.pack(padx=20, pady=20)
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        message = Text(frame, font=("f",20))
        message.insert(END, INSTRUCTION)
        message.pack()
        message.config(state=DISABLED)

    def open_session_window(self, parent, title, geometry, practice_button):

        self.session_window = Toplevel(parent)
        self.session_window.title(title)
        self.session_window.geometry(geometry)

        self.trial_index = 0

        self.practice = True if practice_button else False

        if self.practice:
            self.cur_set_of_stimuli = exp1_stimuli.stimuli_practice
            self.n_stimuli = n_stimuli_practice
        else:
            self.cur_set_of_stimuli = exp1_stimuli.stimuli_test
            self.n_stimuli = n_stimuli_test

        self.label_hit_the_spacebar = Label(
            self.session_window,
            text="Hit the space bar to start the trial.",
            font=(self.font, self.font_size),
            wraplength=500,
            justify=LEFT,
        )
        self.label_hit_the_spacebar.pack(padx=self.pad_x, pady=self.pad_y)

        self.session_window.bind("<space>", self.starttrial_by_spacebar)

    def bind_spacebar(self):
        
        self.label_hit_the_spacebar = Label(
            self.session_window,
            text="Hit the space bar to start the trial.",
            font=(self.font, self.font_size),
            wraplength=500,
            justify=LEFT
        )

        if self.label_feedback is not None:
            self.label_feedback.destroy()
            self.label_feedback = None

        self.label_hit_the_spacebar.pack(padx=self.pad_x, pady=self.pad_y)
        self.session_window.bind("<space>", self.starttrial_by_spacebar)

    # def fixation_cross(self, t_show, t_remove):
        
    #     def show_label(lbl):
    #         lbl.pack()

    #     def remove_label(lbl):
    #         lbl.destroy()

    #     label_fixation_cross = Label(self.session_window, text="\n\n+", font=("Arial", 40))
    #     self.session_window.after(t_show, show_label, label_fixation_cross)
    #     self.session_window.after(t_remove, remove_label, label_fixation_cross)
    
    def starttrial_by_spacebar(self, event):
        
        self.label_hit_the_spacebar.destroy()
        self.label_hit_the_spacebar = None
        self.session_window.unbind("<space>")

        condition = self.cur_set_of_stimuli[self.trial_index].get("condi")
        #print(self.cur_set_of_stimuli[self.trial_index])
        if fwd_means_present:
            condition = "F" + condition
        else:
            condition = "B" + condition

        self.session_window.after(
            self.ms_fixcross * 1,
            self.playVideo,
            self.cur_set_of_stimuli[self.trial_index].get("clip"),
            condition
        )

    def playVideo(self, vid_x, condition):
        
        # self.haptics = MouseHapticMock()
        self.haptics = Hapticore({"hcc1": "COM3"}) # Initialize Hapticore
        # self.haptics.set_tick_angle(3)
        # Erstellen und Laden eines neuen Videoplayers
        
        if self.trial_index == 0:
                self.video_player = TkinterVideo(self.session_window)
        self.video_player.pack(expand=True, fill="both")
        self.video_player.load(vid_x)
        self.video_player.play()

        self.time_vidStarted = time.time()

        self.stop_event = threading.Event()
        self.init_angle = self.haptics.read_angle()
        self.monitor_thread = threading.Thread(
            target=self.monitor_haptic_input,
            args=(self.init_angle,
                  self.stop_event,
                  condition),
            daemon=True
        )
        # Start monitoring input from Hapticore respectively mousewheel
        self.monitor_thread.start()

        def on_close():
            self.stop_event.set()
            self.session_window.destroy()

        self.session_window.protocol("WM_DELETE_WINDOW", on_close)

    # --- Core utilities ---
    # def application_tick_mockup(self, init_angle):
    #     if not self.haptics:
    #         return None, None
    #     current = self.haptics.read_angle()
    #     diff = current - init_angle
    #     # print("application_tick()")
    #     # print(init_angle, current, diff)
    #     # print()
    #     return current, diff

    def application_tick(self, init_angle):
        if not self.haptics:
            return None, None
        current = self.haptics.read_angle()
        # diff = current - init_angle
        diff = (current - init_angle + 540) % 360 - 180
        # current_multiturn = self.haptics.read_multiturn()
        # if current_multiturn != self.prev_multiTurn:
        #     print("one up")
        #     self.prev_multiTurn += 1

        # print(f"Current angle: {current: .2f}, Diff: {diff:.2f}")
        return current, diff

    def monitor_haptic_input(self, init_angle_local, stop_event, condition):

        while not stop_event.is_set():
            angle, diff = self.application_tick(init_angle_local)
            if angle is None:
                time.sleep(0.05)
                continue
            
            # Hapticore-triggered response
            if abs(diff) > 3:
                
                if diff > 0:
                    scrolling_direction = "Fwd"
                    scroll_forward = True
                else:
                    scrolling_direction = "Bwd"
                    scroll_forward = False

                RT = time.time() - self.time_vidStarted 
                stop_event.set()
                self.video_player.pack_forget()
                
                # Other variable than RT
                self.haptics.stop()
                
                 # update angle and trial index
                # self.init_angle = self.haptics.read_angle() # 0 # self.haptics.read_angle()
                self.trial_index += 1

                target_present = True if condition[2] == "P" else False
                # scroll_forward = True if diff > 0 else False
                # scrolling_direction = "Fwd" if diff > 0 else "Bwd"
                

                resp_cat = self.sdt_resp_cat(
                    target_present, scroll_forward, fwd_means_present
                )
                df.loc[len(df.index)] = [
                    person_code, self.practice, self.trial_index, condition, scrolling_direction, resp_cat, RT
                ]
                print(df)

                if resp_cat=="FA" or resp_cat=="Miss":
                    self.label_feedback = Label(self.session_window, text=resp_cat)
                    self.label_feedback.pack()

                if self.trial_index == self.n_stimuli:
                    performance_measures = self.performance_measures(df)
                    hitRate, faRate, percentError, dPrime = performance_measures
                    self.haptics.stop()
                    if self.practice:
                        Label(
                            self.session_window,
                            text="\n\nPractice part completed, thank you."+
                            "\n\nPercent correct (error-corrected): "+
                             str(round(percentError,2)) +
                             "\n\ndPrime: "+
                             str(round(dPrime,2)),
                            font=(self.font, self.font_size),
                            wraplength=500,
                            justify=LEFT,
                        ).pack(padx=self.pad_x, pady=self.pad_y)

                        # self.session_window.after(5000, self.session_window.destroy)
                    else:
                        Label(
                            self.session_window,
                            text="\n\nThank you for your efforts and your time, test part competed too."+
                            "\n\nPercent correct (error-corrected): "+
                             str(round(percentError,2)) +
                             "\n\ndPrime: "+
                             str(round(dPrime,2)),
                            font=(self.font, self.font_size),
                            wraplength=500,
                            justify=LEFT,
                        ).pack(padx=self.pad_x, pady=self.pad_y)
                    df.to_csv(person_code + "_SRC_exp12_A.csv", index=False)

                else:
                    self.session_window.after(
                        self.ms_fixcross,
                        self.bind_spacebar
                    )

            time.sleep(0.05)

    def stop_threads(self):
        if self.stop_event:
            self.stop_event.set()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        if self.haptics:
            self.haptics.stop()

    def sdt_resp_cat(self, target_present, scroll_forward, fwd_means_present):
        if fwd_means_present:
            if target_present:
                return "Hit" if scroll_forward else "Miss"
            else:
                return "FA" if scroll_forward else "CR"
        else:
            if target_present:
                return "Miss" if scroll_forward else "Hit"
            else:
                return "CR" if scroll_forward else "FA"

    def performance_measures(self, df):
        nHits = len(df[df['sdt_resp_cat'] == 'Hit'])
        nMiss = len(df[df['sdt_resp_cat'] == 'Miss'])
        nCR = len(df[df['sdt_resp_cat'] == 'CR'])
        nFA = len(df[df['sdt_resp_cat'] == 'FA'])

        if nHits == 0:
            hitRate = 1 / np.sqrt(400)
        else:
            hitRate = nHits / (nHits + nMiss)
        if hitRate == 1:
            hitRate = 1 - 1 / np.sqrt(400)

        if nFA == 0:
            faRate = 1 / np.sqrt(400)
        else:
            faRate = nFA / (nCR + nFA)
        if faRate == 1:
            faRate = 1 - 1 / np.sqrt(400)

        dPrime = st.norm.ppf(hitRate) - st.norm.ppf(faRate)
        percentErrorCorrected = hitRate - faRate
        return [hitRate, faRate, percentErrorCorrected, dPrime]


class ScreeningWindow:
    def __init__(self, parent, on_done=None):
        self.parent = parent
        self.on_done = on_done
        self.data = {}

        self.win = Toplevel(parent)
        self.win.title("Kurzscreening – Visuelle Voraussetzungen")
        self.win.geometry("600x700+200+50")
        self.win.attributes("-topmost", True)

        self._build_ui()

    def _build_ui(self):
        # --- Scrollable container ---
        container = Frame(self.win)
        container.pack(fill="both", expand=True)

        canvas = Canvas(container, borderwidth=0)
        scrollbar = Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mousewheel support
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)      # Windows
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

        f = self.scrollable_frame

        # --- Content ---
        Label(f, text="Kurzscreening – Visuelle Voraussetzungen", font=("Arial", 18, "bold")).pack(anchor="w", pady=(10, 10))

        # 1a
        Label(f, text="1a) Tragen Sie normalerweise eine Sehhilfe?").pack(anchor="w")
        self.vision_aid = StringVar(value="__none__")
        for txt in ["Nein", "Brille", "Kontaktlinsen"]:
            Radiobutton(f, text=txt, variable=self.vision_aid, value=txt).pack(anchor="w")

        # 1b
        Label(f, text="1b) Tragen Sie Ihre Sehhilfe aktuell?").pack(anchor="w", pady=(10, 0))
        self.vision_aid_now = StringVar(value="__none__")
        for txt in ["Nein", "Ja"]:
            Radiobutton(f, text=txt, variable=self.vision_aid_now, value=txt).pack(anchor="w")

        # 2
        Label(f, text="2) Wie gut ist Ihr Sehen aktuell? (1 = sehr schlecht, 7 = sehr gut)").pack(anchor="w", pady=(10, 0))
        self.vision_quality = IntVar(value=4)
        Scale(f, from_=1, to=7, orient=HORIZONTAL, variable=self.vision_quality).pack(fill="x")

        # 3
        Label(f, text="3) Haben Sie bekannte Augenerkrankungen?").pack(anchor="w", pady=(10, 0))
        self.eye_conditions = StringVar(value="__none__")
        for txt in ["Nein", "Ja"]:
            Radiobutton(f, text=txt, variable=self.eye_conditions, value=txt).pack(anchor="w")

        Label(f, text="Falls ja, welche?").pack(anchor="w")
        self.eye_conditions_text = Entry(f)
        self.eye_conditions_text.pack(fill="x")

        # 4
        Label(f, text="4) Wann war Ihr letzter Sehtest?").pack(anchor="w", pady=(10, 0))
        self.last_test = StringVar(value="__none__")
        for txt in ["< 12 Monate", "1–3 Jahre", "> 3 Jahre", "weiß ich nicht / nie"]:
            Radiobutton(f, text=txt, variable=self.last_test, value=txt).pack(anchor="w")

        # 5
        Label(f, text="5) Ist Ihnen eine Farbsehschwäche bekannt?").pack(anchor="w", pady=(10, 0))
        self.color_vision = StringVar(value="__none__")
        for txt in ["Nein", "Ja", "Weiß ich nicht"]:
            Radiobutton(f, text=txt, variable=self.color_vision, value=txt).pack(anchor="w")

        # 6
        Label(f, text="6) Wie müde fühlen Sie sich aktuell? (1 = sehr wach, 9 = sehr schläfrig)").pack(anchor="w", pady=(10, 0))
        self.sleepiness = IntVar(value=5)
        Scale(f, from_=1, to=9, orient=HORIZONTAL, variable=self.sleepiness).pack(fill="x")

        Button(f, text="Weiter", font=("Arial", 14), command=self.submit).pack(pady=20)

    def submit(self):
        if not all([
            self.vision_aid.get(),
            self.vision_aid_now.get(),
            self.eye_conditions.get(),
            self.last_test.get(),
            self.color_vision.get()
        ]):
            from tkinter import messagebox
            messagebox.showerror("Fehlende Angaben", "Bitte beantworten Sie alle Pflichtfragen.")
            return

        self.data = {
            "vision_aid": self.vision_aid.get(),
            "vision_aid_now": self.vision_aid_now.get(),
            "vision_quality": self.vision_quality.get(),
            "eye_conditions": self.eye_conditions.get(),
            "eye_conditions_text": self.eye_conditions_text.get(),
            "last_test": self.last_test.get(),
            "color_vision": self.color_vision.get(),
            "sleepiness_kss": self.sleepiness.get()
        }

        if self.on_done:
            self.on_done(self.data)

        self.win.destroy()
# ---------------------------
# Main GUI
# ---------------------------

# ---------------------------
# Instruction text
# ---------------------------
INTRODUCTION = """
You are invited to participate in the study AllgBioPsych_24WS_Effects 
    of spatiotemporal coding compatibilities in visual search.

Rights: If you have any questions concerning this study (e.g., aim, 
    procedure), you can ask the experimenter at any time before or during
    the experiment. After you completed the study, you will be provided 
    with comprehensive information. If requested, you will be provided 
    with the results of the experiment after the study is completed. 
    You are free to withdraw at any time, without giving a reason and
    without cost. 

Privacy statement: All information you provide will remain confidential 
    and will not be associated with your name. For reasons of scientific
    transparency, the de-identified data may be shared publicly for
    further use (open science). The data collected as part of this
    study may be published in a scientific journal.

Compensation: Your participation will be compensated by LABS credits.

Press space bar to close the window.  
"""


INSTRUCTION = """
    It follows a sequence of """ + str(len(exp1_stimuli.stimuli_test)) + """ trials, which are short video clips.
    Each clip shows a moving map that is simultaneously zoomed in or out.
    The clips differ in whether or not the so-called target object
    -- a pharmacy symbol, as displayed above --
    appears or does not appear at some point during zooming.

    Your task is to indicate the presence or absence of the 
    target by scrolling the mouse wheel forward (towards the screen) or 
    backward (away from the screen).

    Before the actual test phase with its """ + str(len(exp1_stimuli.stimuli_test)) + """ trials starts, 
    you go through a brief, self-paced sequence of practice trials, 
    which is completed as soon as your accuracy level certifies you a 
    sufficiently accurate response behavior.

    Please consider, the level of accuracy is determined by comparing 
    your hits (trials, where the target is present and you 'hit' the right mouse wheel direction) 
    against your false alarms (trials, where the target is absent but you falsely indicate its presence). 

    Try to be as fast and accurate as you can!

    Press space bar to close the window.
"""

# if compatibility=="C":
#     instr_Procedure_and_Task_2 = """
# Your task is to indicate the presence or absence of the 
# target by scrolling the mouse wheel forward (towards the 
# screen) or backward (away from the screen)."""
# elif compatibility=="I":
#     instr_Procedure_and_Task_2 = """
# Your task is to indicate the presence or absence of the 
# target by scrolling the mouse wheel backward (away from 
# the screen) or forward (towards the screen)."""


DEFAULT_FONT = ("Arial", 16)
helper = HelperFunctions(*DEFAULT_FONT, haptics=None)

columns = ["person_code","practice","i" , "condition", "scrolling_direction", "sdt_resp_cat", "RT"]
df = pd.DataFrame(columns=columns)

def generate_person_code(n_letters=4, n_digits=3):
    letters = random.sample(string.ascii_uppercase, n_letters)
    digits = random.sample("0123456789", n_digits)
    return "".join(letters) + "".join(digits)

person_code = generate_person_code()

print("\nPersonencode:", person_code, "\n")

# zooming_direction = "Z"

root = Tk()
root.title("FFG-STIWA, Experiment 1.2")
root.geometry("400x600+50+30")

Label(
    root,
    text="""...
""",
    font=DEFAULT_FONT
).pack(pady=20)

# self, parent, txt, geometry

screening_data = {}

def start_screening():
    def on_screening_done(data):
        global screening_data
        screening_data.update(data)
        print("Screening-Daten:", screening_data)

        # optional: direkt an df anhängen oder eigene CSV
        screening_row = {"person_code": person_code, **screening_data}
        pd.DataFrame([screening_row]).to_csv(person_code + "_screening.csv", index=False)

        # btn_practice.config(state=NORMAL)
        # btn_test.config(state=NORMAL)

    ScreeningWindow(root, on_done=on_screening_done)

Button(
    root,
    text="Introduction",
    font=DEFAULT_FONT,
    command=lambda: helper.present_introduction(
        root, "Introduction", INTRODUCTION)
).pack(pady=10)

Button(
    root,
    text="Screening",
    font=DEFAULT_FONT,
    command=start_screening
).pack(pady=10)

Button(
    root,
    text="Instruction",
    font=DEFAULT_FONT,
    command=lambda: helper.present_instruction(
        root, "Instruction", INSTRUCTION)
).pack(pady=10)

Button(
    root,
    text="Start Practice",
    font=DEFAULT_FONT,
    command=lambda: helper.open_session_window(
        root, "Practice Session", "600x400+500+50", True)
).pack(pady=10)

Button(
    root,
    text="Start Test Session",
    font=DEFAULT_FONT,
    command=lambda: helper.open_session_window(
        root, "Test Session", "600x400+500+50", False)
).pack(pady=10)

# Button(
#     root,
#     text="Close",
#     font=DEFAULT_FONT,
#     command=lambda: (helper.stop_threads(), root.destroy())
# ).pack(pady=10)

root.title(f"FFG-STIWA, Experiment 1.2 – {person_code}")
root.mainloop()
