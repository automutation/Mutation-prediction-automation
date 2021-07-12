#!/usr/bin/python3

import mechanicalsoup as msp
import sys
import os

def runDuet(pdbFile,mutation,fChain):
	os.chdir("/home/ibab/automutation")
	file1 = open(mutation,"r")
	muts = file1.readlines()
	noOfMuts = len(muts)
	file1.close()
	outFile = open("outFiles/duet.out","w")
	logFile = open("logFiles/duet.log","w")
	outFile.write("mCSM Score,Stability,SDM Score,Stability,DUET Score,Stability,Mutation\n")
	url1 = "http://biosig.unimelb.edu.au/duet/stability"
	try:
		#Submission to DUET server
		br = msp.StatefulBrowser()
		for i in range(noOfMuts):
			br.open(url1)
			form = br.select_form(nr=1)
			form.set("wild",pdbFile)
			br["mutation"] = muts[i].strip()
			br["chain"] = fChain
			res = br.submit_selected()
			#Fetch results from the webpage
			content = br.page.find('div',attrs={"class":"well"})
			if content:
				stability=content.findAll("font",attrs={"size":"4"})
				outFile.write(muts[i].strip()+",")
				for texts in stability:
					outFile.write(texts.text.split()[0]+","+texts.find("i").text+",")
				outFile.write("\n")
			elif not content:
				error = br.page.find("div",attrs={"class":"alert alert-error"})
				if "Error" in error.text:
					logFile.write(error.text)
			else:
				logFile.write(br.page.text)
		logFile.close()
		outFile.close()
	except:
		print(str(sys.exc_info()[0])+" occured and DUET could not run")
