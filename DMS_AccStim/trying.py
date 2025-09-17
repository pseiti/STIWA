import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson
from scipy.stats import norm
from scipy.stats import vonmises

t = """You did well. """ +str(.45*100) + """ percent correct. Lovely."""

v = np.arange(0,1000,36)
v_mod = np.mod(v,36)

a = np.arange(0,10,.1)

b = "hello"

c = ["a","b"]
d = ["c","d","1"]

# print("S"+"1"+"_"+"low"+"_"+"1")
p_correct_emp = {
		"S_low_111_1":[0.6975309, 0.3899896],
		"S_low_211":[0.7438272, 0.1788260],
		"S_low_121":[0.7191358, 0.3069553],
		"S_low_112":[0.6697531, 0.3987936],
		"S_low_122":[0.7561728, 0.2892685],
		"S_low_212":[0.8333333, 0.1666667],
		"S_low_221":[0.6759259, 0.2620550],
		"S_low_222":[0.8271605, 0.1481481],
		"S_high_111":[0.5740741, 0.3908680],
		"S_high_211":[0.4475309, 0.2455014],
		"S_high_121":[0.6851852, 0.3424674],
		"S_high_112":[0.4351852, 0.5400617],
		"S_high_122":[0.4104938, 0.4758395],
		"S_high_212":[0.8302469, 0.1598396],
		"S_high_221":[0.5061728, 0.4814815],
		"S_high_222":[0.7469136, 0.1865689]
		}
m = list(p_correct_emp.keys())
d = {"m":m,"t":t}
e = [0]
e1 = [np.nan,0]
print(any(np.isnan(e)))
d = ["c","d","1"]
print(d[:-1])
print(d[-2])
print(b[-4])
a = np.repeat(.8,4)
b = 100
print(np.concatenate(a,b))
print(.3 in a)
print(np.max([.1,.2,.3]))
print(np.append(a,.1))
print(np.repeat([9,1],2))





