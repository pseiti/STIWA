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

# ---------------------------
# Hapticore
# ---------------------------
ports = {'hcc1': 'COM4'}
protocol_version = '1.0'
class Hapticore:
    #def __init__(self):
    #    self.listener

    def application_tick(self, init_angle):
        cur_angle = get_register('report_encoder_angle', output_queues['hcc1'], input_queues['hcc1'])
        diff_to_init = cur_angle - init_angle
        return [cur_angle, diff_to_init]
        
class MouseHapticMock:
    def __init__(self):
        self.angle = 0
        self.tick_angle = 3
        self.listener = mouse.Listener(on_scroll=self._on_scroll)
        self.listener.start()

    def _on_scroll(self, x, y, dx, dy):
        self.angle += dy * self.tick_angle
        
    def read_angle(self, device="hcc1"):
        return self.angle

    def set_tick_angle(self, angle, device="hcc1"):
        self.tick_angle = angle

    def stop(self):
        self.listener.stop()


# Initialize mock haptic system
haptics = MouseHapticMock()
haptics.set_tick_angle(3)


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
        self.init_angle = self.haptics.read_angle() if haptics else 0

        # threading control
        self.monitor_thread = None
        self.stop_event = None

        # 
        self.video_player = None
        self.time_vidStarted = None

        #
        self.practice = None
        self.n_stimuli = None

    # --- GUI helpers ---

    def open_text_window(self, parent, title, txt1, txt2, txt3, geometry):
        
        window = Toplevel(parent)
        window.title(title)
        window.geometry(geometry)
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

    def open_session_window(self, parent, title, geometry, practice_button):

        self.session_window = Toplevel(parent)
        self.session_window.title(title)
        self.session_window.geometry(geometry)

        self.trial_index = 0

        self.practice = True if practice_button else False

        if self.practice:
            self.cur_set_of_stimuli = exp1_stimuli.stimuli_practice
            self.n_stimuli = 3
        else:
            self.cur_set_of_stimuli = exp1_stimuli.stimuli_test
            self.n_stimuli = 9

        self.label_hit_the_spacebar = Label(
            self.session_window,
            text="Hit the space bar to start the trial.",
            font=(self.font, self.font_size),
            wraplength=500,
            justify=LEFT,
        )
        self.label_hit_the_spacebar.pack(padx=self.pad_x, pady=self.pad_y)

        self.session_window.bind("<space>", self.starttrial_by_spacebar)

    def starttrial_by_spacebar(self, event):
        
        self.label_hit_the_spacebar.destroy()
        self.label_hit_the_spacebar = None
        self.session_window.unbind("<space>")

        condition = self.cur_set_of_stimuli[self.trial_index].get("condi")
        condition = zooming_direction + condition

        self.session_window.after(
            self.ms_fixcross * 1,
            self.playVideo,
            self.cur_set_of_stimuli[self.trial_index].get("clip"),
            condition
        )

    def bind_spacebar(self):
        
        self.label_hit_the_spacebar = Label(
            self.session_window,
            text="Hit the space bar to start the trial.",
            font=(self.font, self.font_size),
            wraplength=500,
            justify=LEFT
        )
        self.label_hit_the_spacebar.pack(padx=self.pad_x, pady=self.pad_y)
        self.session_window.bind("<space>", self.starttrial_by_spacebar)

    def fixation_cross(self):
        def show_label(lbl):
            lbl.pack()

        def remove_label(lbl):
            lbl.destroy()

        label_fixation_cross = Label(self.session_window, text="\n\n+", font=("Arial", 40))
        self.session_window.after(self.ms_fixcross, show_label, label_fixation_cross)
        self.session_window.after(self.ms_fixcross * 2, remove_label, label_fixation_cross)

    def playVideo(self, vid_x, condition):
        
        self.haptics = MouseHapticMock()
        self.haptics.set_tick_angle(3)
            # print("read_angle: " + str(self.haptics.read_angle()))
            # print("init_angle: " + str(self.init_angle))

        # Erstellen und Laden eines neuen Videoplayers
        if self.trial_index == 0:
                self.video_player = TkinterVideo(self.session_window)
        self.video_player.pack(expand=True, fill="both")
        self.video_player.load(vid_x)
        self.video_player.play()

        self.time_vidStarted = time.time()

        self.stop_event = threading.Event()
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
            self.init_angle = self.haptics.read_angle()
            self.stop_event.set()
            self.session_window.destroy()

        self.session_window.protocol("WM_DELETE_WINDOW", on_close)

    # --- Core utilities ---
    def application_tick(self, init_angle):
        if not self.haptics:
            return None, None
        current = self.haptics.read_angle()
        diff = current - init_angle
        # print("application_tick()")
        # print(init_angle, current, diff)
        # print()
        return current, diff

    def monitor_haptic_input(self, init_angle_local, stop_event, condition):

        while not stop_event.is_set():

            angle, diff = self.application_tick(init_angle_local)

            if angle is None:

                time.sleep(0.05)
                continue
            
            # Mouse-triggered response
            if abs(diff) > 3:
                
                RT = time.time() - self.time_vidStarted
                self.video_player.pack_forget()
                # Other variable than RT
                stop_event.set()
                self.haptics.stop()
                
                 # update angle and trial index
                self.init_angle = 0 # self.haptics.read_angle()
                self.trial_index += 1

                target_present = True if condition[2] == "P" else False
                scroll_forward = True if diff > 0 else False
                scrolling_direction = "Fwd" if diff > 0 else "Bwd"
                fwd_means_present = True

                resp_cat = self.sdt_resp_cat(
                    target_present, scroll_forward, fwd_means_present
                )

                df.loc[len(df.index)] = [
                    self.practice, self.trial_index, cur_code, condition, scrolling_direction, resp_cat, RT
                ]
                print(df)

                if self.trial_index == self.n_stimuli:
                    performance_measures = self.performance_measures(df)
                    hitRate, faRate, percentError, dPrime = performance_measures

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
                    df.to_csv(cur_code + "_SRC_exp12.csv")

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


