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
from scipy.stats import chi2
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
		# _111_ targetPosition, ASP, QIP 
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
		Temp_range_max = 600
		C_features = np.arange(Temp_range_min,Temp_range_max,7)
		Temp_scalar = np.array([65,265,465,565]) 
		main_condi_names = [
		"S_low_111",
		"S_low_211","S_low_121","S_low_112",
		"S_low_122","S_low_212","S_low_221","S_low_222",
		"S_high_111",
		"S_high_211","S_high_121","S_high_112",
		"S_high_122","S_high_212","S_high_221","S_high_222"]
		sub_condi_names = list(conditions.keys())
		N_sample = 20
		p_correct_emp_dict = {
		"S_low_111":[0.7398990, 0.3083143],
		"S_low_211":[0.7285354, 0.3088366],
		"S_low_121":[0.7790404, 0.2479305],
		"S_low_112":[0.6931818, 0.3715402],
		"S_low_122":[0.7234848, 0.3397181],
		"S_low_212":[0.8358586, 0.1594351],
		"S_low_221":[0.7108586, 0.2601071],
		"S_low_222":[0.8333333, 0.1635511],
		"S_high_111":[0.6186869, 0.3096980],
		"S_high_211":[0.5164141, 0.3512239],
		"S_high_121":[0.6540404, 0.3047400],
		"S_high_112":[0.3851010, 0.4637265],
		"S_high_122":[0.3901515, 0.4802444],
		"S_high_212":[0.8295455, 0.1966607],
		"S_high_221":[0.4343434, 0.4416700],
		"S_high_222":[0.7752525, 0.2487342]
		}
		emp_values = list(p_correct_emp_dict.values())
		p_correct_emp_Means = []
		for x in range(len(emp_values)):
			p_correct_emp_Means.append(emp_values[x][0])
		N_responses_SorD = np.nan
		# Names of steps of rating scale: Sure - lessSure - Unsure - Unsure - lessSure – Sure
		output = {"conditions": conditions, "Temp_scalar": Temp_scalar, "F_features": F_features, "C_features": C_features,
		"main_condi_names": main_condi_names, "sub_condi_names": sub_condi_names,
		"p_correct_emp_dict":p_correct_emp_dict,"p_correct_emp_Means": p_correct_emp_Means,"N_sample":N_sample}

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
		self.D = prepare()
	
	def fx_encoding(self,f_i,Beta,c_i,cIN,bindings,MFC,MCF,gamma_FC,gamma_CF):
		if any(np.isnan(c_i)):
			c_i = cIN
		else:
			c_prev = c_i
			rho_i = self.D.rho_fx(c_prev,cIN,Beta)
			# print()
			# print("rho: / beta:")
			# print(rho_i)
			# print(Beta)
			c_i = np.add((rho_i*c_prev),(Beta*cIN))
		if bindings:
			delta_MFC = gamma_FC*np.outer(c_i,f_i)
			# MFC = w_FC*MFC + (1-w_FC)*delta_MFC
			MFC = (1-gamma_FC)*MFC + delta_MFC
			delta_MCF = gamma_CF*np.outer(f_i,c_i)
			# MCF = w_CF*MCF + (1-w_CF)*delta_MCF
			MCF = (1-gamma_CF)*MCF + delta_MCF
		d = {"c_i":c_i,"MFC":MFC,"MCF":MCF}
		return d

	def tTCM_running_subcondition(self,cur_paraSet,condi_name):
		# D = prepare()
		inputData = self.D.inputData()
		res_emp = inputData.get("res_emp")
		# S_high_111_1 # # 111 = targetPosition, QIP, ASP
		PTS = condi_name[0]
		targetPosition = int(condi_name[-5])
		ASP = int(condi_name[-4])
		QIP = int(condi_name[-3])
		TNS = "low" if condi_name[2]=="l" else "high"
		questionType = "="
		parDict = {
			# "Beta_AS": cur_paraSet[0],
			# "Beta_ListItem1": cur_paraSet[1],
			# "Beta_ListItem2": cur_paraSet[1],
			# "Beta_Probe": cur_paraSet[3],
			# "Beta_retrvl": cur_paraSet[4],
			# "g": cur_paraSet[5]

			"Beta_AS": cur_paraSet[0],
			"Beta_ListItem_low": cur_paraSet[1],
			"Beta_ListItem_high": cur_paraSet[2],
			"Beta_Probe_low": cur_paraSet[3],
			"Beta_Probe_high": cur_paraSet[4],
			"Beta_retrvl": cur_paraSet[5],
			"gamma_FC": cur_paraSet[6],
			"gamma_CF": cur_paraSet[7],
			"w_0": cur_paraSet[8],
			"w_2": cur_paraSet[9]

			# "gamma_FC": cur_paraSet[6],
			# "gamma_CF": cur_paraSet[7]
			#"g": cur_paraSet[6]
			# "w_FC": cur_paraSet[5],
			# "w_CF": cur_paraSet[6]
			# "Beta_AS_low": cur_paraSet[0],
			# "Beta_AS_high": cur_paraSet[1],
			# "Beta_listItem_low": cur_paraSet[2],
			# "Beta_listItem_high": cur_paraSet[3],
			# "Beta_Probe_low": cur_paraSet[4],
			# "Beta_Probe_high": cur_paraSet[5],
			# "Beta_retrvl_low": cur_paraSet[6],
			# "Beta_retrvl_high": cur_paraSet[7]
		}
		Hz_scalar = np.array(self.conditions[condi_name])
		# Hz-layer F encoding
		item1_Hz = self.D.norm_fx(poisson.pmf(self.F_features, mu = Hz_scalar[0]))
		item2_Hz = self.D.norm_fx(poisson.pmf(self.F_features, mu = Hz_scalar[1]))
		P_Hz = self.D.norm_fx(poisson.pmf(self.F_features, mu = Hz_scalar[2]))
		Hz_distributed = np.array([item1_Hz,item2_Hz,P_Hz])

		# plt.plot(item1_Hz,"k-",label="f1")
		# plt.plot(item2_Hz,"b-",label="f2")
		# plt.plot(P_Hz,"r-",label="fP")
		# lastxTick = self.F_features[len(self.F_features)-1]
		# medxTick = self.F_features[int(np.around((len(self.F_features)-1)/2))]
		# plt.xticks([0,np.around((len(self.F_features)-1)/2),
		# 	len(self.F_features)-1],[1,medxTick,lastxTick+1])
		# plt.title(condi_name + str(Hz_scalar[0]))

		# Temporal layer T encoding
		Temp_scalar = self.Temp_scalar.astype(float)
		context1 = self.D.norm_fx(poisson.pmf(self.C_features, mu = self.Temp_scalar[0]))
		context2 = self.D.norm_fx(poisson.pmf(self.C_features, mu = self.Temp_scalar[1]))
		contextP = self.D.norm_fx(poisson.pmf(self.C_features, mu = self.Temp_scalar[2]))
		
		# plt.plot(context1,"k-",label="context_1")
		# # plt.ylim(0,1.5)
		# lastxTick = self.C_features[len(self.C_features)-1]
		# medxTick = self.C_features[int(np.around((len(self.C_features)-1)/2))]
		# plt.xticks([0,np.around((len(self.C_features)-1)/2),
		# 	len(self.C_features)-1],[1,medxTick,lastxTick+1])
		# plt.plot(context2,"b-",label="context_2")
		# plt.plot(contextP,"r-",label="context_P")
		
		context_AS1 = self.D.norm_fx(poisson.pmf(self.C_features, mu = 50)) # 60 AS = Accessory Stimulus
		context_AS2 = self.D.norm_fx(poisson.pmf(self.C_features, mu = 250)) #260
		Temp_distributed = np.array([context1,context2,contextP])
		context_AS_array = np.array([context_AS1,context_AS2])
		# Preparing 'mental structure' of item-context and context-item associations
		MFC = np.zeros(len(item1_Hz)*len(context1)).reshape((len(context1),len(item1_Hz)))
		MCF = np.zeros(len(item1_Hz)*len(context1)).reshape((len(item1_Hz),len(context1)))
		##### Encoding of the two list items (and click)
		AS_1or2 = [1,0] if ASP==1 else [0,1]
		color_and_lineType_plot = ["k--","b--","m--"]
		for item_i in range(2):
			# Start item encoding
			f_i = Hz_distributed[item_i]
			# Conditional AS encoding
			# Beta = parDict.get("Beta_AS") # parDict.get("Beta_AS_low") if TNS=="low" else parDict.get("Beta_AS_high")
			if AS_1or2[item_i]==1:
				cIN=context_AS_array[item_i]
				if item_i==0:
					outcome_encoding = self.fx_encoding(
						f_i=np.nan,Beta=np.nan,c_i=[np.nan],cIN=cIN,
						gamma_FC=parDict.get("gamma_FC"),gamma_CF=parDict.get("gamma_CF"),
						bindings=False,MFC=np.nan,MCF=np.nan)
				else:
					outcome_encoding = self.fx_encoding(
						f_i=np.nan,Beta=parDict.get("Beta_AS"),c_i=c_i,cIN=cIN,
						gamma_FC=parDict.get("gamma_FC"),gamma_CF=parDict.get("gamma_CF"),
						bindings=False,MFC=np.nan,MCF=np.nan)
				c_i=outcome_encoding.get("c_i")
				
			# Continue item encoding
			Beta = parDict.get("Beta_ListItem_low") if TNS=="low" else parDict.get("Beta_ListItem_high")
			cIN = Temp_distributed[item_i]
			if AS_1or2[item_i]==0 & item_i==0:
				outcome_encoding = self.fx_encoding(
					f_i=f_i,Beta=Beta,c_i=[np.nan],cIN=cIN,
					gamma_FC=parDict.get("gamma_FC"),gamma_CF=parDict.get("gamma_CF"),
					bindings=True,MFC=MFC,MCF=MCF)
			else:
				outcome_encoding = self.fx_encoding(
					f_i=f_i,Beta=Beta,c_i=c_i,cIN=cIN,
					gamma_FC=parDict.get("gamma_FC"),gamma_CF=parDict.get("gamma_CF"),
					bindings=True,MFC=MFC,MCF=MCF)

			c_i=outcome_encoding.get("c_i")
			
			# plt.plot(c_i,color_and_lineType_plot[item_i],label="c_i_ListItem_"+str(int(item_i)))
			
			MFC=outcome_encoding.get("MFC")
			MCF=outcome_encoding.get("MCF")
		
		##### Probe encoding
		f_i = Hz_distributed[2]
		cIN = Temp_distributed[2]
		Beta = parDict.get("Beta_Probe_low") if TNS=="low" else parDict.get("Beta_Probe_high")
		for cycle_x in range(2):
			outcome_encoding = self.fx_encoding(
				f_i=f_i,Beta=Beta,c_i=c_i,cIN=cIN,
				gamma_FC=parDict.get("gamma_FC"),gamma_CF=parDict.get("gamma_CF"),
				bindings=True,MFC=MFC,MCF=MCF)
			c_i=outcome_encoding.get("c_i")
			MFC=outcome_encoding.get("MFC")
			MCF=outcome_encoding.get("MCF")
		
		# plt.plot(c_i,color_and_lineType_plot[item_i+1],label="c_i_Probe")
		##### Responding ###################################
		# question-prompt-based item retrieval
		cIN = context1 if QIP==1 else context2
		fIN = self.D.norm_fx(np.inner(MCF,cIN))
		# ### Part of code modeling  1/2-judgment 
		cIN = self.D.norm_fx(np.inner(MFC,fIN))
		# plt.plot(fIN,"b--")
		# plt.show()
		# plt.plot(cIN,"g--",label="cIN (QIP-based Hz-to-time retrieval)")
		# plt.show()

		Beta = parDict.get("Beta_retrvl")# parDict.get("Beta_retrvl_low") if TNS=="low" else parDict.get("Beta_retrvl_high")
		outcome_encoding = self.fx_encoding(
			f_i=np.nan,Beta=Beta,c_i=c_i,cIN=cIN,
			gamma_FC=parDict.get("gamma_FC"),gamma_CF=parDict.get("gamma_CF"),
			bindings=False,MFC=np.nan,MCF=np.nan)
		c_i=outcome_encoding.get("c_i")
		# plt.matshow(MFC)
		# plt.plot(c_i,"m-",label="c_i with cIN cincluded (densities)")
		# plt.legend()
		# plt.title(condi_name)
		# plt.show()

		increasing = True
		nTurningPoints = 0
		Positions_TurningPoints = []
		for x in np.arange(1,len(c_i)-1):
			if c_i[x]<c_i[x+1]:
				if increasing==False:
					increasing=True
					nTurningPoints+=1
					
					# plt.axvline(x=x)
					
					Positions_TurningPoints.append(x)
			elif c_i[x]>c_i[x+1]:
				if increasing==True:

					# plt.axvline(x=x)

					increasing=False
					nTurningPoints+=1
					Positions_TurningPoints.append(x)
		# plt.show()
		
		if len(Positions_TurningPoints)<5:
			# print("here")
			p_correct=10
		else:
			# print("here2")
			densities = [0,0,0]
			for x in range(len(c_i)-1):
				if x < Positions_TurningPoints[1]:
					densities[0] += c_i[x]
				elif Positions_TurningPoints[1] <= x < Positions_TurningPoints[3]:
					densities[1] += c_i[x]
				elif x >= Positions_TurningPoints[3]:
					densities[2] += c_i[x]
			#densities_p = np.divide(densities,np.sum(densities))
			densities_p = np.divide(densities[:2],np.sum(densities[:2]))
			densities_p_2 = np.divide(densities,np.sum(densities))
			A = densities_p[0]
			B = densities_p[1]

			# plt.legend()
			# plt.show()	
			# print()
			# print("Turning points:")
			# print(Positions_TurningPoints)
			# print("Densities:")
			# print(densities)
			# print(densities_p)
			# print(densities_p_2)
			# print()
			
			# g = parDict.get("g_low") if TNS=="low" else parDict.get("g_high")
			p_correct = A*(1-B) + B*(1-A) + (1-A)*(1-B)*parDict.get("w_0") * A*B*parDict.get("w_2")
			# if targetPosition==1:
			# 	p_correct = A*(1-B) + g
			# else:
			# 	p_correct = B*(1-A) + g
			# if p_correct>1:
			# 	p_correct=1
		p_correct_1or2 = p_correct
		output = {
		"p_correct_sim": p_correct_1or2,
		"parameterNames": parDict.keys()
		}
		# mainCondi_name = condi_name[:-2]
		# print()
		# print("Observed: " + condi_name)
		# print(np.around(inputData.get("p_correct_emp_dict").get(mainCondi_name),3))
		# print("Simulated:")
		# print(np.around(output.get("p_correct_sim"),3))
		# print()
		return output

	def run_allConditions_and_aggregate(self,cur_paraSet):
		columns = ["subCondi_name","mainCondi_name",
		"PTS","targetPosition","QIP","ASP","TNS","p_correct_sim"]
		res_df = pd.DataFrame(columns=columns)
		for sub_condi_name in self.sub_condi_names:
			targetPosition = sub_condi_name[len(sub_condi_name)-3]
			ASP = sub_condi_name[len(sub_condi_name)-2]
			QIP = sub_condi_name[len(sub_condi_name)-1]
			PTS = sub_condi_name[0]
			TNS = "low" if sub_condi_name[2]=="l" else "high"
			mainCondi_name = sub_condi_name[:-2]
			result_subcondi = self.tTCM_running_subcondition(cur_paraSet,sub_condi_name)
			p_correct_sim_subcondi = result_subcondi.get("p_correct_sim")
			res_df.loc[len(res_df.index)] = [sub_condi_name,mainCondi_name,
			PTS,targetPosition,QIP,ASP,TNS,p_correct_sim_subcondi]
		p_correct_sim_array = []
		for x in self.main_condi_names:
			name_vec = res_df.mainCondi_name
			x_rows = np.where(name_vec==x)
			x_data = res_df.iloc[x_rows]
			x_mean = np.mean(x_data.p_correct_sim)
			p_correct_sim_array.append(x_mean)
		output = {
		"p_correct_sim": np.array(p_correct_sim_array),
		"parameterNames": result_subcondi.get("parameterNames")
		}
		### For testing only ###
		# inputData = self.D.inputData()
		# print()
		# print(inputData.get("main_condi_names")[:8])
		# print("Empirical (TNS=Low):")
		# print(np.around(inputData.get("p_correct_emp_Means")[:8],2))
		# print("Simulated:")
		# print(np.around(output.get("p_correct_sim"),2)[:8])
		# print("Empirical (TNS=high)")
		# print(np.around(inputData.get("p_correct_emp_Means")[8:],2))
		# print("Simulated:")
		# print(np.around(output.get("p_correct_sim"),2)[8:])
		# print()
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
		p_correct_sim = output_sim.get("p_correct_sim") # [8:]
		N_sample = inputData.get("N_sample")
		N_conditions = len(main_condi_names)
		N_responses_total = N_sample*N_conditions*3 # = 1440; Nn = 10 subjects, 16 conditions*3 repetitions  
		N_responses_perSubject = int(N_responses_total/N_sample) # = 480
		N_responses_perMainCondition = int(N_responses_total/N_conditions)
		p_correct_emp_Means = np.array(inputData.get("p_correct_emp_Means")) # [8:]
		Mean_p_correct_emp = np.mean(p_correct_emp_Means)
		RMSE_p_correct = np.sqrt(np.mean(np.power(np.subtract(p_correct_emp_Means,p_correct_sim),2)))
		NRMSE_p_correct = RMSE_p_correct/Mean_p_correct_emp
		RSS = np.sum(np.power(np.subtract(p_correct_emp_Means,p_correct_sim),2))
		nDataPoints = len(p_correct_emp_Means)
		BIC = nfreePar*np.log(nDataPoints) + nDataPoints*np.log(RSS/nDataPoints)
		chi2_crit = st.chi2.ppf(.95, df=(nDataPoints-self.nfreePar)) # https://stackoverflow.com/questions/60423364/how-to-calculate-the-critical-chi-square-value-using-python
		chi2_tabl = np.vstack((p_correct_emp_Means*N_responses_perMainCondition,p_correct_sim*N_responses_perMainCondition))
		colSum = chi2_tabl.sum(0); rowSum = chi2_tabl.sum(1)
		N_chi2 = np.sum(colSum)
		chi2_pred = np.outer(rowSum,colSum)/N_chi2
		chi2 = np.sum(((chi2_tabl-chi2_pred)**2)/chi2_pred)
		chi2_p_crit = 1-st.chi2.cdf(x=chi2_crit,df=(nDataPoints - self.nfreePar))
		chi2_p = 1-st.chi2.cdf(x=chi2,df=(nDataPoints - self.nfreePar))
		output = {
			"Results on Same/Different task": "p_correct",
			"p_correct_emp": np.around(p_correct_emp_Means,3),
			"p_correct_sim": np.around(p_correct_sim,3),
			"Number of data points": nDataPoints,
			"nPar": nfreePar,
			"RMSE": RMSE_p_correct,
			"NRMSE": NRMSE_p_correct,
			"RSS": RSS,
			"BIC": BIC,
			"chi2": chi2,
			"chi2_crit": chi2_crit,
			"chi2_p": chi2_p
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
		RMSE = pred.get("RMSE")
		RSS = pred.get("RSS")
		BIC = pred.get("BIC")
		if np.min(np.array(RMSE_trace))>RMSE:
			RMSE_trace.append(RMSE)
			print("... best fitting set thus far, based on RMSE: " + str(np.around(cur_algoString,3)));
		if np.min(np.array(chi2_trace))>chi2:
			chi2_trace.append(chi2)
			print("... best fitting set thus far, based on Chi2: " + str(np.around(cur_algoString,3)));
			
			# if (chi2_trace[-2]-chi2_trace[-1])>1:
			# 	plt.plot(pred.get("p_correct_sim"),"k--",label="Simulated")
			# 	plt.xlim(0,16)
			# 	plt.ylim(0,1.4)
			# 	plt.plot(pred.get("p_correct_emp"),"k",label="observed")
			# 	plt.legend()
			# 	plt.show()

		if np.min(np.array(RSS_trace))>RSS:
			RSS_trace.append(RSS)
			print("... best fitting set thus far, based on RSS: " + str(np.around(cur_algoString,3)));
		if np.min(np.array(BIC_trace))>BIC:
			BIC_trace.append(BIC)
			print("... best fitting set thus far, based on BIC: " + str(np.around(cur_algoString,3)));
		dur_since_lastMessage = time.time() - interim
		dur_total = time.time() - start_time

		if dur_since_lastMessage > 10: # Sekunden
			print()
			print("... for " + str(round(dur_total)) + " seconds, RMSE: " + str(np.around(np.min(RMSE_trace),3)))
			print()
			# print("... for " + str(round(dur_total)) + " seconds, RSS: " + str(np.around(np.min(RSS_trace),3)))
			# print()
			print("... for " + str(round(dur_total)) + " seconds, Chi2: " + str(np.around(np.min(chi2_trace),3)))
			print()
			# print("... for " + str(round(dur_total)) + " seconds, BIC: " + str(np.around(np.min(BIC_trace),3)))
			# print()
			interim = time.time()
			n_interims += 1
		return RMSE


		
# #################################################################################################################

# #### Applying classes and functions #############################################################################


# ###### Testing classes and functions ############################################################################

prep = prepare()
prep.inputData()

def parameterTesting_subcondition():
	print()
	condi_name_input = input("""

		Which experimental condition?
		
		S_low_111_x
		S_low_211_x
		S_low_121_x
		S_low_112_x
		S_low_122_x
		S_low_212_x
		S_low_221_x
		S_low_222_x
		S_high_111_x
		S_high_211_x
		S_high_121_x
		S_high_112_x
		S_high_122_x
		S_high_212_x
		S_high_221_x
		S_high_222_x

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
	"S_low_111",
	"S_low_211","S_low_121","S_low_112",
	"S_low_122","S_low_212","S_low_221","S_low_222",
	"S_high_111",
	"S_high_211","S_high_121","S_high_112",
	"S_high_122","S_high_212","S_high_221","S_high_222"
	M.tTCM_running_subcondition(cur_paraSet = [0.98536525,0.99999912,0.98968058,0.09265353,
		0.99743678,0.99082615,0.22892641,0.97378066,0.5,0.5],
		condi_name=condi_name_input)

###

# print()
# S = search_parameter_space(nfreePar=8)
# S.evaluateFit(np.repeat(.5,8))

# # #########################################################################################################################

# ###### Searching parameter space and evaluating model fit  ##############################################################
D = prepare()
inputData = D.inputData()
mainCondiNames = inputData.get("main_condi_names")
initSearch = True
start_time = time.time()
interim = start_time
n_interims = 0
RMSE_trace = [10]
chi2_trace = [10000]
RSS_trace = [10]
BIC_trace = [100]
def searchParaSpace():
	global nfreePar	
	nfreePar = 8
	S = search_parameter_space(nfreePar=nfreePar)
	xopt = so.minimize(fun=S.linkTofMinSearch, method='L-BFGS-B',
	x0 = [.5,.5,.5,.5,.5,.5,.5,.5,.5,.5],
	bounds=[(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(.01,1),(.01,1),(.5,.5),(.5,.5)])
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
	print("Same/Different frequencies observed (first two rows) vs. simulated (third and fourth row):")
	print("#### Empirical / TNS=low ####")
	print(mainCondiNames[:10])
	dps_1to8_emp = pred_and_eval_given_bestParaSet.get("p_correct_emp")[:8]
	print(dps_1to8_emp)
	print("#### Simulated ####")
	dps_1to8_sim = pred_and_eval_given_bestParaSet.get("p_correct_sim")[:8]
	print(dps_1to8_sim)
	plt.plot(dps_1to8_emp,'bs-')
	plt.plot(dps_1to8_sim,'bo--')
	print("#### Empirical / TNS=high ####")
	print(mainCondiNames[10:])
	dps_9to16_emp = pred_and_eval_given_bestParaSet.get("p_correct_emp")[8:]
	print(dps_9to16_emp)
	print("#### Simulated ####")
	dps_9to16_sim = pred_and_eval_given_bestParaSet.get("p_correct_sim")[8:]
	print(dps_9to16_sim)
	print()
	plt.plot(dps_9to16_emp,'rs-')
	plt.plot(dps_9to16_sim,'ro--')
	plt.ylim(0,1.1)
	plt.xticks([0,1,2,3,4,5,6,7],
		["S_111","S_211","S_121","S_112","S_122","S_212","S_221","S_222"])
	print("#### Goodness-of-fit measures ####")
	print("Chi2 test (chi2, chi2_crit, p): ")
	print(pred_and_eval_given_bestParaSet.get("chi2"))
	print(pred_and_eval_given_bestParaSet.get("chi2_crit"))
	print(pred_and_eval_given_bestParaSet.get("chi2_p"))
	print()
	print("RSS: ")
	print(pred_and_eval_given_bestParaSet.get("RSS"))
	print()
	print("BIC: ")
	print(pred_and_eval_given_bestParaSet.get("BIC"))
	print()
	print("RMSE: ")
	print(pred_and_eval_given_bestParaSet.get("RMSE"))
	print()
	plt.xlabel("Condition")
	plt.ylabel("Percent correct")
	plt.show()

####

# parameterTesting_subcondition()
searchParaSpace()


