#!/bin/bash

cd /home/ibab/automutation
mailx <<< q > mails
cmd=$(`grep "PON-P2" mails`)
if [ "$cmd" != "0" ]; then
        cp /var/mail/$(whoami) mbox
        /home/ibab/.local/bin/mboxattachments --filter_from proteinbioinformatik /home/ibab/automutation/mbox
	filecheck=$(`ls *$(grep -o -E ' [0-9]+' logFiles/ponp2.log | sed 's/ //')*.txt`)
        if [ "$filecheck" != "0" ]; then
                mv -T *$(grep -o -E ' [0-9]+' logFiles/ponp2.log | sed 's/ //')*.txt "result.txt"
                awk -F'\t' '{ print $3 "," $6 "," $4 }' result.txt > outFiles/ponp2.out
                sed -i "1s/.*/Mutation,Phenotype,Score/" outFiles/ponp2.out
                rm result.txt mails mbox
                sudo service cron stop
        fi
fi
