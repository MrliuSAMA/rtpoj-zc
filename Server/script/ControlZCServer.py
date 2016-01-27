#!/usr/bin/python

import sys
import subprocess

if(sys.argv[1] == '--restart'):

	cmd = "sudo service named restart &"

	p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	out, err = p.communicate()
	print out
