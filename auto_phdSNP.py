#!/usr/bin/python3

import os
import re
import sys

def runPhdSNP(fasta,mutation):
	os.chdir("/home/ibab/automutation")
	#To edit the sequence file as required(without header and line wrap)
	with open(fasta,"r") as f1:
		seq = f1.readlines()[1:]
	sequence = ""
	for line in seq:
		sequence = sequence + line.split('\n')[0]
	f1.close()
	outFile = open("outFiles/phdSNP.out","w")
	outFile.write("Mutation,Phenotype,Score\n")
	outFile.close()
	with open("/home/ibab/automutation/PhD-SNP2.0.7/seqFile","w") as f2:
		f2.write(sequence)
	f2.close()
	with open(mutation,"r") as mutFile:
		muts = mutFile.readlines()
	muts = [x.strip() for x in muts]
	newRes = [x[-1] for x in muts]
	pos = []
	for x in muts:
		pos.append(''.join(re.findall('\d',x)))
	#To run PhD-SNP one after ther other
	try:
		os.chdir("/home/ibab/automutation/PhD-SNP2.0.7")
		open('result.out', 'w').close()
		for i in range(len(pos)):
			os.system("python -O PhD-SNP.py -seq seqFile "+pos[i]+" "+newRes[i]+" >> result.out")
		csvFile = open("/home/ibab/automutation/outFiles/phdSNP.out","a")
		#Getting the result in required format
		with open("result.out","r") as resFile:
			for lines in resFile:
				if "Sequence-Based Prediction" in lines:
					line = next(resFile)
					csvFile.write(line.split()[1]+line.split()[0]+line.split()[2]+','+line.split()[3]+','+line.split()[4]+'\n')
		resFile.close()
		csvFile.close()
		os.chdir("/home/ibab/automutation")
	except:
		print(str(sys.exc_info()[0])+" occured and PhDSNP could not run")
