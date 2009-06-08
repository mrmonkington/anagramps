import sys
import re
import pickle

d = []
re_valid = re.compile( "^[a-z]{3,9}$" )
for line in sys.stdin:
	werds = line.strip().split( ' ' )
	for werd in werds:
		if re_valid.match( werd ):
			d.append( werd )

pickle.dump( d, sys.stdout )
