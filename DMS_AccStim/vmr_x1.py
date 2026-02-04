"""
Simplified-but-conceptually-identical VMR implementation.

Core ideas preserved:
- Distributed Poisson coding for frequency (F layer) and context (C layer)
- TCM-style nonlinear context drift (rho update)
- Bidirectional Hebbian memory (context↔feature), implemented as low-rank
  sums over bound events rather than explicit large matrices
- Question-prompt based retrieval
- Turning-point-based decision rule on the final context trajectory

The math follows the specification given in the previous explanation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

import numpy as np
from scipy.stats import poisson
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# 1. Experiment configuration and empirical data
# ---------------------------------------------------------------------------

@dataclass
class ExperimentConfig:
    # Feature ranges
    Hz_range_min: int = 1
    Hz_range_max: int = 300
    Temp_range_min: int = 1
    Temp_range_max: int = 600
    Temp_step: int = 60

    # Temporal scalars (means for context Poisson distributions)
    Temp_scalar: np.ndarray = field(default_factory=lambda: np.array([50, 250, 450]))
    AS1_ms: float = 50.0
    AS2_ms: float = 250.0

    # Number of samples per participant in empirical data
    N_sample: int = 25

    # These will be filled in __post_init__
    F_features: np.ndarray = field(init=False)
    C_features: np.ndarray = field(init=False)
    conditions: Dict[str, Tuple[int, int, int]] = field(init=False)
    main_condi_names: List[str] = field(init=False)
    sub_condi_names: List[str] = field(init=False)
    p_correct_emp_dict: Dict[str, Tuple[float, float]] = field(init=False)
    p_correct_emp_Means: np.ndarray = field(init=False)
    p_correct_emp_SDs: np.ndarray = field(init=False)
    p_correct_emp_SEMs: np.ndarray = field(init=False)

    def __post_init__(self):
        # Feature axes
        self.F_features = np.arange(self.Hz_range_min, self.Hz_range_max, 1)
        self.C_features = np.arange(self.Temp_range_min, self.Temp_range_max, self.Temp_step)

        # 48 subconditions: (f1, f2, fP)
        self.conditions = {
            "S_low_111_1":[82,132,82],"S_low_111_2":[132,82,132],"S_low_111_3":[70,112,70],
            "S_low_111_4":[112,70,112],"S_low_111_5":[96,154,96],"S_low_111_6":[154,96,154],
            "S_low_211_1":[82,132,132],"S_low_211_2":[132,82,82],"S_low_211_3":[70,112,112],
            "S_low_211_4":[112,70,70],"S_low_211_5":[96,154,154],"S_low_211_6":[154,96,96],
            "S_low_112_1":[82,132,82],"S_low_112_2":[132,82,132],"S_low_112_3":[70,112,70],
            "S_low_112_4":[112,70,112],"S_low_112_5":[96,154,96],"S_low_112_6":[154,96,154],
            "S_low_212_1":[82,132,132],"S_low_212_2":[132,82,82],"S_low_212_3":[70,112,112],
            "S_low_212_4":[112,70,70],"S_low_212_5":[96,154,154],"S_low_212_6":[154,96,96],

            "S_low_121_1":[82,132,82],"S_low_121_2":[132,82,132],"S_low_121_3":[70,112,70],
            "S_low_121_4":[112,70,112],"S_low_121_5":[96,154,96],"S_low_121_6":[154,96,154],
            "S_low_221_1":[82,132,132],"S_low_221_2":[132,82,82],"S_low_221_3":[70,112,112],
            "S_low_221_4":[112,70,70],"S_low_221_5":[96,154,154],"S_low_221_6":[154,96,96],
            "S_low_122_1":[82,132,82],"S_low_122_2":[132,82,132],"S_low_122_3":[70,112,70],
            "S_low_122_4":[112,70,112],"S_low_122_5":[96,154,96],"S_low_122_6":[154,96,154],
            "S_low_222_1":[82,132,132],"S_low_222_2":[132,82,82],"S_low_222_3":[70,112,112],
            "S_low_222_4":[112,70,70],"S_low_222_5":[96,154,154],"S_low_222_6":[154,96,96],

            "S_high_111_1":[82,112,82],"S_high_111_2":[112,82,112],"S_high_111_3":[70,96,70],
            "S_high_111_4":[96,70,96],"S_high_111_5":[96,132,96],"S_high_111_6":[132,96,132],
            "S_high_211_1":[82,112,112],"S_high_211_2":[112,82,82],"S_high_211_3":[70,96,96],
            "S_high_211_4":[96,70,70],"S_high_211_5":[96,132,132],"S_high_211_6":[132,96,96],
            "S_high_112_1":[82,112,82],"S_high_112_2":[112,82,112],"S_high_112_3":[70,96,70],
            "S_high_112_4":[96,70,96],"S_high_112_5":[96,132,96],"S_high_112_6":[132,96,132],
            "S_high_212_1":[82,112,112],"S_high_212_2":[112,82,82],"S_high_212_3":[70,96,96],
            "S_high_212_4":[96,70,70],"S_high_212_5":[96,132,132],"S_high_212_6":[132,96,96],

            "S_high_121_1":[82,112,82],"S_high_121_2":[112,82,112],"S_high_121_3":[70,96,70],
            "S_high_121_4":[96,70,96],"S_high_121_5":[96,132,96],"S_high_121_6":[132,96,132],
            "S_high_221_1":[82,112,112],"S_high_221_2":[112,82,82],"S_high_221_3":[70,96,96],
            "S_high_221_4":[96,70,70],"S_high_221_5":[96,132,132],"S_high_221_6":[132,96,96],
            "S_high_122_1":[82,112,82],"S_high_122_2":[112,82,112],"S_high_122_3":[70,96,70],
            "S_high_122_4":[96,70,96],"S_high_122_5":[96,132,96],"S_high_122_6":[132,96,132],
            "S_high_222_1":[82,112,112],"S_high_222_2":[112,82,82],"S_high_222_3":[70,96,96],
            "S_high_222_4":[96,70,70],"S_high_222_5":[96,132,132],"S_high_222_6":[132,96,96]
        }

        self.main_condi_names = [
            "S_low_111","S_low_121","S_low_112","S_low_122",
            "S_low_211","S_low_212","S_low_221","S_low_222",
            "S_high_111","S_high_121","S_high_112","S_high_122",
            "S_high_211","S_high_212","S_high_221","S_high_222"
        ]
        self.sub_condi_names = list(self.conditions.keys())

        # Empirical means and SDs
        self.p_correct_emp_dict = {
            "S_low_111":[0.7463768,0.3028235],
            "S_low_121":[0.7789855,0.2422303],
            "S_low_112":[0.7016908,0.3652845],
            "S_low_122":[0.7355072,0.3368782],
            "S_low_211":[0.7403382,0.3069994],
            "S_low_212":[0.8429952,0.1594852],
            "S_low_221":[0.7234300,0.2611807],
            "S_low_222":[0.8405797,0.1635263],
            "S_high_111":[0.6207729,0.3027429],
            "S_high_121":[0.6690821,0.3063480],
            "S_high_112":[0.3973430,0.4568529],
            "S_high_122":[0.4118357,0.4805893],
            "S_high_211":[0.5326087,0.3518283],
            "S_high_212":[0.8369565,0.1953989],
            "S_high_221":[0.4589372,0.4473445],
            "S_high_222":[0.7801932,0.2441678]
        }
        values = list(self.p_correct_emp_dict.values())
        self.p_correct_emp_Means = np.array([v[0] for v in values])
        self.p_correct_emp_SDs   = np.array([v[1] for v in values])
        self.p_correct_emp_SEMs  = self.p_correct_emp_SDs / np.sqrt(self.N_sample)


# ---------------------------------------------------------------------------
# 2. Utility functions (normalization, rho, turning points)
# ---------------------------------------------------------------------------

def l2_normalize(v: np.ndarray) -> np.ndarray:
    s = np.sum(v * v)
    if s <= 0:
        return v
    return v / np.sqrt(s)


def rho_fx(c_prev: np.ndarray, cIN: np.ndarray, beta: float) -> float:
    """
    TCM-style context drift coefficient rho(beta, <c_prev, cIN>).
    Directly mirrors the original math.
    """
    u = float(np.dot(c_prev, cIN))
    comp1_1 = u*u - 1.0
    comp1 = np.sqrt(1.0 + (beta**2) * comp1_1)
    comp2 = beta * u
    return comp1 - comp2


def turning_points(c: np.ndarray) -> List[int]:
    """
    Turning-point detection as in the original code:
    track changes between increasing/decreasing.
    """
    increasing = True
    positions: List[int] = []
    for x in range(1, len(c)-1):
        if c[x] < c[x+1]:
            if not increasing:
                increasing = True
                positions.append(x)
        elif c[x] > c[x+1]:
            if increasing:
                increasing = False
                positions.append(x)
    return positions


def p_correct_from_context(c: np.ndarray) -> float:
    """
    Apply the turning point + density rule to final context c.
    Returns p_correct, or 10.0 if too few turning points (penalty).
    """
    positions = turning_points(c)
    if len(positions) < 5:
        return 10.0  # same penalty as original

    densities = [0.0, 0.0, 0.0]
    for x in range(len(c)-1):
        if x < positions[1]:
            densities[0] += c[x]
        elif positions[1] <= x < positions[3]:
            densities[1] += c[x]
        else:
            densities[2] += c[x]

    d01 = densities[0] + densities[1]
    if d01 <= 0:
        return 0.5

    A = densities[0] / d01
    B = densities[1] / d01
    p = A*(1-B) + (1-A)*B
    return float(p)


# ---------------------------------------------------------------------------
# 3. VMR model using event-based, low-rank memory
# ---------------------------------------------------------------------------

@dataclass
class BoundEvent:
    """A single binding event (context-feature pair) in memory."""
    c: np.ndarray
    f: np.ndarray


class VMRModelSimplified:
    """
    Conceptually identical VMR:

    - Poisson-coded F & C layers
    - Context drift per event using rho_fx
    - Bidirectional memory via stored bound events and gamma_FC/gamma_CF
    - Question-prompt retrieval
    - Turning-point decision rule
    """

    def __init__(self, cfg: ExperimentConfig):
        self.cfg = cfg

    # ---- Poisson-coded representations ----

    def freq_vec(self, hz: float) -> np.ndarray:
        pmf = poisson.pmf(self.cfg.F_features, mu=hz)
        return l2_normalize(pmf)

    def ctx_vec(self, mu: float) -> np.ndarray:
        pmf = poisson.pmf(self.cfg.C_features, mu=mu)
        return l2_normalize(pmf)

    # ---- Context evolution ----

    def context_update(
        self,
        c_prev: Optional[np.ndarray],
        cIN: np.ndarray,
        beta: float
    ) -> np.ndarray:
        """
        If c_prev is None, just initialize context as cIN.
        Otherwise, apply TCM-style drift with rho_fx.
        """
        if c_prev is None:
            return cIN.copy()
        rho = rho_fx(c_prev, cIN, beta)
        return rho * c_prev + beta * cIN

    # ---- Memory retrieval using low-rank event representation ----

    def retrieve_feature(
        self,
        bound_events: List[BoundEvent],
        c_prompt: np.ndarray,
        gamma_CF: float
    ) -> np.ndarray:
        """
        Compute f_IN = norm(M_CF * c_prompt) using:
        M_CF = sum_n gamma_CF * (1-gamma_CF)^(T-n) f_n c_n^T
        where T = len(bound_events).
        """
        if not bound_events:
            return np.zeros_like(c_prompt)  # shape will be wrong, override below

        # All f_n share the same dimension
        f_dim = bound_events[0].f.size
        f_accum = np.zeros(f_dim, dtype=float)

        T = len(bound_events)
        for idx, ev in enumerate(bound_events):
            # Weight for event n: gamma_CF * (1-gamma_CF)^(T-1-idx)
            power = (T-1) - idx
            w = gamma_CF * ((1.0 - gamma_CF) ** power)
            dot_c = float(np.dot(ev.c, c_prompt))
            f_accum += w * dot_c * ev.f

        return l2_normalize(f_accum)

    def retrieve_context(
        self,
        bound_events: List[BoundEvent],
        f_in: np.ndarray,
        gamma_FC: float
    ) -> np.ndarray:
        """
        Compute c_IN = M_FC * f_IN using:
        M_FC = sum_n gamma_FC * (1-gamma_FC)^(T-n) c_n f_n^T
        """
        if not bound_events:
            return np.zeros_like(f_in)  # will be overwritten effectively

        c_dim = bound_events[0].c.size
        c_accum = np.zeros(c_dim, dtype=float)

        T = len(bound_events)
        for idx, ev in enumerate(bound_events):
            power = (T-1) - idx
            w = gamma_FC * ((1.0 - gamma_FC) ** power)
            dot_f = float(np.dot(ev.f, f_in))
            c_accum += w * dot_f * ev.c

        return c_accum  # not normalized in original retrieval step

    # ---- Run a single subcondition ----

    def run_subcondition(
        self,
        params: Dict[str, float],
        condi_name: str
    ) -> float:
        """
        Runs the full encoding->probe->retrieval->decision pipeline
        for a single subcondition, returning p_correct.
        """

        cfg = self.cfg

        # Parse condition name, e.g. "S_low_111_1"
        PTS = condi_name[0]  # 'S' or 'D' (same/different)
        TNS = "low" if condi_name.split("_")[1] == "low" else "high"
        triple = condi_name.split("_")[2]  # e.g. "111"
        target_pos = int(triple[0])       # unused here, but kept for completeness
        ASP = int(triple[1])              # 1 = AS before item 1, 2 = AS before item 2
        QIP = int(triple[2])              # 1 or 2

        # Frequencies (f1, f2, fP)
        f1_hz, f2_hz, fP_hz = cfg.conditions[condi_name]
        f1 = self.freq_vec(f1_hz)
        f2 = self.freq_vec(f2_hz)
        fP = self.freq_vec(fP_hz)

        # Event contexts
        c1 = self.ctx_vec(cfg.Temp_scalar[0])
        c2 = self.ctx_vec(cfg.Temp_scalar[1])
        cP = self.ctx_vec(cfg.Temp_scalar[2])

        cAS1 = self.ctx_vec(cfg.AS1_ms)
        cAS2 = self.ctx_vec(cfg.AS2_ms)

        # Parameters
        beta_AS        = params["Beta_AS"]
        beta_list      = params["Beta_ListItem"]
        beta_probe_low = params["Beta_Probe_low"]
        beta_probe_high= params["Beta_Probe_high"]
        beta_retrieval = params["Beta_retrvl"]
        gamma_FC       = params["gamma_FC"]
        gamma_CF       = params["gamma_CF"]

        # Internal state
        c_current: Optional[np.ndarray] = None
        bound_events: List[BoundEvent] = []

        # Event schedule
        # ASP=1 → AS before item 1; ASP=2 → AS before item 2
        AS_flags = [1, 0] if ASP == 1 else [0, 1]
        item_features = [f1, f2]
        item_contexts = [c1, c2]
        AS_contexts   = [cAS1, cAS2]

        # 1) Encoding of two list items (with possible AS)
        for i in range(2):
            # Optional AS event before item i
            if AS_flags[i] == 1:
                c_current = self.context_update(c_current, AS_contexts[i], beta_AS)
                # AS does not bind

            # List item event (binds)
            c_current = self.context_update(c_current, item_contexts[i], beta_list)
            bound_events.append(BoundEvent(c=c_current.copy(), f=item_features[i].copy()))

        # 2) Probe encoding (2 cycles)
        beta_probe = beta_probe_low if TNS == "low" else beta_probe_high
        for _ in range(2):
            c_current = self.context_update(c_current, cP, beta_probe)
            bound_events.append(BoundEvent(c=c_current.copy(), f=fP.copy()))

        # 3) Retrieval
        c_prompt = c1 if QIP == 1 else c2

        f_in = self.retrieve_feature(bound_events, c_prompt, gamma_CF)
        c_in = self.retrieve_context(bound_events, f_in, gamma_FC)

        # Feed retrieved context back into dynamics
        c_final = self.context_update(c_current, c_in, beta_retrieval)

        # 4) Decision
        return p_correct_from_context(c_final)

    # ---- Run all subconditions and aggregate to main conditions ----

    def run_all_conditions_and_aggregate(
        self,
        params: Dict[str, float]
    ) -> np.ndarray:
        """
        Returns a vector of length 16: mean p_correct over 6 subconditions
        for each main condition.
        """
        cfg = self.cfg
        main_to_vals: Dict[str, List[float]] = {name: [] for name in cfg.main_condi_names}

        for sub_name in cfg.sub_condi_names:
            p = self.run_subcondition(params, sub_name)
            main_name = sub_name[:-2]
            main_to_vals[main_name].append(p)

        main_means = np.array([
            np.mean(main_to_vals[m]) for m in cfg.main_condi_names
        ], dtype=float)

        return main_means


# ---------------------------------------------------------------------------
# 5. SciPy optimizer for the simplified VMR
# ---------------------------------------------------------------------------




class VMRParameterSearch:
    """
    Wrap a SciPy optimizer around the simplified VMR.

    Parameters fitted:
        Beta_AS
        Beta_ListItem
        Beta_Probe_low
        Beta_Probe_high
        Beta_retrvl
        gamma_FC
        gamma_CF
    """

    PARAM_NAMES = [
        "Beta_AS",
        "Beta_ListItem",
        "Beta_Probe_low",
        "Beta_Probe_high",
        "Beta_retrvl",
        "gamma_FC",
        "gamma_CF",
    ]

    def __init__(self, cfg: ExperimentConfig, model: VMRModelSimplified):
        self.cfg = cfg
        self.model = model

    # ------------------------------------------------------------------
    # vector <-> dict conversions
    # ------------------------------------------------------------------
    def vec_to_dict(self, x: np.ndarray) -> Dict[str, float]:
        return {name: float(val) for name, val in zip(self.PARAM_NAMES, x)}

    def dict_to_vec(self, d: Dict[str, float]) -> np.ndarray:
        return np.array([d[name] for name in self.PARAM_NAMES], dtype=float)

    # ------------------------------------------------------------------
    # Objective function: RMSE between empirical and simulated main-condition means
    # ------------------------------------------------------------------
    def objective_rmse(self, x: np.ndarray) -> float:
        params = self.vec_to_dict(x)
        sim = self.model.run_all_conditions_and_aggregate(params)
        emp = self.cfg.p_correct_emp_Means

        # RMSE
        rmse = np.sqrt(np.mean((emp - sim)**2))
        return rmse

    # ------------------------------------------------------------------
    # Optimization wrapper
    # ------------------------------------------------------------------
    def fit_parameters(
        self,
        x0: Optional[np.ndarray] = None,
        method: str = "L-BFGS-B"
    ) -> Dict[str, Any]:

        # initial guess: 0.5 for all parameters unless supplied
        if x0 is None:
            x0 = np.ones(len(self.PARAM_NAMES)) * 0.5

        # bounds: all parameters in [0,1] except gamma values must not be 0
        bounds = [
            (0.0, 1.0),   # Beta_AS
            (0.0, 1.0),   # Beta_ListItem
            (0.0, 1.0),   # Beta_Probe_low
            (0.0, 1.0),   # Beta_Probe_high
            (0.0, 1.0),   # Beta_retrvl
            (1e-4, 1.0),  # gamma_FC
            (1e-4, 1.0),  # gamma_CF
        ]

        result = minimize(
            fun=self.objective_rmse,
            x0=x0,
            method=method,
            bounds=bounds,
        )

        best_vec = result.x
        best_dict = self.vec_to_dict(best_vec)
        best_rmse = self.objective_rmse(best_vec)

        return {
            "result": result,
            "best_vector": best_vec,
            "best_parameters": best_dict,
            "best_rmse": best_rmse
        }


# ---------------------------------------------------------------------------
# 4. Simple test / usage example
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cfg = ExperimentConfig()
    model = VMRModelSimplified(cfg)

    # Example parameter set (arbitrary values in [0,1])
    params_example = {
        "Beta_AS":        0.9894,
        "Beta_ListItem":  0.2639,
        "Beta_Probe_low": 0.0001,
        "Beta_Probe_high":0.8307,
        "Beta_retrvl":    1.0,
        "gamma_FC":       0.4743,
        "gamma_CF":       0.3667,
    }

    p_sim = model.run_all_conditions_and_aggregate(params_example)

    print("Main conditions (in order):")
    print(cfg.main_condi_names)
    print("\nSimulated p(correct):")
    print(np.round(p_sim, 3))

    print("\nEmpirical p(correct):")
    print(np.round(cfg.p_correct_emp_Means, 3))

    rmse = np.sqrt(np.mean((cfg.p_correct_emp_Means - p_sim)**2))
    print(f"\nRMSE between empirical and simulated (with example params): {rmse:.3f}")

# ---------------------------------------------------------------------------
# 6. Example: optimize the simplified VMR
# ---------------------------------------------------------------------------

# if __name__ == "__main__":
#     cfg = ExperimentConfig()
#     model = VMRModelSimplified(cfg)
#     search = VMRParameterSearch(cfg, model)

#     print("Starting optimization...")
#     out = search.fit_parameters()

#     print("\nOptimization finished.")
#     print("Success:", out["result"].success)

#     print("\nBest parameter vector:")
#     print(np.round(out["best_vector"], 4))

#     print("\nBest parameter dictionary:")
#     for k, v in out["best_parameters"].items():
#         print(f"{k:15s} {v:.4f}")

#     print(f"\nBest RMSE = {out['best_rmse']:.4f}")

# ---------------------------------------------------------------------------
# 7. Plot empirical vs simulated data for the simplified VMR
# ---------------------------------------------------------------------------

def plot_model_fit(cfg: ExperimentConfig, sim_vals: np.ndarray):
    """
    Plot empirical vs simulated p(correct) for TNS=low and TNS=high.
    """
    emp = cfg.p_correct_emp_Means
    sem = cfg.p_correct_emp_SEMs
    cond_names = cfg.main_condi_names  # 16 names in order

    # Condition labels for the x-axis
    xticks_labels = ["1/1/1","1/2/1","1/1/2","1/2/2","2/1/1","2/1/2","2/2/1","2/2/2"]
    x = np.arange(8)

    # ----------------------------
    # Plot 1: TNS = LOW (conditions 1–8)
    # ----------------------------
    plt.figure(figsize=(10, 6))
    plt.title("Model Fit – TNS = LOW")
    plt.plot(emp[:8], "bs-", label="Empirical", linewidth=2)
    plt.plot(sim_vals[:8], "bo--", label="VMR Simplified", linewidth=2)
    plt.errorbar(x, emp[:8], yerr=sem[:8], fmt="none", ecolor="b", capsize=4)

    plt.xticks(x, xticks_labels, fontsize=11)
    plt.xlabel("Condition (TP / ASP / QIP)")
    plt.ylabel("p(correct)")
    plt.ylim(0, 1.1)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

    # ----------------------------
    # Plot 2: TNS = HIGH (conditions 9–16)
    # ----------------------------
    plt.figure(figsize=(10, 6))
    plt.title("Model Fit – TNS = HIGH")
    plt.plot(emp[8:], "rs-", label="Empirical", linewidth=2)
    plt.plot(sim_vals[8:], "ro--", label="VMR Simplified", linewidth=2)
    plt.errorbar(x, emp[8:], yerr=sem[8:], fmt="none", ecolor="r", capsize=4)

    plt.xticks(x, xticks_labels, fontsize=11)
    plt.xlabel("Condition (TP / ASP / QIP)")
    plt.ylabel("p(correct)")
    plt.ylim(0, 1.1)
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    cfg = ExperimentConfig()
    model = VMRModelSimplified(cfg)
    search = VMRParameterSearch(cfg, model)

    print("Starting optimization...")
    out = search.fit_parameters()

    print("\nBest RMSE:", out["best_rmse"])
    print("Best parameters:", out["best_parameters"])

    # Compute simulated values using best parameters
    sim = model.run_all_conditions_and_aggregate(out["best_parameters"])

    # Plot the fit
    plot_model_fit(cfg, sim)

