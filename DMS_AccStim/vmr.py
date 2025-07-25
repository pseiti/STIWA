## General Notes: 
### This code implements the Vibrotactile Model of Resonance (VMR) as ...
## ... described in the manuscript "A Retrieved Context Model to Predict Vibrotactile Frequency Discrimination".
### See the according comments for the specific parts of the code that implement Equations (1) - (7) of VMR.

import conditions
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
		# conditions = { 
		# "S1_low_1": [82,132,82],"S1_low_2": [132,82,132],"S1_low_3": [70,112,70],
		# "S1_low_4": [112,70,112],"S1_low_5": [96,154,96],"S1_low_6": [154,96,154],
		# "S2_low_1": [82,132,132],"S2_low_2": [132,82,82],"S2_low_3": [70,112,112],
		# "S2_low_4": [112,70,70],"S2_low_5": [96,154,154],"S2_low_6": [154,96,96],
		# "D1_low_1": [82,132,70],"D1_low_2": [132,82,154],"D1_low_3": [70,112,60],
		# "D1_low_4": [112,70,132],"D1_low_5": [96,154,82],"D1_low_6": [154,96,180],
		# "D2_low_1": [82,132,154],"D2_low_2": [132,82,70],"D2_low_3": [70,112,132],
		# "D2_low_4": [112,70,60],"D2_low_5": [96,154,180],"D2_low_6": [154,96,82],
		# "S1_high_1": [82,112,82],"S1_high_2": [112,82,112],"S1_high_3": [70,96,70],
		# "S1_high_4": [96,70,96],"S1_high_5": [96,132,96],"S1_high_6": [132,96,132],
		# "S2_high_1": [82,112,112],"S2_high_2": [112,82,82],"S2_high_3": [70,96,96],
		# "S2_high_4": [96,70,70],"S2_high_5": [96,132,132],"S2_high_6": [132,96,96],
		# "D1_high_1": [82,112,70],"D1_high_2": [112,82,132],"D1_high_3": [70,96,60],
		# "D1_high_4": [96,70,112],"D1_high_5": [96,132,82],"D1_high_6": [132,96,154],
		# "D2_high_1": [82,112,132],"D2_high_2": [112,82,70],"D2_high_3": [70,96,112],
		# "D2_high_4": [96,70,60],"D2_high_5": [96,132,154],"D2_high_6": [132,96,82]}
		conditions = {
		# targetPosition, QIP, AS
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
		Temp_scalar = np.array([900,2900,4900,4500]) 
		main_condi_names = [
		"S_low_111","S_low_211","S2_low_112","S2_low_2_212",
		"S_low_121","S_low_221","S2_low_112","S2_low_222",
		"S_high_111","S_high_211","S2_high_112","S2_high_2_212",
		"S_high_121","S_high_221","S2_high_112","S2_high_222",]
		sub_condi_names1 = list(conditions[0].keys())
		sub_condi_names2 = list(conditions[1].keys())
		sub_condi_names = sub_condi_names1 + sub_condi_names2
		p_correct_emp = {
		"S_low_111":[],"S_low_211":[],
		"S_low_221":[],"S_low_21":[],
		"S_low_12":[],"S_low_12":[],
		"S_low_22":[],"S_low_22":[],
		"S_high_11":[],"S_high_11":[],
		"S_high_21":[],"S_high_21":[],
		"S_high_12":[],"S_high_12":[],
		"S_high_22":[],"S_high_22":[]
		}
		N_responses_SorD = np.nan
		# Names of steps of rating scale: Sure - lessSure - Unsure - Unsure - lessSure – Sure
		output = {"conditions": conditions, "Temp_scalar": Temp_scalar, "F_features": F_features, "C_features": C_features,
		"main_condi_names": main_condi_names, "sub_condi_names": sub_condi_names,
		"p_correct_emp": p_correct_emp}

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

	def tTCM_running_subcondition(self,cur_paraSet,condi_name):
		D = prepare()
		inputData = D.inputData()
		res_emp = inputData.get("res_emp")
		# S_high_111_1 # # 111 = targetPosition, QIP, ASP
		PTS = condi_name[0]
		targetPosition = condi_name[-5]
		QIP = int(condi_name[-4])
		ASP = int(condi_name[-3])
		TNS = "low" if condi_name[2]=="l" else "high"
		
		mainCondi_name = PTS + str(targetPosition) + "_" + TNS + "_" + str(ASP)

		# Free parameters		
		Beta_listItem = cur_paraSet[0]
		Beta_Probe = Beta_listItem
		if TNS == "low":
			Beta_Probe = cur_paraSet[1]
		Beta_AS = cur_paraSet[len(cur_paraSet)-1]

		#### Main VMR-specific code starts here: ###################################################
		Hz_scalar = np.array(self.conditions[condi_name])
		# Hz-layer F encoding
		item1_Hz = D.norm_fx(poisson.pmf(self.F_features, mu = Hz_scalar[0]))
		item2_Hz = D.norm_fx(poisson.pmf(self.F_features, mu = Hz_scalar[1]))
		P_Hz = D.norm_fx(poisson.pmf(self.F_features, mu = Hz_scalar[2]))
		Hz_distributed = np.array([item1_Hz,item2_Hz,P_Hz])
		# Temporal layer T encoding
		Temp_scalar = self.Temp_scalar.astype(float)
		context1 = D.norm_fx(poisson.pmf(self.C_features, mu = self.Temp_scalar[0]))
		context2 = D.norm_fx(poisson.pmf(self.C_features, mu = self.Temp_scalar[1]))
		contextP = D.norm_fx(poisson.pmf(self.C_features, mu = self.Temp_scalar[2]))
		# context_AS = context1 if ASP==1 else context2 # AS = Accessory Stimulus
		context_AS = D.norm_fx(poisson.pmf(self.C_features, mu = self.Temp_scalar[3]))
		Temp_distributed = np.array([context1,context2,contextP])
		# Preparing 'mental structure' of item-context, respectively, context-item associations
		MFC = np.zeros(len(item1_Hz)*len(context1)).reshape((len(context1),len(item1_Hz)))
		MCF = np.zeros(len(item1_Hz)*len(context1)).reshape((len(item1_Hz),len(context1)))
		##### Encoding of the two list items (and click)
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
			# plt.plot(c_i)
			delta_MFC = np.outer(c_i,f_i)
			MFC = MFC + delta_MFC
			delta_MCF = np.outer(f_i,c_i)
			MCF = MCF + delta_MCF
			if item_i==(ASP-1):
				c_prev = c_i
				rho_i = D.rho_fx(c_prev,context_AS,Beta_AS)
				c_i = np.add((rho_i*c_prev),(Beta_AS*context_AS))
				delta_MFC = np.outer(c_i,f_i)
				MFC = MFC + delta_MFC
				delta_MCF = np.outer(f_i,c_i)
				MCF = MCF + delta_MCF
		##### Probe encoding
		f_i = Hz_distributed[2]
		cIN = Temp_distributed[2]
		for cycle_x in range(2):
			c_prev = c_i
			rho_i = D.rho_fx(c_prev,cIN,Beta_Probe)
			c_i = np.add((rho_i*c_prev),(Beta_Probe*cIN))
			delta_MFC = np.outer(c_i,f_i)
			MFC = MFC + delta_MFC
			delta_MCF = np.outer(f_i,c_i)
			MCF = MCF + delta_MCF
		# plt.plot(c_i,"--")
		# plt.show()
		##### Responding ###################################
		# question-prompt-based item retrieval
		cIN = context_AS
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
		p_yes = p_same if condi_name[0]=="S" else p_different
		if QIP==1:
			if targetPosition==1:
				p_correct_sim = p_yes
			else:
				p_correct_sim = 1-p_yes
		else:
			if targetPosition==2:
				p_correct_sim = p_yes
			else:
				p_correct_sim = 1-p_yes
		### Part of code modeling  1/2-judgment 
		# cIN = D.norm_fx(np.inner(MFC,fIN))
		# increasing = True
		# densities = [0,0,0]
		# for x in range(len(cIN)-1):
		# 	if 0 <= x < .33*len(self.C_features): #24
		# 		densities[0] += cIN[x]
		# 	elif .33*len(self.C_features) <= x < .66*len(self.C_features): #48
		# 		densities[1] += cIN[x]
		# 	elif x >= .66*len(self.C_features):
		# 		densities[2] += cIN[x]
		# act_early, act_late = densities[:2]
		# # Equation (7)
		# p_correct_1or2 = act_early*act_late + (1-(act_early*act_late))*.5
		output = {
		#"questionProbe": questionProbe,
		"p_correct_SorD": p_correct_sim
		}
		#### Main VMR-specific code ends here. ####################################################
		return output

	def run_allConditions_and_aggregate(self,cur_paraSet):
		columns = ["subcondition_name","mainCondi_name","questionProbe",
		"PTS","targetPosition","QIP","ASP","TNS","p_correct_sim"]
		res_df = pd.DataFrame(columns=columns)
		for sub_condi_name in self.sub_condi_names:
			targetPosition = sub_condi_name[2]
			ASP = sub_condi_name[len(sub_condi_name)-1]
			PTS = sub_condi_name[0]
			TNS = "low" if TNS=="l" else "high"
			mainCondi_name = PTS + str(targetPosition) + "_" + TNS + "_" + str(ASP)
			result_subcondi = self.tTCM_running_subcondition(cur_paraSet,sub_condi_name)
			p_correct_sim_subcondi = result_subcondi.get("p_correct_sim")
			res_df.loc[len(res_df.index)] = [sub_condi_name,mainCondi_name,
			PTS,targetPosition,QIP,ASP,TNS,p_correct_sim_subcondi]
			result_subcondi = self.tTCM_running_subcondition(cur_paraSet,sub_condi_name)
			p_correct_subcondi = result_subcondi.get("p_correct_SorD")
			res_df.loc[len(res_df.index)] = [sub_condi_name,mainCondi_name,
			PTS,targetPosition,QIP,ASP,TNS,p_correct_sim_subcondi]
		p_correct_sim_array = []
		for x in self.main_condi_names:
			name_vec = res_df.mainCondi_name
			x_rows = np.where(name_vec==x)
			x_data = res_df.iloc[x_rows]
			x_mean = np.mean(x_data.p_correct_sim)
			p_correct_SorD_array.append(x_mean)
		output = {
		"p_correct_SorD": np.array(p_correct_sim_array)
		}
		return output 

class search_parameter_space:
	def __init__(self,nfreePar):
		self.nfreePar = nfreePar
		self.D = prepare()
		
	def evaluateFit(self,cur_paraSet):
		nfreePar = self.nfreePar
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
		p_correct_sim = output_sim.get("p_correct_sim")
		nDataPoints = len(p_correct_sim)

		N_responses_total = 10*48*3 # = 1440; Nn = 10 subjects, 48 conditions*3 repetitions  
		N_responses_perSubject = N_responses_total/10 # = 480
		N_responses_perMainCondition = N_responses_total/8
		
		p_correct_emp = inputData.get("p_correct_emp")
		Mean_p_correct_emp = np.mean(p_correct_SorD_emp)
		RMSE_p_correct = np.sqrt(np.mean(np.power(np.subtract(p_correct_emp,p_correct_sim),2)))
		NRMSE_p_correct = RMSE_p_correct/Mean_p_correct_emp
		RSS = np.sum(np.power(np.subtract(p_correct_emp,p_correct_sim),2))
		BIC = nfreePar*np.log(nDataPoints) + nDataPoints*np.log(RSS/nDataPoints)
		# NRMSE = NRMSE_p_correct_SorD
		chi2_crit = st.chi2.ppf(q=.95, df=nDataPoints)
		chi2_tabl = np.vstack((p_correct_emp*N_responses_perMainCondition,p_correct_sim*N_responses_perMainCondition))
		colSum = chi2_tabl.sum(0); rowSum = chi2_tabl.sum(1)
		N = np.sum(colSum)
		chi2_pred = np.outer(rowSum,colSum)/N
		chi2 = np.sum(((chi2_tabl-chi2_pred)**2)/chi2_pred)
		chi2_p_crit = 1-st.chi2.cdf(x=chi2_crit,df=(nDataPoints - self.nfreePar))
		chi2_p = 1-st.chi2.cdf(x=chi2,df=(nDataPoints - self.nfreePar))
		# chi2_added = chi2_SorD
		# chi2_crit_added = st.chi2.ppf(q=.95, df=(nDataPoints - nfreePar))
		# chi2_p_crit_added = 1-st.chi2.cdf(x=chi2_crit_added,df=(nDataPoints - nfreePar))
		# chi2_p_added = 1-st.chi2.cdf(x=chi2_added,df=(nDataPoints-nfreePar))
		output = {
			"Results on Same/Different task": "p_correct",
			"p_correct_emp": np.around(p_correct_emp,3),
			"p_correct_sim": np.around(p_correct_sim,3),
			"Number of data points": nDataPoints,
			"nPar": nfreePar,
			"NRMSE": NRMSE_p_correct,
			"RSS": RSS_SorD,
			"BIC": BIC_SorD,
			"chi2": chi2,
			"chi2_p_crit": chi2_p_crit,
			"chi2_p": chi2_p
			# "chi2_added": chi2_added,
			# "chi2_crit_added": chi2_crit_added,
			# "chi2_p_added": chi2_p_added
		}
		
		return output

	def linkTofMinSearch(self,cur_algoString):
		global initSearch, start_time, interim, n_interims
		if initSearch==True:
			print()
			print("Searching space ...")
			initSearch=False
		pred = self.evaluateFit(cur_algoString)
		chi2 = pred.get("chi2")
		NRMSE = pred.get("NRMSE_p_correct")
		RSS = pred.get("RSS")
		if np.min(np.array(NRMSE_trace))>NRMSE:
			NRMSE_trace.append(NRMSE)
			print("... best fitting set thus far, based on NRMSE: " + str(np.around(cur_algoString,3)));
		if np.min(np.array(chi2_trace))>chi2:
			chi2_trace.append(chi2)
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
		return chi2


		
# #################################################################################################################

# #### Applying classes and functions #############################################################################


# ###### Testing classes and functions ############################################################################

prep = prepare()
prep.inputData()

print()
condi_name_input = input("""

	Which experimental condition?
	
	"S1_low_x"
	"S2_low_x"
	"D1_low_x"
	"D2_low_x"
	"S1_high_x"
	"S2_high_x"
	"D1_high_x"
	"D2_high_x"

	where x ranges between 1 and 6

	""")

prep = prepare()
inputData = prep.inputData()
Temp_scalar = inputData.get("Temp_scalar")
res_emp = inputData.get("res_emp")
F_features = inputData.get("F_features")
C_features = inputData.get("C_features")
Conditions = inputData.get("conditions")
main_condi_names = inputData.get("main_condi_names")
sub_condi_names = inputData.get("sub_condi_names")
M = generateData(Temp_scalar,F_features,C_features,Conditions,main_condi_names,sub_condi_names)
M.tTCM_running_subcondition(cur_paraSet = [.9,.9,.9],
	condi_name=condi_name_input,"P = T1?")
####


# # print()
# # S = search_parameter_space(nfreePar=3,nfreePar=2)
# # S.evaluateFit([0.57115471,0.66102614,0.76251886,0.5,0.6099648,0.])

# # #########################################################################################################################

# # ###### Searching parameter space and evaluating model fit  ##############################################################
# initSearch = True
# start_time = time.time()
# interim = start_time
# n_interims = 0
# NRMSE_trace = [1000000]
# chi2_trace = [1000000]
# S = search_parameter_space(nfreePar=2)
# xopt = so.minimize(fun=S.linkTofMinSearch, method='L-BFGS-B',
# ## Start values
# x0=[ .5, .5],
# bounds=[ (.05,1), (.05,1)])
# best_paraSet = xopt.get("x")
# print()
# print("... completed.")
# print()
# print("Optimization procedure converged?")
# print(xopt.get("success"))
# print()
# print("Best set of searched parameter values:")
# print()
# print(best_paraSet)
# pred_and_eval_given_bestParaSet = S.evaluateFit(best_paraSet)
# print()
# print("Same/Different frequencies observed (first row) vs. simulated (second row):")
# print(pred_and_eval_given_bestParaSet.get("p_correct_emp"))
# print(pred_and_eval_given_bestParaSet.get("p_correct_sim"))
# print("Chi2 value (and critical value): ")
# print(pred_and_eval_given_bestParaSet.get("chi2"))
# print(pred_and_eval_given_bestParaSet.get("chi2_crit"))
# print()
# print("RSS (Same / Different): ")
# print(pred_and_eval_given_bestParaSet.get("RSS"))
# print()
# print("BIC (Same / Different): ")
# print(pred_and_eval_given_bestParaSet.get("BIC"))
# print()
# print("NRMSE: ")
# print(pred_and_eval_given_bestParaSet.get("NRMSE"))


	
