import sys
import re
import pickle
import random

import cluttergtk
import clutter
import gtk
import gtk
import math


tile_size = 32 
tile_margin = 2
screen_margin = 45
screen_width = 360
screen_height = 480
rack_y = 360

class Tile( clutter.Group ):
	def __init__( self, letter, pos ):
		clutter.Group.__init__( self )
		self.letter = letter
		self.pos = pos
		self.set_width( tile_size )
		self.set_height( tile_size )
		self.bg = clutter.Texture()
		self.bg.set_width( tile_size )
		self.bg.set_height( tile_size )
		#self.bg.set_from_file( "tile_down.png" )
		pixbuf = gtk.gdk.pixbuf_new_from_file( "tile_down.png" )
		self.bg.set_from_rgb_data(
			pixbuf.get_pixels(),
			pixbuf.props.has_alpha,
			pixbuf.props.width,
			pixbuf.props.height,
			pixbuf.props.rowstride,
			pixbuf.props.n_channels,
			0
		)
		#self.bg.set_opacity( 50 )
		#self.bg.set_color( clutter.Color( 0xff, 0xfd, 0xf9, 0xff ) )
		self.add( self.bg )
		self.bg.show()
		self.label = clutter.Text()
		self.label.set_font_name( "sans bold 23px" )
		self.label.set_text( letter )
		self.label.set_color( clutter.Color( 0x50, 0x20, 0x10, 0xff ) )
		self.label.set_width( tile_size )
		self.label.set_height( tile_size )
		self.label.set_anchor_point_from_gravity( clutter.GRAVITY_CENTER )
		self.label.set_position( int( tile_size / 2 ), int( tile_size / 2 ) )
		self.add( self.label )
		self.label.show()

		self.set_anchor_point_from_gravity( clutter.GRAVITY_CENTER )
		self.set_opacity( 0xff )

		# random wobble
		self.set_rotation(
			axis = clutter.Z_AXIS,
			angle = random.gauss( 0, 4 ),
			x = 0,
			y = 3,
			z = 60
		)
		

class Rack( clutter.Group ):
	def __init__( self, letters, previous ):
		clutter.Group.__init__( self )
		self.letters = letters
		self.tiles = []
		slot = 0
		self.cap_x = 0
		self.cap_y = 0

		#self.timeline = clutter.Timeline( fps = 60, duration = 200 )
		#fps removed from API	
		#self.timeline = clutter.Timeline( duration = 200 )
		#self.timeline.set_loop( False )
		#self.alpha = clutter.Alpha( self.timeline, clutter.smoothstep_inc_func )
		#self.tile_fx_tp = clutter.EffectTemplate( self.timeline, clutter.smoothstep_inc_func )

		for l in letters:
			t = Tile( l, slot )
			self.tiles.append( t )
			t.set_reactive( True )
			t.connect( 'button-press-event', self.on_mousedown )
			self.add( t )
			t.set_position( slot * ( tile_size + tile_margin ) , rack_y )
			slot += 1

		step = len( previous )
		for p in previous:
			slot = 0
			for l in p:
				t = Tile( l, slot )
				self.add( t )
				t.set_position(
					slot * ( tile_size + tile_margin ),
					rack_y - step * ( tile_size + tile_margin )
				)
				slot += 1
			step -= 1

		self.show_all()
		self.drag_res = 0
		self.mouseup_res = 0

	def on_mousedown( self, stage, event ):
		print "down"
		self.cap_x = event.x
		self.cap_y = event.y
		self.cap_tile = event.source
		if self.drag_res:
			self.get_stage().disconnect( self.drag_res )
		if self.mouseup_res:
			self.get_stage().disconnect( self.mouseup_res )
		self.drag_res = self.get_stage().connect( 'motion-event', self.on_dragrack )
		self.mouseup_res = self.get_stage().connect( 'button-release-event', self.on_mouseup )

		self.cap_tile.raise_top()
		self.cap_tile.set_scale( 1.2, 1.2 )

	def on_mouseup( self, stage, event ):
		print "up "
		self.get_stage().disconnect( self.drag_res )
		self.get_stage().disconnect( self.mouseup_res )
		self.drag_res = 0
		self.mouseup_res = 0
		self.tiles.sort( cmp = lambda a, b: int( a.get_x() - b.get_x() ) )
		slot = 0
		for t in self.tiles:
			if t == self.cap_tile:
				print "cap"
				t.set_position( slot * ( tile_size + tile_margin ), rack_y )
			else:
				#clutter.effect_move( self.tile_fx_tp, t, slot * ( tile_size + tile_margin ), rack_y )
				t.animate( clutter.EASE_IN_OUT_BACK, 400, 'x', slot * ( tile_size + tile_margin ), 'y', rack_y )
			slot += 1

		self.letters = "".join( [ l.letter for l in self.tiles ] )
		self.cap_tile.set_scale( 1.0, 1.0 )
		print "new order: %s" % self.letters

	def on_dragrack( self, stage, event ):
		print "drag %i %i" % ( event.x, event.y )
		self.cap_tile.set_x( event.x - self.get_x() )

