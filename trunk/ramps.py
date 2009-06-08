import sys
import re
import pickle
import random

class NoLadderPossible( Exception ): pass

def partial_anagram( parent, child, diff ):
	rem = list( parent )
	for letter in child:
		if letter not in rem:
			return False
		rem.remove( letter )
	if len( rem ) != diff:
		return False
	return True

def create_ladder( dictionary, size, min_size, start_word = "" ):
	# frequency word must be initially above
	#f_thresh = 3;
	# sample the whole lot

	if start_word != "":
		filtered = [ word for word in dictionary[ size ].keys() if partial_anagram( start_word, word, 1 ) ]
	else:
		filtered = dictionary[ size ].keys()
	
	if len( filtered ) == 0:
		raise NoLadderPossible()

	for word in random.sample( filtered, len( filtered ) ):
		try:
			#print ( " " * ( 10 - size ) ) + word
			if size > min_size:
				return [ word ] + create_ladder( dictionary, size - 1, min_size, word )
			else:
				return [ word ]
		except NoLadderPossible:
			continue
	raise NoLadderPossible


if __name__ == "__main__":
	d = pickle.load( open( "dictionary.pkl" ) )
	ladders = []
	for i in range( 1, 100 ):
		ladders.append( create_ladder( d, 9, 3 ) )
	pickle.dump( ladders, sys.stdout )
