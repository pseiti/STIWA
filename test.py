import numpy as np
import pandas as pd

columns = ["Track", "Name"]
df = pd.DataFrame(columns=columns)

i = 0
while True:
	i += 1
	name_i = np.random.choice(["Peter","Zoe"])
	df.loc[len(df.index),["Track","Name"]] = [i,name_i] 
	priorNames = df.Name
	nPeter = 0
	for x in priorNames:
		if x=="Peter":
			nPeter += 1
	if nPeter > 5:
		break

zeros = []
for x in range(10):
	zeros.append(x)

print(zeros[-3:])