class SubmitButton( clutter.Group ):
	def __init__( self ):
		clutter.Group.__init__( self )
		self.set_size( 5 * tile_size, tile_size )
		self.submit = clutter.Rectangle()
		self.submit.set_size( 5 * tile_size, tile_size )
		self.submit.set_color( clutter.Color( 0x20, 0xd0, 0x30, 0xff ) )
		self.add( self.submit )
		self.label = clutter.Text()
		self.label.set_font_name( "sans bold 15px" )
		self.label.set_text( "Try word..." )
		self.label.set_color( clutter.Color( 0x00, 0x20, 0x05, 0xff ) )
		self.label.set_position( int( 5 * tile_size / 2 ), int( tile_size / 2 ) - 1 )
		self.label.set_anchor_point_from_gravity( clutter.GRAVITY_CENTER )
		self.label.set_width( tile_size * 5 )
		self.label.set_height( tile_size )
		self.add( self.label )
		self.show_all()

class AnagrampsClutter():

	def __init__( self ):
		self.game_state = "play"

	def dict_lookup( self, word ):
		if word in self.dict:
			return True
		return False

	def on_submit( self, stage, event ):
		if self.game[ self.step ] == self.rack.letters:
			print "yay"
			self.correct()
		elif self.dict_lookup( self.rack.letters ):
			print "not what I was thinking, which was %s, but no biggie" % self.game[ self.step ]
			# make this the step
			self.game[ self.step ] = self.rack.letters
			self.correct()
		else:
			print "incorrect"


	def init_rack( self, letters ):
		x = screen_margin
		self.rack = Rack( letters, self.game[ 0 : self.step ] )
		self.rack.set_x( x )
		self.stage.add( self.rack )

	def get_word_diff( self, parent, child ):
		rem = list( parent )
		for letter in child:
			rem.remove( letter )
		return "".join( rem )
	
	def correct( self ):
		letters = self.rack.letters
		self.stage.remove( self.rack )
		self.step += 1
		if self.step >= len( self.game ):
			self.win()
		else:
			letters = letters + self.get_word_diff( self.game[ self.step ], letters )
			self.init_rack( letters )

	def win( self ):
		print "you win"
		sys.exit( 0 )

	def play( self, game ):
		self.step = 0
		self.game = game

		self.submit = SubmitButton()
		self.submit.set_position( int( ( screen_width - 5 * tile_size ) / 2 ), rack_y + tile_size + tile_margin )
		self.stage.add( self.submit )
		self.submit.set_reactive( True )

		self.submit.connect( 'button-press-event', self.on_submit )

		letters = "".join( random.sample( game[ self.step ], len( game[ self.step ] ) ) )
		print letters
		self.init_rack( letters )

		self.stage.show_all()

	def run( self, args, ramps, dict ):

		window = gtk.Window()
		window.connect('destroy', gtk.main_quit)
		window.set_title('cluttergtk.Embed')
		vbox = gtk.VBox(False, 6)
		window.add(vbox)
		embed = cluttergtk.Embed()
		vbox.pack_start(embed, True, True, 0)
		embed.set_size_request( screen_width, screen_height )
		embed.realize()
		#self.stage = clutter.Stage()
		self.stage = embed.get_stage()
		self.stage.set_color(clutter.Color( 0x20, 0x20, 0x20, 0xff ) )
		#self.stage.set_size( screen_width, screen_height )
		self.stage.set_reactive( True )
		self.stage.set_title( "Anagramps!" )

		bg = clutter.Texture()
		bg.set_from_file( "table.png" )
		bg.set_position( 0, 0 )
		self.stage.add( bg )

		game = random.sample( ramps, 1 )[ 0 ][ -1 : : -1 ]
		#game = ramps[ int( sys.argv[ 1 ] ) ][ -1 : : -1 ]
		#print game
		self.dict = dict
		self.play( game )

		self.stage.show_all()
		#timeline.start()
		clutter.threads_init()

		window.show_all()
		#clutter.main()
		gtk.main()

		return 0

def main( args ):
	app = AnagrampsClutter()
	ramps = pickle.load( open( "anagramps.pkl" ) )
	dict = pickle.load( open( "complete_dictionary.pkl" ) )
	return app.run( args, ramps, dict )
	
if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))


# scratchpad
#( fovy, aspect, z_near, z_far ) = stage.get_perspective()
#print ( fovy, aspect, z_near, z_far )
#stage.set_perspective( 60.0, 1.0, 0.08, 70.0 )

#	def on_new_frame (self, tl, frame_num):
#		self.set_rotation (clutter.Z_AXIS,
#			frame_num,
#			self.stage.get_width() / 2,
#			self.stage.get_height () / 2,
#			0)
#	  
#		angle = frame_num * -2
#
#		for i in range(self.n_hands):
#			hand = self.get_nth_child(i)
#			hand.set_rotation(clutter.Z_AXIS,
#				angle, 
#				hand.get_width() / 2,
#				hand.get_height() / 2,
#				0)

#	def ping( self ):
#		print "ping"
#		self.timeline_in = clutter.Timeline(8, 60)
#		self.alpha_in = clutter.Alpha( self.timeline_in, clutter.sine_half_func ) 
#		self.in_behaviour = clutter.BehaviourScale(
#			alpha = self.alpha_in,
#			x_scale_start = 1.1,
#			y_scale_start = 1.1,
#			x_scale_end = 1.2,
#			y_scale_end = 1.2
#		)
#		self.in_behaviour.apply( self )
#		self.timeline_in.start()
#		return False
