#!/usr/bin/python3

import os
import sys
import pandas

def runMutPred(fastaFile,mutations):
	os.chdir("/home/ibab/automutation")
	#To edit the FASTA file as required for MutPred2.0
	sequence = ""
	with open(fastaFile,"r") as f1:
		header = f1.readline().split()[0]
		f1.seek(0)
		seq = f1.readlines()[1:]
	f1.close()
	sequence = "".join(seq)
	with open(mutations,"r") as mutFile:
		mutations = mutFile.readlines()
	mutFile.close()
	mutList = [x.split('\n')[0] for x in mutations]
	muts = " "
	mutAll = muts.join(mutList)
	try:
		os.chdir("/home/ibab/automutation/mutpred2.0")
		with open("inFile","w") as inFile:
			inFile.write(header+" "+mutAll+"\n"+sequence)
		inFile.close()
		os.system("./run_mutpred2.sh -i inFile -p 1 -c 1 -t 0.1 -f 4 -o result.out")
		#Filter only required columns for the final output file
		out = pandas.read_csv("result.out")
		newOut = out.filter(["Substitution","MutPred2 score"],axis=1)
		phenotype = []
		for i in range(len(newOut)):
			if newOut.iloc[i,1] > 0.5:
				phenotype.append("Pathogenic")
			else:
				phenotype.append("Benign")
		newOut["Phenotype"] = phenotype
		newOut = newOut[["Substitution","Phenotype","MutPred2 score"]]
		newOut.columns = ["Mutation","Phenotype","Score"]
		newOut.to_csv("/home/ibab/automutation/outFiles/mutPred2.out",index=False)
		os.chdir("/home/ibab/automutation")
	except:
		print(str(sys.exc_info()[0])+" occured and MutPred2 could not run")
