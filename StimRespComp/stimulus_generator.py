"""
stimulus_generator.py
Creates full-factorial stimulus sets for the experiment.

You define:
- factors
- video directory structure
- how many repetitions per condition

Outputs:
- a clean list of dicts: {'condi': 'IPS', 'clip': 'path', 'rm': ...}
- ready for rm assignment and validation
"""

import os
import itertools
import numpy as np

# ---------------------------------------------------
# DEFINE FACTORS
# ---------------------------------------------------
# Factor 1: Zoom direction
ZOOM_LEVELS = ["I", "O"]

# Factor 2: Presence
PRES_LEVELS = ["P", "A"]

# Factor 3: Motion or Speed
MOTION_LEVELS = ["S", "F"]


def make_condition_code(zoom, pres, mot):
    """Returns a condi string like 'IPS'."""
    return f"{zoom}{pres}{mot}"


def generate_factorial_conditions():
    """
    Create a full factorial list like:
    ['IPS', 'IPF', 'IAS', ...]
    """
    return [
        make_condition_code(z, p, m)
        for z, p, m in itertools.product(ZOOM_LEVELS, PRES_LEVELS, MOTION_LEVELS)
    ]


# ---------------------------------------------------
# ASSIGN VIDEO FILES TO EACH CONDITION
# ---------------------------------------------------
def attach_videos_to_conditions(condi_list, video_root, n_reps=1):
    """
    Assumes your videos follow a naming scheme:
        stimuli/vidX.mp4  etc.
    OR each condition has its own folder:
        stimuli/IPS/clip1.mp4, clip2.mp4, ...
    This function works with both layouts.

    condi_list: list of condition strings
    video_root: e.g. "stimuli"
    n_reps: number of repetitions per available clip
    """
    output = []

    for condi in condi_list:
        condi_path = os.path.join(video_root, condi)

        if os.path.isdir(condi_path):
            # Directory = many clips for this condition
            files = sorted([
                os.path.join(condi_path, f)
                for f in os.listdir(condi_path)
                if f.lower().endswith((".mp4", ".avi", ".mov"))
            ])
        else:
            # Fallback if using a flat structure
            files = [
                os.path.join(video_root, f)
                for f in os.listdir(video_root)
                if f.lower().endswith((".mp4", ".avi", ".mov")) and condi in f
            ]

        if not files:
            print(f"WARNING: No files found for condi '{condi}'")

        for clip in files:
            for _ in range(n_reps):
                output.append({"condi": condi, "clip": clip})

    return output


# ---------------------------------------------------
# BLOCK COUNTERBALANCED RM ASSIGNMENT
# ---------------------------------------------------
def assign_rm(stim_list):
    stim_list = list(stim_list)
    n = len(stim_list)
    half = n // 2

    for i, stim in enumerate(stim_list):
        stim["rm"] = "A" if i < half else "B"

    np.random.shuffle(stim_list)
    return stim_list


# ---------------------------------------------------
# Full pipeline
# ---------------------------------------------------
def generate_full_stimulus_set(video_root, n_reps=1):
    condi_list = generate_factorial_conditions()
    stim_list = attach_videos_to_conditions(condi_list, video_root, n_reps)
    stim_list = assign_rm(stim_list)
    return stim_list
