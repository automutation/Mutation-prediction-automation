#!usr/bin/python3

import mechanicalsoup
import sys
import re
import pandas as pd
import os

def runProvean(uniprotid,mutation):
	os.chdir("/home/ibab/automutation")
	url1 = "http://provean.jcvi.org/protein_batch_submit.php?species=human"

	with open(mutation,"r") as mutFile:
		muts = mutFile.readlines()
	mutFile.close()
	
	muts = [x.strip() for x in muts]
	newRes = [x[-1] for x in muts]
	oldRes = [x[0] for x in muts]
	pos = []
	for x in muts:
		position = ''.join(re.findall('\d',x))
		pos.append(int(position))

	variants=""
	for i in range(len(muts)):
		variants=variants+uniprotid+" "+str(pos[i])+" "+oldRes[i]+" "+newRes[i]+"\n"
	
	try:
		#Submit the mutations on web server
		br = mechanicalsoup.StatefulBrowser()
		br.open(url1)
		br.select_form(nr=0)
		br["variants"] = variants
		br.submit_selected()
		if "Error" in br.page.text:
			print("PROVEAN: There are errors in the input. Check the log file for details")
			logFile = open("logFiles/provean.log","w")
			logFile.write(br.page.text)
			logFile.close()
		else:
			#Fetch the results from the web page
			jobID= br.page.text.split("job ID: ")[1].split(")")[0]
			br.open("http://provean.jcvi.org/protein_batch_report.php?jobid="+jobID)
			while "View result table" not in br.page.text:
				br.open("http://provean.jcvi.org/protein_batch_report.php?jobid="+jobID)
			br.download_link(link="/"+jobID+".result.tsv",file="outFiles/provean.out")
			df = pd.read_table("outFiles/provean.out")
			df["Mutation"] = df["RESIDUE_REF"]+df["POSITION"].astype(str)+df["RESIDUE_ALT"]
			provean = df.filter(["Mutation","PREDICTION (cutoff=-2.5)","SCORE"],axis=1)
			provean.columns = ["Mutation","Phenotype","Score"]
			provean.to_csv("outFiles/provean.out",index=False)
			sift=df.filter(["Mutation","PREDICTION (cutoff=0.05)","SCORE.1"],axis=1)
			sift.columns = ["Mutation","Phenotype","Score"]
			sift.to_csv("outFiles/sift.out",index=False)
		
	except:
		print(str(sys.exc_info()[0])+" occured and PROVEAN could not run")
