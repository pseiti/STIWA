## General Notes: 
### This code implements the Vibrotactile Model of Resonance (VMR) as ...
## ... described in the manuscript "A Retrieved Context Model to Predict Vibrotactile Frequency Discrimination".
### See the according comments for the specific parts of the code that implement Equations (1) - (7) of VMR.

import time
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import scipy.stats as st
from scipy.stats import poisson
from scipy.stats import norm
from scipy.stats import binom
from scipy.stats import entropy
from scipy.ndimage import gaussian_filter
import scipy.optimize as so
from scipy.optimize import differential_evolution
from scipy.optimize import brute

class prepare:
	
	def inputData(self):
		# S and D = Same and Different
		# S1 or S2, D1 or D2 = Position 1 or Position 2 in a Same or Different condition
		# low and high = TNS-low and TNS-high, where TNS = Target-to-Nontarget similarity
		# _x = Indicates the subcondition of a given main condition, where x = 1,...,6.
		## There are thus 2 x 4 x 6 = 48 unique conditions to be predicted.
		conditions = { 
		"S1_low_1": [82,132,82],"S1_low_2": [132,82,132],"S1_low_3": [70,112,70],
		"S1_low_4": [112,70,112],"S1_low_5": [96,154,96],"S1_low_6": [154,96,154],
		"S2_low_1": [82,132,132],"S2_low_2": [132,82,82],"S2_low_3": [70,112,112],
		"S2_low_4": [112,70,70],"S2_low_5": [96,154,154],"S2_low_6": [154,96,96],
		"D1_low_1": [82,132,70],"D1_low_2": [132,82,154],"D1_low_3": [70,112,60],
		"D1_low_4": [112,70,132],"D1_low_5": [96,154,82],"D1_low_6": [154,96,180],
		"D2_low_1": [82,132,154],"D2_low_2": [132,82,70],"D2_low_3": [70,112,132],
		"D2_low_4": [112,70,60],"D2_low_5": [96,154,180],"D2_low_6": [154,96,82],
		"S1_high_1": [82,112,82],"S1_high_2": [112,82,112],"S1_high_3": [70,96,70],
		"S1_high_4": [96,70,96],"S1_high_5": [96,132,96],"S1_high_6": [132,96,132],
		"S2_high_1": [82,112,112],"S2_high_2": [112,82,82],"S2_high_3": [70,96,96],
		"S2_high_4": [96,70,70],"S2_high_5": [96,132,132],"S2_high_6": [132,96,96],
		"D1_high_1": [82,112,70],"D1_high_2": [112,82,132],"D1_high_3": [70,96,60],
		"D1_high_4": [96,70,112],"D1_high_5": [96,132,82],"D1_high_6": [132,96,154],
		"D2_high_1": [82,112,132],"D2_high_2": [112,82,70],"D2_high_3": [70,96,112],
		"D2_high_4": [96,70,60],"D2_high_5": [96,132,154],"D2_high_6": [132,96,82]}
		
		unique_condition_names = []
		for x in conditions:
			unique_condition_names.append(x)
		unique_Fqs = []
		for cx in conditions.values():
			unique_Fqs.append(cx)
		unique_Fqs = np.unique(unique_Fqs)
		Hz_range_min = 1
		Hz_range_max = 300
		F_features = np.arange(Hz_range_min,Hz_range_max,1)
		Temp_range_min = 1
		Temp_range_max = 6000
		C_features = np.arange(Temp_range_min,Temp_range_max,70) 
		Temp_scalar = np.array([900,2900,4900,5900]) 
		main_condi_names = ["S1_low","S2_low","D1_low","D2_low","S1_high","S2_high","D1_high","D2_high"]
		sub_condi_names = list(conditions.keys())
		p_correct_SorD_emp = np.array([0.594167,0.695833,0.599722,0.538889,0.631389,0.707500,0.549722,0.485833])
		N_responses_SorD = np.nan
		d_Prime_1or2_emp = np.array([1.32, 1.48, 0.81, 1.01]) # Same/Low, Different/Low, Same/High, Different/High
		# Names of steps of rating scale: Sure - lessSure - Unsure - Unsure - lessSure – Sure
		S1_1to5_SameLow_emp = np.array([0.1439106,0.4990775,0.7674077,0.8491661,0.9635187])
		S2_1to5_SameLow_emp = np.array([0.01977898,0.08609008,0.16261948,0.37415016,0.75033650])
		D1_1to5_DiffLow_emp = np.array([0.1525585, 0.5197318, 0.8332057, 0.8986638, 0.9754359])
		D2_1to5_DiffLow_emp = np.array([0.01634693, 0.07173676, 0.1409325, 0.3761745, 0.7508688])
		S1_1to5_SameHigh_emp = np.array([0.1082916,0.3838179,0.6315914,0.7696246,0.9304663])
		S2_1to5_SameHigh_emp = np.array([0.03178504,0.13810474,0.24048732,0.46597713,0.79263244])
		D1_1to5_DiffHigh_emp = np.array([0.1242838,0.4486599,0.7374914,0.8393417,0.9601434])
		D2_1to5_DiffHigh_emp = np.array([0.02217522,0.12493919,0.24095754,0.46895104,0.79282785])
		p_correct_1or2_emp = np.array([0.7674077,0.8373805,0.8332057,0.8590675,0.6315914,0.7595127,0.7374914,0.7590425])
		N_responses_1or2 = np.array([2139, 2505, 1441, 1660, 2273, 2547, 1621, 1851])
		output = {"conditions": conditions, "Temp_scalar": Temp_scalar, "F_features": F_features, "C_features": C_features,
		"main_condi_names": main_condi_names, "sub_condi_names": sub_condi_names, "p_correct_SorD_emp": p_correct_SorD_emp,
		"dPrime_1or2_emp": d_Prime_1or2_emp, "p_correct_1or2_emp": p_correct_1or2_emp, "N_responses_1or2": N_responses_1or2}

		return output

	def norm_fx(self,vec):
		vec_sq = np.power(vec,2)
		vec_sq_sum = np.sum(vec_sq)
		vec_norm = np.divide(vec,np.sqrt(vec_sq_sum))
		return(vec_norm)

	def rho_fx(self,c_prev,cIN,Beta):
		dotprod = np.dot(c_prev,cIN)
		comp1_1 = np.power(dotprod,2)-1
		comp1 = np.sqrt(1 + np.power(Beta,2) * comp1_1)
		comp2 = Beta*dotprod
		return comp1 - comp2

