#!usr/bin/python3
import os
import mechanicalsoup as msp
import sys

def runMetaSNP(fasta,mutation):
	os.chdir("/home/ibab/automutation")
	file1 = open(fasta,"r")
	seq = file1.read()
	file1.close()
	file2 = open(mutation,"r")
	muts = file2.read()
	file2.seek(0)
	noOfMuts = len(file2.readlines())
	file2.close()
	url1 = "https://snps.biofold.org/meta-snp/index.html"
	try:
		#Submit the mutations to the web server
		br = msp.StatefulBrowser()
		br.open(url1)
		br.select_form(selector="form")
		br["proteina"] = seq
		br["posizione"] = muts
		res = br.submit_selected()
		br.follow_link("output.html")
		resultLink = br.get_url()
		br.open(resultLink)
		#Fetch the output file from the results page
		while "Please wait." in br.page.text:
			br.open(resultLink)
		br.download_link(link="output.txt",file="metaSNP")
		outFile = open("outFiles/metaSNP.out","w")
		outFile.write("Mutation,Phenotype,Score\n")
		snpsFile = open("metaSNP","r")
		allres = []
		res = snpsFile.readlines()
		#Fetch only required results
		for i in range(7,len(res)):
			allres.append(res[i].split())
		for i in range(1,len(allres)-18,2):
			meta = allres[i][0],allres[i][-5],allres[i+1][-1]
			outFile.write(','.join(meta))
			outFile.write("\n")
		outFile.close()
		snpsFile.close()
		os.system("rm metaSNP")
	except:
		print(str(sys.exc_info()[0])+" occured and metaSNP could not run")
