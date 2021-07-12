#!/usr/bin/python3

from multiprocessing import Process
import sys
import getpass
import re
import mechanicalsoup
import os
import pandas as pd
import auto_iMutant2
import auto_ponp2
import auto_muPro
import auto_mutPred2
import auto_phdSNP
import auto_mutAssessor
import auto_provean
import auto_panther
import auto_polyphen2
import auto_snpsGO
import auto_metaSNP
import auto_duet
import auto_dynamut2
import auto_maestro
import auto_foldx

def runAll1(fastaF,mutationF,pdbF,uniprotID,password,firstChain):
	auto_iMutant2.runIMutant(fastaF,mutationF)
	auto_ponp2.runPonP2(fastaF,mutationF,password)
	auto_muPro.runMuPro(fastaF,mutationF)
	auto_metaSNP.runMetaSNP(fastaF,mutationF)
	auto_foldx.runFoldx(pdbF,mutationF,firstChain)
	
def runAll2(fastaF,mutationF,pdbF,uniprotID,password,firstChain):
	auto_provean.runProvean(uniprotID,mutationF)
	auto_panther.runPanther(fastaF,mutationF)
	auto_snpsGO.runSnpsGO(fastaF,mutationF)
	auto_phdSNP.runPhdSNP(fastaF,mutationF)
	auto_dynamut2.runDynamut(pdbF,mutationF,firstChain)

def runAll3(fastaF,mutationF,pdbF,uniprotID,password,firstChain):
	auto_mutAssessor.runMutAssessor(fastaF,mutationF)
	auto_mutPred2.runMutPred(fastaF,mutationF)
	auto_maestro.runMaestro(pdbF,mutationF,firstChain)
	auto_polyphen2.runPolyphen2(uniprotID,mutationF)
	auto_duet.runDuet(pdbF,mutationF,firstChain)

"""def runAll(fastaF,mutationF,pdbF,uniprotID,password,firstChain):
	auto_iMutant2.runIMutant(fastaF,mutationF)
	auto_ponp2.runPonP2(fastaF,mutationF,password)
	auto_muPro.runMuPro(fastaF,mutationF)
	auto_metaSNP.runMetaSNP(fastaF,mutationF)
	auto_foldx.runFoldx(pdbF,mutationF,firstChain)
	auto_provean.runProvean(uniprotID,mutationF)
	auto_panther.runPanther(fastaF,mutationF)
	auto_snpsGO.runSnpsGO(fastaF,mutationF)
	auto_phdSNP.runPhdSNP(fastaF,mutationF)
	auto_dynamut2.runDynamut(pdbF,mutationF,firstChain)
	auto_mutAssessor.runMutAssessor(fastaF,mutationF)
	auto_mutPred2.runMutPred(fastaF,mutationF)
	auto_maestro.runMaestro(pdbF,mutationF,firstChain)
	auto_polyphen2.runPolyphen2(uniprotID,mutationF)
	auto_duet.runDuet(pdbF,mutationF,firstChain)"""

fastaFile = sys.argv[1]
mutationFile = sys.argv[2]
pdbFile = sys.argv[3]
uniprot = sys.argv[4]
passwd = getpass.getpass(prompt='Enter the system password: ')

#Create directories for output files and logfiles
if os.path.exists("outFiles"):
	pass
else:
	os.system("mkdir outFiles")
if os.path.exists("logFiles"):
	pass
else:
	os.system("mkdir logFiles")

#Download the FASTA from UNIPROT
"""br = mechanicalsoup.StatefulBrowser()
br.open("https://www.uniprot.org/uniprot/"+uniprot+".fasta")
if br.page:
	if "this page was not found" in br.page.text:
		raise Exception("Provide a valid UNIPROT ID")
else:
	if os.path.exists(uniprot+".fasta"):
		pass
	else:
		os.system("wget https://www.uniprot.org/uniprot/"+uniprot+".fasta")

fastaFile = uniprot+".fasta"""
#Check FASTA file
readFasta = open(fastaFile,"r")
head = readFasta.readline()
if head.startswith(">"):
	pass
else:
	sys.exit("The sequence file is not in FASTA format. Check the file before submission.")

#If there is any invalid mutation, the lines containing those invalid mutations will be removed and only valid ones will be used for prediction
with open(mutationFile,"r") as mutFile:
	muts = mutFile.readlines()
mutFile.close()
muts = [x.strip() for x in muts]
newRes = [x[-1] for x in muts]
oldRes = [x[0] for x in muts]
pos = []
for x in muts:
	position = ''.join(re.findall('\d',x))
	pos.append(int(position))
newMuts = []
for i in range(len(pos)):
	muts = [x.upper() for x in muts]
	if newRes[i] not in "BJOUXZ" and oldRes[i] not in "BJOUXZ":
		newMuts.append(muts[i])
pos = []
for x in newMuts:
	position = ''.join(re.findall('\d',x))
	pos.append(int(position))
df=pd.DataFrame({"pos":pos,"Mut":newMuts})
df1 = df.sort_values(by=['pos'])
head=["Mut"]
df1.to_csv(mutationFile,index=False,header=False,columns=head)

#To get the first chain in PDB file
pdb=open(pdbFile,"r")
pdbline=pdb.readlines()
for lines in pdbline:
	if re.match("^ATOM",lines):
		chain = re.split('\s+',lines)[4]
		break

#Start the functions in 3 different processors
myProcess1=Process(target=runAll1,args=(fastaFile,mutationFile,pdbFile,uniprot,passwd,chain))
myProcess1.start()
myProcess2=Process(target=runAll2,args=(fastaFile,mutationFile,pdbFile,uniprot,passwd,chain))
myProcess2.start()
myProcess3=Process(target=runAll3,args=(fastaFile,mutationFile,pdbFile,uniprot,passwd,chain))
myProcess3.start()
myProcess1.join()
myProcess2.join()
myProcess3.join()

#runAll(fastaFile,mutationFile,pdbFile,uniprot,passwd,chain)

#Stop the daemon prcess and remove mails and files from PON-P2
comd = "sudo service cron stop"
os.system('echo %s | sudo -S %s' % (passwd, comd))
os.system("rm SQ*")
os.system("bash -c 'mailx <<< d*'")