class generateData:

	def __init__(self, Temp_scalar, F_features, C_features, conditions, main_condi_names, sub_condi_names):
		self.Temp_scalar = Temp_scalar
		self.F_features = F_features
		self.C_features = C_features
		self.conditions = conditions
		self.main_condi_names = main_condi_names
		self.sub_condi_names = sub_condi_names
		self.nItems = 3 # Two list items plus one probe

	def tTCM_running_subcondition(self,cur_paraSet,condi_name):
		D = prepare()
		inputData = D.inputData()
		res_emp = inputData.get("res_emp")
		TNS_id = condi_name.find("_")
		TNS_abbr = condi_name[TNS_id+1]
		TNS = "low" if TNS_abbr=="l" else "high"
		Position = condi_name[1]

		# Free parameters		
		Beta_listItem = cur_paraSet[0]
		Beta_Probe = Beta_listItem
		if TNS == "low":
			Beta_Probe = cur_paraSet[1]

		#### Main VMR-specific code starts here: ###################################################
		Hz_scalar = np.array(self.conditions[condi_name])
		# Equation (1) Hz-layer F encoding
		item1_Hz = poisson.pmf(self.F_features, mu = Hz_scalar[0])
		item2_Hz = poisson.pmf(self.F_features, mu = Hz_scalar[1])
		P_Hz = poisson.pmf(self.F_features, mu = Hz_scalar[2])
		item1_Hz = D.norm_fx(item1_Hz) 
		item2_Hz = D.norm_fx(item2_Hz)
		P_Hz = D.norm_fx(P_Hz)
		Hz_distributed = np.array([item1_Hz,item2_Hz,P_Hz])
		# Equation (2) Temporal layer T encoding
		Temp_scalar = self.Temp_scalar.astype(float)
		context1 = D.norm_fx(poisson.pmf(self.C_features, mu = self.Temp_scalar[0]))
		context2 = D.norm_fx(poisson.pmf(self.C_features, mu = self.Temp_scalar[1]))
		contextP = D.norm_fx(poisson.pmf(self.C_features, mu = self.Temp_scalar[2]))
		Temp_distributed = np.array([context1,context2,contextP])
		# Preparing 'mental structure' of item-context, respectively, context-item associations
		MFC = np.zeros(len(item1_Hz)*len(context1)).reshape((len(context1),len(item1_Hz)))
		MCF = np.zeros(len(item1_Hz)*len(context1)).reshape((len(item1_Hz),len(context1)))
		##### Encoding of the two list items
		Beta = Beta_listItem
		for item_i in range(2):
			f_i = Hz_distributed[item_i]
			cIN = Temp_distributed[item_i]
			if item_i==0:
				c_i = cIN
			else:
				c_prev = c_i
				rho_i = D.rho_fx(c_prev,cIN,Beta)
				# Equation (3)
				c_i = np.add((rho_i*c_prev),(Beta*cIN))
                        # Equation (4)
			# plt.plot(c_i)
			delta_MFC = np.outer(c_i,f_i)
			MFC = MFC + delta_MFC
			delta_MCF = np.outer(f_i,c_i)
			MCF = MCF + delta_MCF
		##### Probe encoding
		Beta = Beta_Probe
		f_i = Hz_distributed[2]
		cIN = Temp_distributed[2]
		for cycle_x in range(2):
			c_prev = c_i
			rho_i = D.rho_fx(c_prev,cIN,Beta)
			c_i = np.add((rho_i*c_prev),(Beta*cIN))
			delta_MFC = np.outer(c_i,f_i)
			MFC = MFC + delta_MFC
			delta_MCF = np.outer(f_i,c_i)
			MCF = MCF + delta_MCF
		# plt.plot(c_i,"--")
		# plt.show()
		##### Responding ###################################
		# item-based context retrieval
		# Equation (5)
		cIN = D.norm_fx(np.inner(MFC,f_i))
		c_prev = c_i
		rho_i = D.rho_fx(c_prev,cIN,Beta)
		# context drift
		c_i = np.add((rho_i*c_prev),(Beta*cIN))
		# context-based item retrieval
		fIN = D.norm_fx(np.inner(MCF,c_i))
		### Part of code modeling Same / Different judgment 
		area_overlap = 0
		area_diff_fIN_larger = 0
		area_diff_P_larger = 0
		for x in range(len(P_Hz)):
			if P_Hz[x]<fIN[x]:
				area_diff_fIN_larger += fIN[x]-P_Hz[x]
				area_overlap += P_Hz[x]
			else:
				area_diff_P_larger += P_Hz[x]-fIN[x]
				area_overlap += fIN[x]
		areas = [area_overlap,area_diff_fIN_larger,area_diff_P_larger]
		areas_n = np.divide(areas,np.sum(areas))
		sameness = areas_n[0] 
		difference = areas_n[1] + areas_n[2]
		# Equation (6)
		p_same = sameness*(1-difference) 
		p_different = 1-p_same 
		p_correct_SorD = p_same if condi_name[0]=="S" else p_different
		
		### Part of code modeling  1/2-judgment 
		cIN = D.norm_fx(np.inner(MFC,fIN))
		increasing = True
		densities = [0,0,0]
		for x in range(len(cIN)-1):
			if 0 <= x < .33*len(self.C_features): #24
				densities[0] += cIN[x]
			elif .33*len(self.C_features) <= x < .66*len(self.C_features): #48
				densities[1] += cIN[x]
			elif x >= .66*len(self.C_features):
				densities[2] += cIN[x]
		act_early, act_late = densities[:2]
		# Equation (7)
		p_correct_1or2 = act_early*act_late + (1-(act_early*act_late))*.5
		output = {
		"p_correct_SorD": p_correct_SorD,
		"p_correct_1or2": p_correct_1or2
		}
		#### Main VMR-specific code ends here. ####################################################
		return output

	def run_allConditions_and_aggregate(self,cur_paraSet):
		columns = ["subcondition_name","maincondition_name",
		"PTS","Position","TNS","p_correct_SorD","p_correct_1or2"]
		res_df = pd.DataFrame(columns=columns)
		for sub_condi_name in self.sub_condi_names:
			mainCondi_name = sub_condi_name[:2]
			S_or_D_trial = mainCondi_name[0]
			Position = mainCondi_name[1]
			TNS = sub_condi_name[3]
			TNS = "low" if TNS=="l" else "high"
			mainCondi_name = mainCondi_name + "_" + TNS
			result_subcondi = self.tTCM_running_subcondition(cur_paraSet,sub_condi_name)
			p_correct_SorD_subcondi = result_subcondi.get("p_correct_SorD")
			p_correct_1or2_subcondi = result_subcondi.get("p_correct_1or2")
			res_df.loc[len(res_df.index)] = [sub_condi_name,mainCondi_name,S_or_D_trial,Position,
			TNS,p_correct_SorD_subcondi,p_correct_1or2_subcondi] 
		p_correct_SorD_array = []
		p_correct_1or2_array = []
		for x in self.main_condi_names:
			name_vec = res_df.maincondition_name
			x_rows = np.where(name_vec==x)
			x_data = res_df.iloc[x_rows]
			x_mean = np.mean(x_data.p_correct_SorD)
			p_correct_SorD_array.append(x_mean)
			p_correct_1or2_mean = np.mean(x_data.p_correct_1or2)
			p_correct_1or2_array.append(p_correct_1or2_mean)
		output = {
		"p_correct_SorD": np.array(p_correct_SorD_array),
		"p_correct_1or2": np.array(p_correct_1or2_array)
		}
		return output 