# ---------------------------
# Main GUI
# ---------------------------

# ---------------------------
# Instruction text
# ---------------------------
compatibility = "C"

instr_Procedure_and_Task_1 = """
It follows a sequence of """ + str(len(exp1_stimuli.stimuli_test)) + """ trials, which are short video clips.
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
#logo_apotheke = ImageTk.PhotoImage(logo_apotheke)
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
Before the actual test phase with its """ + str(len(exp1_stimuli.stimuli_test)) + """ trials starts, 
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



DEFAULT_FONT = ("Arial", 16)
helper = HelperFunctions(*DEFAULT_FONT, haptics=haptics)

columns = ["practice","i" ,"code", "condition", "scrolling_direction", "sdt_resp_cat", "RT"]
df = pd.DataFrame(columns=columns)

letters = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
cur_code_letters = random.sample(letters,4)
cur_code_numbers = str(random.sample(range(0,10),3))
cur_code = cur_code_letters
cur_code = "".join(cur_code)
print()
# cur_code = "pcs"
print("cur_code: ", cur_code)
print()
zooming_direction = "Z"

root = Tk()
root.title("FFG-STIWA, Experiment 1.2")
root.geometry("400x400+50+150")

Label(
    root,
    text="""Please click on the instructions button
and read the information carefully!
""",
    font=DEFAULT_FONT
).pack(pady=20)

Button(
    root,
    text="Instruction",
    font=DEFAULT_FONT,
    command=lambda: helper.open_text_window(
        root, "Instruction", "...", "600x400+500+50")
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

Button(
    root,
    text="Close",
    font=DEFAULT_FONT,
    command=lambda: (helper.stop_threads(), root.destroy())
).pack(pady=10)

root.mainloop()
