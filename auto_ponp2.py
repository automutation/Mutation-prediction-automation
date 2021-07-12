#!usr/bin/python3

import mechanicalsoup
import sys
import os

def runPonP2(fasta,mutation,passwrd):
	os.chdir("/home/ibab/automutation")
	try:
		#Submit the mutation on web server
		url1 = "http://structure.bmc.lu.se/PON-P2/fasta_submission.html/"
		with open(fasta, "r") as infile:
			header = infile.readline()
			infile.seek(0)
			sequence = infile.read()
		infile.close()
		with open(mutation,"r") as mutFile:
			readFile = header+"\n"+mutFile.read()
		mutFile.close()
	
		br = mechanicalsoup.StatefulBrowser()
		br.open(url1)
		br.select_form(nr=0)
		br["email"] = "software@ibab.in"
		br["qSeq"] = sequence
		br["qVar"] = readFile
		res = br.submit_selected()
		message = res.text
		with open("logFiles/ponp2.log", "w") as outfile:
			outfile.write(str(message))
		outfile.close()
		if "Error" in str(message) or "do not match" in str(message) or "not acceptable" in str(message):
			print("PON-P2: There is an error while submitting the file. Check the log file for details")
		else:
			#Start the daemon process
			os.system("fetchmail -f /etc/.fetchmailrc")
			cmd = "sudo service cron restart"
			os.system('echo %s | sudo -S %s' % (passwrd, cmd))
	except:
		print(str(sys.exc_info()[0])+" occured and PON-P2 could not run")