class search_parameter_space:
	def __init__(self,nfreePar):
		self.nfreePar = nfreePar
		self.D = prepare()
		self.nDataPoints_SorD = 8 
		self.nDataPoints_1or2 = 8
		
	def evaluateFit(self,cur_paraSet):
		nfreePar = self.nfreePar
		nDataPoints = self.nDataPoints_SorD + self.nDataPoints_1or2
		inputData = self.D.inputData()
		Temp_scalar = inputData.get("Temp_scalar")
		F_features = inputData.get("F_features")
		C_features = inputData.get("C_features")
		Conditions = inputData.get("conditions")
		main_condi_names = inputData.get("main_condi_names")
		sub_condi_names = inputData.get("sub_condi_names")
		M = generateData(Temp_scalar, F_features, C_features, Conditions, 
			main_condi_names, sub_condi_names)
		output_sim = M.run_allConditions_and_aggregate(cur_paraSet)

		N_responses_total = 60*8*6*10 # = 28800; Nn = 60 subjects, 8 main conditions, 6 subconditions (per maincondition), 10 trials (per subcondition)  
		N_responses_perPTS_TNS_tabulation = N_responses_total/4 # = 7200 {Same/Low, Different/Low, Same/High, Different/High}
		N_responses_perSubject = N_responses_total/60 # = 480
		N_responses_perMainCondition = N_responses_total/8
		N_responses_perSubCondition = N_responses_total/8*6
		
		p_correct_SorD_emp = inputData.get("p_correct_SorD_emp")
		p_correct_SorD_sim = np.array(output_sim.get("p_correct_SorD"))
		Mean_p_correct_SorD_emp = np.mean(p_correct_SorD_emp)
		RMSE_p_correct_SorD = np.sqrt(np.mean(np.power(np.subtract(p_correct_SorD_emp,p_correct_SorD_sim),2)))
		NRMSE_p_correct_SorD = RMSE_p_correct_SorD/Mean_p_correct_SorD_emp
		p_correct_1or2_emp = inputData.get("p_correct_1or2_emp")
		p_correct_1or2_sim = np.array(output_sim.get("p_correct_1or2"))
		RMSE_p_correct_1or2 = np.sqrt(np.mean(np.power(np.subtract(p_correct_1or2_emp,p_correct_1or2_sim),2)))
		Mean_p_correct_1or2_emp = np.mean(p_correct_1or2_emp)
		NRMSE_p_correct_1or2 = RMSE_p_correct_1or2/Mean_p_correct_1or2_emp
		RSS_SorD = np.sum(np.power(np.subtract(p_correct_SorD_emp,p_correct_SorD_sim),2))
		BIC_SorD = nfreePar*np.log(self.nDataPoints_SorD) + self.nDataPoints_SorD*np.log(RSS_SorD/self.nDataPoints_SorD)
		RSS_1or2 = np.sum(np.power(np.subtract(p_correct_1or2_emp,p_correct_1or2_sim),2))
		BIC_1or2 = nfreePar*np.log(self.nDataPoints_1or2) + self.nDataPoints_1or2*np.log(RSS_1or2/self.nDataPoints_1or2)
		NRMSE = NRMSE_p_correct_SorD + NRMSE_p_correct_1or2
		chi2_crit_SorD = st.chi2.ppf(q=.95, df=(self.nDataPoints_SorD - self.nfreePar))
		chi2_tabl_SorD = np.vstack((p_correct_SorD_emp*N_responses_perMainCondition,p_correct_SorD_sim*N_responses_perMainCondition))
		colSum = chi2_tabl_SorD.sum(0); rowSum = chi2_tabl_SorD.sum(1); N = np.sum(colSum)
		chi2_pred_SorD = np.outer(rowSum,colSum)/N
		chi2_SorD = np.sum(((chi2_tabl_SorD-chi2_pred_SorD)**2)/chi2_pred_SorD)
		chi2_p_crit_SorD = 1-st.chi2.cdf(x=chi2_crit_SorD,df=(self.nDataPoints_SorD - self.nfreePar))
		chi2_p_SorD = 1-st.chi2.cdf(x=chi2_SorD,df=(self.nDataPoints_SorD - self.nfreePar))
		chi2_crit_1or2 = st.chi2.ppf(q=.95, df=(self.nDataPoints_1or2 - self.nfreePar))
		chi2_tabl_1or2 = np.vstack((p_correct_1or2_emp*inputData.get("N_responses_1or2"),p_correct_1or2_sim*inputData.get("N_responses_1or2")))
		colSum = chi2_tabl_1or2.sum(0); rowSum = chi2_tabl_1or2.sum(1); N = np.sum(colSum)
		chi2_pred_1or2 = np.outer(rowSum,colSum)/N
		chi2_1or2 = np.sum(((chi2_tabl_1or2-chi2_pred_1or2)**2)/chi2_pred_1or2)
		chi2_p_crit_1or2 = 1-st.chi2.cdf(x=chi2_crit_1or2,df=(self.nDataPoints_1or2 - self.nfreePar))
		chi2_p_1or2 = 1-st.chi2.cdf(x=chi2_1or2,df=(self.nDataPoints_1or2 - self.nfreePar))
		chi2_added = chi2_SorD + chi2_1or2
		chi2_crit_added = st.chi2.ppf(q=.95, df=(nDataPoints - nfreePar))
		chi2_p_crit_added = 1-st.chi2.cdf(x=chi2_crit_added,df=(nDataPoints - nfreePar))
		chi2_p_added = 1-st.chi2.cdf(x=chi2_added,df=(nDataPoints-nfreePar))
		output = {
			"Results on Same/Different task": "p_correct",
			"p_correct_SorD_emp": np.around(p_correct_SorD_emp,2),
			"p_correct_SorD_sim": np.around(p_correct_SorD_sim,2),
			"p_correct_1or2_emp": np.around(p_correct_1or2_emp,2),
			"p_correct_1or2_sim": np.around(p_correct_1or2_sim,2),
			"Number of data points": self.nDataPoints_SorD + self.nDataPoints_1or2,
			"nPar": self.nfreePar,
			"NRMSE": NRMSE,
			"NRMSE_p_correct_1or2": NRMSE_p_correct_1or2,
			"NRMSE_p_correct_SorD": NRMSE_p_correct_SorD,
			"RSS_SorD": RSS_SorD,
			"BIC_SorD": BIC_SorD,
			"RSS_1or2": RSS_1or2,
			"RSS_added": RSS_SorD + RSS_1or2,
			"BIC_1or2": BIC_1or2,
			"chi2_SorD": chi2_SorD,
			"chi2_crit_SorD": chi2_crit_SorD,
			"chi2_p_SorD": chi2_p_SorD,
			"chi2_1or2": chi2_1or2,
			"chi2_crit_1or2": chi2_crit_1or2,
			"chi2_p_1or2": chi2_p_1or2,
			"chi2_added": chi2_added,
			"chi2_crit_added": chi2_crit_added,
			"chi2_p_added": chi2_p_added
		}
		
		return output

	def linkTofMinSearch(self,cur_algoString):
		global initSearch, start_time, interim, n_interims
		if initSearch==True:
			print()
			print("Searching space ...")
			initSearch=False
		pred = self.evaluateFit(cur_algoString)
		chi2_SorD = pred.get("chi2_SorD")
		chi2_1or2 = pred.get("chi2_1or2")
		chi2_added = pred.get("chi2_added")
		NRMSE_SorD = pred.get("NRMSE_p_correct_SorD")
		NRMSE_1or2 = pred.get("NRMSE_p_correct_1or2")
		NRMSE = NRMSE_SorD + NRMSE_1or2
		RSS = pred.get("RSS_added")
		if np.min(np.array(NRMSE_trace))>NRMSE:
			NRMSE_trace.append(NRMSE)
			print("... best fitting set thus far, based on NRMSE: " + str(np.around(cur_algoString,3)));
		if np.min(np.array(chi2_trace))>chi2_SorD:
			chi2_trace.append(chi2_SorD)
			print("... best fitting set thus far, based on Chi2: " + str(np.around(cur_algoString,3)));
		dur_since_lastMessage = time.time() - interim
		dur_total = time.time() - start_time
		if dur_since_lastMessage > 10: # Sekunden
			print()
			print("... for " + str(round(dur_total)) + " seconds, NRMSE: " + str(np.around(np.min(NRMSE_trace),3)) + ";")
			print()
			print("... for " + str(round(dur_total)) + " seconds, RSS: " + str(np.around(RSS,3)))
			interim = time.time()
			n_interims += 1
		return chi2_added


		
