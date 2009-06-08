import sys
import re
import pickle

mode = sys.argv[ 1 ]

if mode == "raw":
	d = dict( zip( range( 1, 10 ), [ dict() for i in range( 1, 10 ) ]  ) )
	re_valid = re.compile( "^[a-z]{3,9}$" )
	for line in sys.stdin:
		werds = line.strip().split( ' ' )
		for werd in werds:
			if re_valid.match( werd ):
				l = len( werd )
				if d[ l ].has_key( werd ):
					d[ l ][ werd ] += 1
				else:
					d[ l ][ werd ] = 1

elif mode == "freq":
	thresh = int( sys.argv[ 2 ] )
	d = dict( zip( range( 1, 10 ), [ dict() for i in range( 1, 10 ) ]  ) )
	re_valid = re.compile( "^[a-z]{3,9}$" )
	for line in sys.stdin:
		( werd, freq ) = line.strip().split( ' ' )
		freq = int( freq )
		if freq >= thresh and re_valid.match( werd ):
			l = len( werd )
			d[ l ][ werd ] = freq
	

pickle.dump( d, sys.stdout )
