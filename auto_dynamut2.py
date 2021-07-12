#!usr/bin/python3

import re
import mechanicalsoup as msp
import sys
import pandas as pd
import os

def runDynamut(pdbFile,mutationFile,fChain):
	os.chdir("/home/ibab/automutation")
	try:
		chain = fChain
		file1 = open(mutationFile,"r")
		muts = file1.readlines()
		file1.close()
		muts = [x.strip() for x in muts]
		newRes = [x[-1] for x in muts]
		oldRes = [x[0] for x in muts]
		pos = []
		for x in muts:
			position = ''.join(re.findall('\d',x))
			pos.append(int(position))

		pdbfile=open(pdbFile,"r")
		pdblines=pdbfile.readlines()
		for lines in pdblines:
			if re.match("^ATOM",lines):
				firstRes=re.split('\s+',lines)[5]
				break
	
		missing = []
		for lines in pdblines:
			if re.match("REMARK 465",lines):
				missing.append(lines)
		chainA=[]
		for x in missing[7:]:
			if re.split('\s+',x)[3]==chain:
				chainA.append(int(re.split('\s+',x)[4]))
		common=[x for x in pos if x in chainA]
		#Removing missing residues from mutation file
		notCommon=[]
		for x in pos:
			if x in common or x < int(firstRes):
				notCommon.append(0)
			else:
				notCommon.append(x)
		muts=[]	
		for i in range(len(pos)):
			if notCommon[i]==0:
				pass
			else:
				muts.append(oldRes[i]+str(notCommon[i])+newRes[i])
		outFile=open("outFiles/dynamut2.out","w")
		outFile.write("Mutation,Stability,ddG\n")
		outFile.close()
		url1 = "http://biosig.unimelb.edu.au/dynamut2/submit_prediction"
		logFile=open("logFiles/dynamut2.log","w")
		outFile=open("outFiles/dynamut2.out","a")
		for i in range(len(muts)):
			#Submission of mutations to the web server
			br = msp.StatefulBrowser()
			br.open(url1)
			form = br.select_form(nr=0)
			form.set("pdb_file_single",pdbFile)
			br["mutation_single"]=muts[i]
			br["chain_single"] = chain
			br.submit_selected()
			if "Error" in br.page.text:
				print("DynaMut2: Error in submission of a mutation. Check log file for details.")
				logFile.write(br.page.text.split("Submission Error")[2].split("arrow")[0])
			else:
				#Fetching results from the webpage
				res = br.get_url()
				while("Predicted Stability Change" not in br.page.text):
					br.open(res)
				result=re.split("Predicted Stability Change",br.page.text)[1].split('\n\n')[0]
				score=result.split('\n')[1].split()[0]
				stability=result.split('\n')[2][1:-1]
				outFile.write(muts[i]+","+stability+","+score+"\n")
				
		logFile.close()
		outFile.close()
		"""pos = []
		for x in df.mutation:
			position = ''.join(re.findall('\d',x))
			pos.append(int(position))
		df["pos"] = pos
		df = df.sort_values(by=["pos"])
		df = read_csv("outFiles/dynamut2.out",header=True,index_col=False)
		stab = []
		for x in df.score:
			if x < 0:
				stab.append("Destabilizing")
			else:
				stab.append("Stabilizing")
		df["stability"] = stab
		df = df.filter(["mutation","stability","prediction"],axis=1)
		df.columns = ["Mutation","Prediction","Stability"]
		df.to_csv("outFiles/dynaRes.out",index=False)
		os.system("rm submit.txt")"""
	except:
		print(str(sys.exc_info()[0])+" occured and DynaMut2 could not run")
