import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime

class ScreeningApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Visuelles Kurzscreening")
        self.geometry("650x700")

        self.create_widgets()

    def create_widgets(self):
        container = ttk.Frame(self, padding=10)
        container.pack(fill="both", expand=True)

        title = ttk.Label(container, text="Kurzscreening – Visuelle Voraussetzungen", font=("Arial", 14, "bold"))
        title.pack(pady=10)

        # 1a) Sehhilfe
        ttk.Label(container, text="1a) Tragen Sie normalerweise eine Sehhilfe?").pack(anchor="w")
        self.vision_aid = tk.StringVar(value="")
        for text in ["Nein", "Brille", "Kontaktlinsen"]:
            ttk.Radiobutton(container, text=text, value=text, variable=self.vision_aid).pack(anchor="w")

        # 1b) Sehhilfe aktuell getragen
        ttk.Label(container, text="1b) Tragen Sie Ihre Sehhilfe aktuell?").pack(anchor="w", pady=(10, 0))
        self.vision_aid_now = tk.StringVar(value="")
        for text in ["Nein", "Ja"]:
            ttk.Radiobutton(container, text=text, value=text, variable=self.vision_aid_now).pack(anchor="w")

        # 2) Subjektive Sehqualität
        ttk.Label(container, text="2) Wie gut ist Ihr Sehen aktuell? (1 = sehr schlecht, 7 = sehr gut)").pack(anchor="w", pady=(10, 0))
        self.vision_quality = tk.IntVar(value=4)
        ttk.Scale(container, from_=1, to=7, orient="horizontal", variable=self.vision_quality).pack(fill="x")

        # 3) Augenerkrankungen
        ttk.Label(container, text="3) Haben Sie bekannte Augenerkrankungen?").pack(anchor="w", pady=(10, 0))
        self.eye_conditions = tk.StringVar(value="")
        for text in ["Nein", "Ja"]:
            ttk.Radiobutton(container, text=text, value=text, variable=self.eye_conditions).pack(anchor="w")

        ttk.Label(container, text="Falls ja, welche?").pack(anchor="w")
        self.eye_conditions_text = ttk.Entry(container)
        self.eye_conditions_text.pack(fill="x")

        # 4) Letzter Sehtest
        ttk.Label(container, text="4) Wann war Ihr letzter Sehtest?").pack(anchor="w", pady=(10, 0))
        self.last_test = tk.StringVar(value="")
        for text in ["< 12 Monate", "1–3 Jahre", "> 3 Jahre", "weiß ich nicht / nie"]:
            ttk.Radiobutton(container, text=text, value=text, variable=self.last_test).pack(anchor="w")

        # 5) Farbensehen
        ttk.Label(container, text="5) Ist Ihnen eine Farbsehschwäche bekannt?").pack(anchor="w", pady=(10, 0))
        self.color_vision = tk.StringVar(value="")
        for text in ["Nein", "Ja", "Weiß ich nicht"]:
            ttk.Radiobutton(container, text=text, value=text, variable=self.color_vision).pack(anchor="w")

        # 6) Müdigkeit (KSS)
        ttk.Label(container, text="6) Wie müde fühlen Sie sich aktuell? (1 = sehr wach, 9 = sehr schläfrig)").pack(anchor="w", pady=(10, 0))
        self.sleepiness = tk.IntVar(value=5)
        ttk.Scale(container, from_=1, to=9, orient="horizontal", variable=self.sleepiness).pack(fill="x")

        # Submit
        ttk.Button(container, text="Absenden", command=self.submit).pack(pady=20)

    def submit(self):
        if not all([
            self.vision_aid.get(),
            self.vision_aid_now.get(),
            self.eye_conditions.get(),
            self.last_test.get(),
            self.color_vision.get()
        ]):
            messagebox.showerror("Fehler", "Bitte beantworten Sie alle Pflichtfragen.")
            return

        data = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "vision_aid": self.vision_aid.get(),
            "vision_aid_now": self.vision_aid_now.get(),
            "vision_quality": int(self.vision_quality.get()),
            "eye_conditions": self.eye_conditions.get(),
            "eye_conditions_text": self.eye_conditions_text.get(),
            "last_test": self.last_test.get(),
            "color_vision": self.color_vision.get(),
            "sleepiness_kss": int(self.sleepiness.get())
        }

        file_exists = False
        try:
            with open("screening_results.csv", "r", newline="", encoding="utf-8"):
                file_exists = True
        except FileNotFoundError:
            file_exists = False

        with open("screening_results.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

        messagebox.showinfo("Danke!", "Ihre Antworten wurden gespeichert.")
        self.destroy()

if __name__ == "__main__":
    app = ScreeningApp()
    app.mainloop()