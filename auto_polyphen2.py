#!usr/bin/python3
import mechanicalsoup
import re
import pandas
import os
import sys

def runPolyphen2(uniprotId,mutation):
	os.chdir("/home/ibab/automutation")
	with open(mutation,"r") as mutFile:
		muts = mutFile.readlines()
	mutFile.close()
	muts = [x.strip() for x in muts]
	newRes = [x[-1] for x in muts]
	wildRes = [x[0] for x in muts]
	pos = []
	for x in muts:
		pos.append(''.join(re.findall('\d',x)))
	batch = ""
	for i in range(len(pos)):
		batch += uniprotId+" "+pos[i]+" "+wildRes[i]+" "+newRes[i]+"\n"
	try:
		#Submit mutations on web server
		br = mechanicalsoup.StatefulBrowser()
		url1 = "http://genetics.bwh.harvard.edu/pph2/bgi.shtml"
		br.open(url1)
		br.select_form(nr=0)
		br["_ggi_batch"]= batch
		br["MODELNAME"] = "HumVar"
		br.submit_selected(btnName="_ggi_target_pipeline")
		session = str(br.page.find("input",attrs={"name":"sid"}))
		sID = session.split('value="')[-1][:-3]
		br.select_form(nr=0)
		br.submit_selected()
		br.select_form()
		br.submit_selected()
		checkLink = "/pph2/"+sID
		res = br.links(url_regex=checkLink)
		#Get the output from results web page
		while not res or checkLink not in str(res[0]):
			br.select_form()
			br.submit_selected()
			res = br.links(url_regex=checkLink)
		resultLink = "/pph2/"+sID+"/./pph2-short.txt"
		logLink = "/pph2/"+sID+"/./pph2-log.txt"
		br.download_link(link=resultLink,file="pph2.out")
		br.download_link(link=logLink,file="logFiles/polyphen2.log")
		#Format the output as required
		out = pandas.read_table("pph2.out")
		out.columns = [out.columns[i].strip() for i in range(len(out.columns))]
		newOut = out.dropna()
		newOut = newOut[newOut["pos"].notnull()].copy()
		newOut["pos"]=newOut["pos"].astype(int)
		newOut = newOut.filter(["pos","aa1","aa2","prediction","pph2_prob"],axis=1)
		newOut["aa1"] = newOut["aa1"].str.strip()
		newOut["aa2"] = newOut["aa2"].str.strip()
		newOut["prediction"] = newOut["prediction"].str.strip()
		newOut["mut"] = newOut["aa1"]+newOut["pos"].astype(str)+newOut["aa2"]
		newOut = newOut.filter(["mut","prediction","pph2_prob"],axis=1)
		newOut.columns = ["Mutation","Phenotype","Score"]
		newOut.to_csv("outFiles/polyphen2.out",index=False)
		os.remove("pph2.out")
	except:
		print(str(sys.exc_info()[0])+" occured and PolyPhen-2 could not run")
