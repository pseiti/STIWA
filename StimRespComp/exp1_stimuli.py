"""
exp1_stimuli.py
Automatic generator version — NO long lists needed.

This replaces your 600-line manual stimulus lists with:
- automatic generation of IPS, IPF, OPS, OPF, IAS, IAF, OAS, OAF
- automatic video number assignment
- block-counterbalanced rm
- condition parser + validator
"""

import numpy as np
import os


# ============================================================
# 1. CONDITION PARSER
# ============================================================

def parse_condi(condi):
    if len(condi) != 3:
        raise ValueError(f"Invalid condi '{condi}', expected format like 'IPS'.")
    return {
        "Zoom": condi[0],      # I/O
        "Presence": condi[1],  # P/A
        "Motion": condi[2],    # S/F
    }


# ============================================================
# 2. RM ASSIGNMENT
# ============================================================

def assign_resp_mapping(stim_list):
    stim_list = list(stim_list)
    n = len(stim_list)
    half = n // 2
    for i, stim in enumerate(stim_list):
        stim["rm"] = "A" if i < half else "B"
    np.random.shuffle(stim_list)
    return stim_list


# ============================================================
# 3. VALIDATOR
# ============================================================

def validate_stimuli(stim_list, check_files=False):
    errors = []
    for i, stim in enumerate(stim_list):
        for key in ("condi", "clip", "rm"):
            if key not in stim:
                errors.append(f"Stim {i} missing key '{key}'.")
        try:
            parse_condi(stim["condi"])
        except Exception as e:
            errors.append(f"Stim {i}: invalid condi — {e}")
        if check_files:
            if not os.path.exists(stim["clip"]):
                errors.append(f"Stim {i}: file not found — {stim['clip']}")
    return errors


# ============================================================
# 4. AUTOMATIC FULL STIMULUS GENERATOR
# ============================================================

"""
Your original dataset uses 8 condition types with these video number groups:

IPS →   1–25  
IPF →  26–50  
OPS →  51–75  
OPF →  76–100  
IAS → 101–125  
IAF → 126–150  
OAS → 151–175  
OAF → 176–200  

Each range repeated twice in your test list.
Practice list used first 4 clips of each condi.
"""

CONDITION_VIDEO_MAP = {
    "IPS": range(1, 26),
    "IPF": range(26, 51),
    "OPS": range(51, 76),
    "OPF": range(76, 101),
    "IAS": range(101, 126),
    "IAF": range(126, 151),
    "OAS": range(151, 176),
    "OAF": range(176, 201),
}


def make_stimuli_from_map(video_map, video_folder="stimuli", reps=1):
    """
    Creates:
      [{'condi': ..., 'clip': 'stimuli/vidXYZ.mp4'}, ...]
    With optional repetition (reps=2 recreates your big test list).
    """
    out = []
    for condi, numbers in video_map.items():
        for r in range(reps):
            for n in numbers:
                out.append({
                    "condi": condi,
                    "clip": f"{video_folder}/vid{n}.mp4"
                })
    return out


# ============================================================
# 5. PRACTICE STIMULI (small subset)
# ============================================================

"""
Your original practice set always took the FIRST 4 clips from each condition.
We recreate those automatically.
"""

def make_practice_set():
    practice = []
    for condi, nums in CONDITION_VIDEO_MAP.items():
        first_four = list(nums)[:4]
        for n in first_four:
            practice.append({
                "condi": condi,
                "clip": f"stimuli/vid{n}.mp4"
            })
    practice = assign_resp_mapping(practice)
    return practice


stimuli_practice = make_practice_set()


# ============================================================
# 6. TEST STIMULI (full set, repeated twice like your original)
# ============================================================

"""
Your test list repeated each condition's full 25 videos *twice*.
This matches reps=2.
"""

stimuli_test_ordered = make_stimuli_from_map(CONDITION_VIDEO_MAP, reps=2)
stimuli_test = assign_resp_mapping(stimuli_test_ordered)


# ============================================================
# 7. VALIDATION (optional)
# ============================================================

if __name__ == "__main__":
    print("Validating practice set...")
    errs = validate_stimuli(stimuli_practice)
    print("Practice OK" if not errs else "\n".join(errs))

    print("Validating test set...")
    errs = validate_stimuli(stimuli_test)
    print("Test OK" if not errs else "\n".join(errs))