# #################################################################################################################

# #### Applying classes and functions #############################################################################


# ###### Testing classes and functions ############################################################################

# prep = prepare()
# prep.inputData()

# print()
# condi_name_input = input("""

# 	Which experimental condition?
	
# 	"S1_low_x"
# 	"S2_low_x"
# 	"D1_low_x"
# 	"D2_low_x"
# 	"S1_high_x"
# 	"S2_high_x"
# 	"D1_high_x"
# 	"D2_high_x"

# 	where x ranges between 1 and 6

# 	""")

# prep = prepare()
# inputData = prep.inputData()
# Temp_scalar = inputData.get("Temp_scalar")
# res_emp = inputData.get("res_emp")
# F_features = inputData.get("F_features")
# C_features = inputData.get("C_features")
# Conditions = inputData.get("conditions")
# main_condi_names = inputData.get("main_condi_names")
# sub_condi_names = inputData.get("sub_condi_names")
# M = generateData(Temp_scalar,F_features,C_features,Conditions,main_condi_names,sub_condi_names)
# M.tTCM_running_subcondition(cur_paraSet = [.70914837, .55405778],
# 	condi_name=condi_name_input)
####


# # print()
# # S = search_parameter_space(nfreePar=3,nfreePar=2)
# # S.evaluateFit([0.57115471,0.66102614,0.76251886,0.5,0.6099648,0.])

