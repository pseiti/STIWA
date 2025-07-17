
import random 

# conditions

unique_conditions_ST1 = [
{'ST1_low_1_a1':[82,132,82]},{'ST1_low_2_a1':[132,82,132]},{'ST1_low_3_a1':[70,112,70]},
{'ST1_low_4_a1':[112,70,112]},{'ST1_low_5_a1':[96,154,96]},{'ST1_low_6_a1':[154,96,154]},
{'ST1_high_1_a1':[82,112,82]},{'ST1_high_2_a1':[112,82,112]},{'ST1_high_3_a1':[70,96,70]},
{'ST1_high_4_a1':[96,70,96]},{'ST1_high_5_a1':[96,132,96]},{'ST1_high_6_a1':[132,96,132]},

{'ST1_low_1_a2':[82,132,82]},{'ST1_low_2_a2':[132,82,132]},{'ST1_low_3_a2':[70,112,70]},
{'ST1_low_4_a2':[112,70,112]},{'ST1_low_5_a2':[96,154,96]},{'ST1_low_6_a2':[154,96,154]},
{'ST1_high_1_a2':[82,112,82]},{'ST1_high_2_a2':[112,82,112]},{'ST1_high_3_a2':[70,96,70]},
{'ST1_high_4_a2':[96,70,96]},{'ST1_high_5_a2':[96,132,96]},{'ST1_high_6_a2':[132,96,132]}

]
unique_conditions_ST2 = [
{'ST2_low_1_a2':[82,132,132]},{'ST2_low_2_a2':[132,82,82]},{'ST2_low_3_a2':[70,112,112]},
{'ST2_low_4_a2':[112,70,70]},{'ST2_low_5_a2':[96,154,154]},{'ST2_low_6_a2':[154,96,96]},
{'ST2_high_1_a2':[82,112,112]},{'ST2_high_2_a2':[112,82,82]},{'ST2_high_3_a2':[70,96,96]},
{'ST2_high_4_a2':[96,70,70]},{'ST2_high_5_a2':[96,132,132]},{'ST2_high_6_a2':[132,96,96]},

{'ST2_low_1_a1':[82,132,132]},{'ST2_low_2_a1':[132,82,82]},{'ST2_low_3_a1':[70,112,112]},
{'ST2_low_4_a1':[112,70,70]},{'ST2_low_5_a1':[96,154,154]},{'ST2_low_6_a1':[154,96,96]},
{'ST2_high_1_a1':[82,112,112]},{'ST2_high_2_a1':[112,82,82]},{'ST2_high_3_a1':[70,96,96]},
{'ST2_high_4_a1':[96,70,70]},{'ST2_high_5_a1':[96,132,132]},{'ST2_high_6_a1':[132,96,96]}
]
unique_conditions_D = [
{'DT1_low_1_a1':[82,132,70]},{'DT1_low_2_a1':[132,82,154]},{'DT1_low_3_a1':[70,112,60]},
{'DT1_low_4_a1':[112,70,132]},{'DT1_low_5_a1':[96,154,82]},{'DT1_low_6_a1':[154,96,180]},
{'DT1_high_1_a1':[82,112,70]},{'DT1_high_2_a1':[112,82,132]},{'DT1_high_3_a1':[70,96,60]},
{'DT1_high_4_a1':[96,70,112]},{'DT1_high_5_a1':[96,132,82]},{'DT1_high_6_a1':[132,96,154]},

{'DT2_low_1_a2':[82,132,154]},{'DT2_low_2_a2':[132,82,70]},{'DT2_low_3_a2':[70,112,132]},
{'DT2_low_4_a2':[112,70,60]},{'DT2_low_5_a2':[96,154,180]},{'DT2_low_6_a2':[154,96,82]},
{'DT2_high_1_a2':[82,112,132]},{'DT2_high_2_a2':[112,82,70]},{'DT2_high_3_a2':[70,96,112]},
{'DT2_high_4_a2':[96,70,60]},{'DT2_high_5_a2':[96,132,154]},{'DT2_high_6_a2':[132,96,82]},

{'DT1_low_1_a2':[82,132,70]},{'DT1_low_2_a2':[132,82,154]},{'DT1_low_3_a2':[70,112,60]},
{'DT1_low_4_a2':[112,70,132]},{'DT1_low_5_a2':[96,154,82]},{'DT1_low_6_a2':[154,96,180]},
{'DT1_high_1_a2':[82,112,70]},{'DT1_high_2_a2':[112,82,132]},{'DT1_high_3_a2':[70,96,60]},
{'DT1_high_4_a2':[96,70,112]},{'DT1_high_5_a2':[96,132,82]},{'DT1_high_6_a2':[132,96,154]},

{'DT2_low_1_a1':[82,132,154]},{'DT2_low_2_a1':[132,82,70]},{'DT2_low_3_a1':[70,112,132]},
{'DT2_low_4_a1':[112,70,60]},{'DT2_low_5_a1':[96,154,180]},{'DT2_low_6_a1':[154,96,82]},
{'DT2_high_1_a1':[82,112,132]},{'DT2_high_2_a1':[112,82,70]},{'DT2_high_3_a1':[70,96,112]},
{'DT2_high_4_a1':[96,70,60]},{'DT2_high_5_a1':[96,132,154]},{'DT2_high_6_a1':[132,96,82]}
]
unique_conditions_S = [
{'STb_1_a1':[60,60,60]},{'STb_2_a1':[70,70,70]},{'STb_3_a1':[82,82,82]},
{'STb_4_a1':[96,96,96]},{'STb_5_a1':[112,112,112]},{'STb_6_a1':[132,132,132]},
{'STb_7_a1':[154,154,154]},{'STb_8_a1':[180,180,180]},

{'STb_1_a2':[60,60,60]},{'STb_2_a2':[70,70,70]},{'STb_3_a2':[82,82,82]},
{'STb_4_a2':[96,96,96]},{'STb_5_a2':[112,112,112]},{'STb_6_a2':[132,132,132]},
{'STb_7_a2':[154,154,154]},{'STb_8_a2':[180,180,180]}
]

