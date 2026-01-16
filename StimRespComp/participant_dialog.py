"""
participant_dialog.py
GUI dialog to collect participant info before experiment starts.
"""

import tkinter as tk
from tkinter import simpledialog


class ParticipantDialog(simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Participant Code:").grid(row=0, column=0)
        tk.Label(master, text="Session Type:").grid(row=1, column=0)
        tk.Label(master, text="rm Assignment Mode:").grid(row=2, column=0)

        self.entry_code = tk.Entry(master)
        self.entry_code.grid(row=0, column=1)

        self.session_var = tk.StringVar(value="practice")
        tk.OptionMenu(master, self.session_var, "practice", "test").grid(row=1, column=1)

        self.rm_var = tk.StringVar(value="block")
        tk.OptionMenu(master, self.rm_var, "block", "random", "A-only", "B-only").grid(row=2, column=1)

        return self.entry_code  # focus

    def apply(self):
        self.result = {
            "participant_code": self.entry_code.get(),
            "session_type": self.session_var.get(),
            "rm_mode": self.rm_var.get(),
        }
