#!/usr/bin/python3

import sys
import os
import re
import pandas as pd

def runMaestro(pdbF,mutationF,fChain):
	os.chdir("/home/ibab/automutation")
	chain = fChain
	pdb=open(pdbF,"r")
	pdbFile=pdb.readlines()
	#Getting the first residue
	for lines in pdbFile:
		if re.match("^ATOM",lines):
			firstRes=int(re.split('\s+',lines)[5])
			break
	with open(mutationF,"r") as mutFile:
		muts = mutFile.readlines()
	muts = [x.strip() for x in muts]
	newRes = [x[-1] for x in muts]
	oldRes = [x[0] for x in muts]
	pos = []
	#Remove mutations not in PDB file
	for x in muts:
		position=int(''.join(re.findall('\d',x)))
		if position < firstRes:
			pos.append(0)
		else:
			pos.append(int(''.join(re.findall('\d',x))))
	mutFile = open("MutMaestro","w")
	mutants = []
	#Creating input file for MAESTRO
	for i in range(len(pos)):
		if pos[i] == 0:
			pass
		else:
			mutFile.write(oldRes[i]+str(pos[i])+"."+chain+"{"+newRes[i]+"}\n")
			mutants.append(muts[i])
	mutFile.close()
	mutFile=open("MutMaestro","r")
	muts=mutFile.readlines()
	muts = [x.strip() for x in muts]
	mutFile.close()
	try:
		os.chdir("/home/ibab/automutation/MAESTRO_linux_x64")
		#Run MAESTRO in command-line
		open("result","w").close()
		for i in range(len(muts)):
			os.system("maestro config.xml /home/ibab/automutation/"+pdbF+","+chain+" --evalmut="+muts[i]+" >> result")
		df = pd.read_csv("result",sep='\t',index_col=False)
		os.chdir("/home/ibab/automutation")
		df = df.rename(columns={"#structure":"structure"})
		i=df[df.structure == "#structure"].index
		df=df.drop(i)
		i=df[df.mutation=="wildtype"].index
		df=df.drop(i)
		ddG=[]
		for i in range(len(df)):
			ddG.append(df.iloc[i,-2].strip())
		df["ddG"]=ddG
		stability=[]
		#Create stability values based on ddG
		for i in range(len(df)):
			if float(df.iloc[i,-2].strip()) > 0:
				stability.append("Destabilizing")
			else:
				stability.append("Stabilizing")
		df["Stability"]=stability
		df["Mutation"] = mutants
		out = df.filter(["Mutation","Stability","ddG"],axis=1)
		out.to_csv("outFiles/maestro.out",index=False)
		os.system("rm MutMaestro result")
	except:
		print(str(sys.exc_info()[0])+" occured and MAESTRO could not run")