# frequency amplitudes

Hz_amp_mapping = {                        
    '60':1.778327198,
    '70':1.608381144,
    '82':1.426248320,
    '96':1.243820967,
    '112':1.074973366,
    '132':0.923375067,
    '154':0.832925483,
    '180':0.829096604
}


ordered_Hz = list(Hz_amp_mapping)
ordered_Amps = list(Hz_amp_mapping.values())

# variables

trial_template = {
    'question':0,
    'condition':0,
    'PTS':0,
    'TargetPosition':0,
    'AccessoryPosition':0,
    'TNS':0,
    'T1_hz':0,
    'T1_amp':0,
    'T2_hz':0,
    'T2_amp':0,
    'P_hz':0,
    'P_amp':0
}

# create dictionary with all trials

def dict_maker(unique_conditions,nRep):
    conditions = []
    for rep_x in range(nRep):
        for x in unique_conditions:
            x_condi_templ = trial_template.copy()
            x_condi_name = list(x)[0]
            S_or_D = x_condi_name[0]
            S_or_D = "Same" if S_or_D=="S" else "Different"
            AccessoryPosition = 1 if x_condi_name[-1]=="1" else 2
            
            if x_condi_name[2]=="1": 
                TargetPosition = 1 
            elif x_condi_name[2]=="2": 
                TargetPosition = 2
            else: 
                TargetPosition = 0

            if x_condi_name[4]=="h": 
                TNS = "high" 
            elif x_condi_name[4]=="l":
                TNS = "low"
            else: 
                TNS = "None"
            
            T1_hz = x[x_condi_name][0]
            T1_id = ordered_Hz.index(str(T1_hz))
            T1_amp = ordered_Amps[T1_id]
            T2_hz = x[x_condi_name][1]
            T2_id = ordered_Hz.index(str(T2_hz))
            T2_amp = ordered_Amps[T2_id]
            P_hz = x[x_condi_name][2]
            P_id = ordered_Hz.index(str(P_hz))
            P_amp = ordered_Amps[P_id]

            templ_update = {
                    'question':q, 'condition':x_condi_name, 'PTS':S_or_D,
                    'TargetPosition':TargetPosition, 'AccessoryPosition':AccessoryPosition, 'TNS':TNS,
                    'T1_hz':T1_hz, 'T1_amp': T1_amp, 'T2_hz':T2_hz, 'T2_amp':T2_amp, 'P_hz':P_hz, 'P_amp':P_amp
                    }
            x_condi_templ.update(templ_update)
            conditions.append(x_condi_templ)
    return conditions

# create lists of equal/unequal practice and main trials

conditions_eq_pract = []
conditions_eq = []
conditions_uneq_pract = []
conditions_uneq = []

questions = ["P = T1?", "P = T2?", "P != T1?", "P != T2?"]
for q in questions: 
    temp_ST1 = dict_maker(unique_conditions_ST1,1)  # 72 repetitions per question (36 per ST condition) (with two repetitions of each question block =/!=)
    temp_ST2 = dict_maker(unique_conditions_ST2,1) 
    temp_D = dict_maker(unique_conditions_D,1)
    temp_S = dict_maker(unique_conditions_S, 1)
    dict_list = [temp_ST1, temp_ST2, temp_D, temp_S]
    if " = " in q:
        for i in dict_list: 
            conditions_eq_pract.extend(random.sample(i,2)) 
        conditions_eq.extend(temp_ST1)
        conditions_eq.extend(temp_ST2)
        conditions_eq.extend(random.sample(temp_D,4)) # 8 distractor trials
        conditions_eq.extend(random.sample(temp_S,4)) # 8 distractor trials
    elif "!=" in q:
        for i in dict_list: 
            conditions_uneq_pract.extend(random.sample(i,2)) 
        conditions_uneq.extend(temp_ST1)
        conditions_uneq.extend(temp_ST2)
        conditions_uneq.extend(random.sample(temp_D,4)) # 8 distractor trials
        conditions_uneq.extend(random.sample(temp_S,4)) # 8 distractor trials
print(len(conditions_eq),len(conditions_uneq))
# print(len(conditions_eq),len(conditions_uneq))
# conditions_eq_pract = conditions_eq_pract[:10]
# conditions_eq = conditions_eq[:10]
# conditions_uneq_pract = conditions_uneq_pract [:10]
# conditions_uneq = conditions_uneq[:10]