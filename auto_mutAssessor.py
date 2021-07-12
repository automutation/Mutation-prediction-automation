#!usr/bin/python3

import mechanicalsoup
import sys
import os

# Receive input from the user for mailid and filename

def runMutAssessor(fasta,mutations):
	os.chdir("/home/ibab/automutation")
	url1 = "http://mutationassessor.org/r3"
	try:
		file1 = open(fasta,"r")
		uniprotid = file1.readline().split('|')[2].split()[0]
		file1.close()
		toSubmit = os.popen("sed 's/^/"+uniprotid+" /' "+mutations).read()
		br = mechanicalsoup.StatefulBrowser()
		br.open(url1)
		form = br.select_form(nr=0)
		br["vars"] = toSubmit
		form.set("info",False)
		res = br.submit_selected()
		csvFile = open("outFiles/mutationAssessor.out","w")
		csvFile.write("Mutation,Phenotype,Score\n")
		table = br.page.find('table',cellspacing="2")
		rows = []
		for row in table.find("tbody"):
			for content in row.findAll('td'):
				rows.append(content.text)
		for i in range(0,len(rows),16):
			csvFile.write(rows[i+1].split()[1]+","+rows[i+6].strip()+","+rows[i+7]+"\n")
		csvFile.close()
	except:
		print(str(sys.exc_info()[0])+" occured and MutationAssessor could not run")