# # #########################################################################################################################

# # ###### Searching parameter space and evaluating model fit  ##############################################################
initSearch = True
start_time = time.time()
interim = start_time
n_interims = 0
NRMSE_trace = [1000000]
chi2_trace = [1000000]
S = search_parameter_space(nfreePar=2)
xopt = so.minimize(fun=S.linkTofMinSearch, method='L-BFGS-B',
## Start values
x0=[ .5, .5],
bounds=[ (.05,1), (.05,1)])
best_paraSet = xopt.get("x")
print()
print("... completed.")
print()
print("Optimization procedure converged?")
print(xopt.get("success"))
print()
print("Best set of searched parameter values:")
print()
print(best_paraSet)
pred_and_eval_given_bestParaSet = S.evaluateFit(best_paraSet)
print()
print("Same/Different frequencies observed (first row) vs. simulated (second row):")
print(pred_and_eval_given_bestParaSet.get("p_correct_SorD_emp"))
print(pred_and_eval_given_bestParaSet.get("p_correct_SorD_sim"))
print("Chi2 value (and critical value): ")
print(pred_and_eval_given_bestParaSet.get("chi2_SorD"))
print(pred_and_eval_given_bestParaSet.get("chi2_crit_SorD"))
print()
print("1/2 frequencies:")
print(pred_and_eval_given_bestParaSet.get("p_correct_1or2_emp"))
print(pred_and_eval_given_bestParaSet.get("p_correct_1or2_sim"))
print("Chi2 value (and critical value): ")
print(pred_and_eval_given_bestParaSet.get("chi2_1or2"))
print(pred_and_eval_given_bestParaSet.get("chi2_crit_1or2"))
print()
print("RSS (Same / Different): ")
print(pred_and_eval_given_bestParaSet.get("RSS_SorD"))
print("RSS (1st / 2nd): ")
print(pred_and_eval_given_bestParaSet.get("RSS_1or2"))
print()
print("BIC (Same / Different): ")
print(pred_and_eval_given_bestParaSet.get("BIC_SorD"))
print("BIC (1st / 2nd): ")
print(pred_and_eval_given_bestParaSet.get("BIC_1or2"))
print()
print("Chi2_added (and critical value):")
print(pred_and_eval_given_bestParaSet.get("chi2_added"))
print(pred_and_eval_given_bestParaSet.get("chi2_crit_added"))
print()
print("NRMSE: ")
print(pred_and_eval_given_bestParaSet.get("NRMSE"))


	
