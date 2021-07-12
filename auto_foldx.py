#!/usr/bin/python3

import sys
import os
import re
import pandas as pd

def runFoldx(pdbFilename,mutationFilename,fchain):
	os.chdir("/home/ibab/automutation")
	pdb=open(pdbFilename,"r")
	pdbFile=pdb.readlines()
	for lines in pdbFile:
		if re.match("^ATOM",lines):
			firstRes=int(re.split('\s+',lines)[5])
			break
	with open(mutationFilename,"r") as mutFile:
		muts = mutFile.readlines()
	muts = [x.strip() for x in muts]
	newRes = [x[-1] for x in muts]
	oldRes = [x[0] for x in muts]
	pos = []
	for x in muts:
		position=int(''.join(re.findall('\d',x)))
		if position < firstRes:
			pos.append(0)
		else:
			pos.append(int(''.join(re.findall('\d',x))))
	os.system("mkdir Foldxout")
	muts=[]
	try:
		for i in range(len(pos)):
			if pos[i] == 0:
				pass
			else:
				#Run FoldX in command-line
				mutFile = open("individual_list.txt","w")
				mutFile.write(oldRes[i]+fchain+str(pos[i])+newRes[i]+";\n")
				mutFile.close()
				res = os.system("foldx --command=BuildModel --pdb="+pdbFilename+" --mutant-file=individual_list.txt --out-pdb=false --screen=false --output-dir=./Foldxout")
				if res == 0:
					muts.append(oldRes[i]+str(pos[i])+newRes[i])
			
		file1 = open("Foldxout/Dif_"+pdbFilename.split(".")[0]+".fxout","r")
		lines = file1.readlines()[8:]
		file1.close()
		newFile = open("Foldxout/outFile","w")
		for i in range(len(lines)):
			newFile.write(lines[i])
		newFile.close()
		df = pd.read_csv("Foldxout/outFile",sep="\t",index_col=False)
		df["Mutations"]=muts
		stability=[]
		#Set stability values based on ddG values
		for i in range(len(df)):
			if df.iloc[i,1] < 0:
				stability.append("Stabilizing")
			else:
				stability.append("Destabilizing")
		df["Stability"] = stability
		df=df.filter(items=["Mutations","Stability","total energy"],axis=1)
		df = df.rename(columns={"total energy":"ddG"})
		df.to_csv("outFiles/foldX.out",index=False)
		
		os.system("rm -rf Foldxout molecules outFile individual_list.txt rotabase.txt Unrecognized_molecules.txt")
	except:
		print(str(sys.exc_info()[0])+" occured and FoldX could not run")
