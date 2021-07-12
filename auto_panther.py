#!/usr/bin/python3

import re
import os
import pandas
import sys

def runPanther(fasta,mutation):
	os.chdir("/home/ibab/automutation")
	file1 = open(fasta,"r")
	seq = file1.read()
	file1.close()
	seq = seq.replace('|','_')
	header = seq.split()[0]
	sequence = ''.join(seq.split('\n')[1:])
	file1 = open("/home/ibab/automutation/PANTHER_PSEP1.01/scripts/"+fasta,"w")
	file1.write(header+'\n'+sequence)
	file1.close()
	file2 = open(mutation,"r")
	muts = file2.readlines()
	file2.close()
	muts = [x.strip() for x in muts]
	newRes = [x[-1] for x in muts]
	wildRes = [x[0] for x in muts]
	pos = []
	for x in muts:
		pos.append(''.join(re.findall('\d',x)))
	try:
		os.chdir("/home/ibab/automutation/PANTHER_PSEP1.01/scripts")
		inputFile = open("inFile.input","w")
		#Create input file as required by PANTHER and run in command-line
		for i in range(len(pos)):
			inputFile.write("del"+str(i+1)+"|"+header[1:]+"|"+pos[i]+"|"+wildRes[i]+";"+newRes[i]+'\n')
		inputFile.close()
		os.system("perl run_blastp.pl -q "+fasta+" -d ../blast/blast -o Blastout -e err")
		os.system("perl BlastpExisit.pl -d ../blast/blast -l ../opt/panther/PAML_RST/ -s HUMAN -i inFile.input -f Blastout -o Snp.out -e Err")
		outFile = open("/home/ibab/automutation/outFiles/panther.out","w")
		out = pandas.read_csv("Snp.out",header=None,names=['a','b','c','d','e'])
		newOut = out.filter(["b","e","d"],axis=1)
		newOut.columns=["Mutation","Phenotype","Score"]
		os.chdir("/home/ibab/automutation")
		newOut.to_csv("outFiles/panther.out",index=False)
		os.chdir("/home/ibab/automutation")
	except:
		print(str(sys.exc_info()[0])+" occured and PANTHER could not run")
