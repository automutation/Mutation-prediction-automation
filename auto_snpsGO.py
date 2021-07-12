#!/usr/bin/python3

import os
import sys
import mechanicalsoup as msp

def runSnpsGO(fasta,mutation):
	os.chdir("/home/ibab/automutation")
	file1 = open(fasta,"r")
	seq = file1.read()
	file1.close()
	file2 = open(mutation,"r")
	muts = file2.read()
	file2.close()
	url1 = "https://snps.biofold.org/snps-and-go/snps-and-go.html"
	try:
		#Submit the mutations on webserver
		br = msp.StatefulBrowser()
		br.open(url1)
		br.select_form(selector="form")
		br["proteina"] = seq
		br["posizione"] = muts
		res = br.submit_selected()
		br.follow_link("output.html")
		resultLink = br.get_url()
		br.open(resultLink)
		#Fetch results from web page
		while "Please wait." in br.page.text:
			br.open(resultLink)
		br.download_link(link="output.txt",file="snpsGO")
		outFile = open("outFiles/snpsGO.out","w")
		outFile.write("Mutation,Phenotype,Score\n")
		snpsFile = open("snpsGO","r")
		logFile = open("logFiles/snpsGO.log","w")
		for lines in snpsFile:
			if "SNPs&GO" in lines and (("*" not in lines) and ("SVM" not in lines)):
				res = lines.split()[:2]
				res.append(lines.split()[-2])
				outFile.write(','.join(res))
				outFile.write("\n")
			if "WARNING" in lines:
				logFile.write(lines)
		logFile.close()
		snpsFile.close()
		outFile.close()
		os.system("rm snpsGO")
	except:
		print(str(sys.exc_info()[0])+" occured and SNPs&GO could not run")
