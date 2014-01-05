import pyglet
import random
from game import world
from game import graphics

#from pyglet.window import key
#from pyglet.window import mouse
#import world.py
#import graphics.py


window = pyglet.window.Window(512,512)

t = 0

# load world from file
def loadWorld():

  global w
  
  #resources = {'forest':0, 'swamp':0, 'grass':0, 'human':0, 'wood':0}
  resources = ['altitude', 'relief', 'land', 'rainfall', 'temperature', 'water', 'forest', 'swamp', 'grass', 'human', 'wood']

  waterLevel = 0.5
  
  influenceMatrix = {'human':{'human' :-0.02,
                              'forest':-0.01,
                              'swamp' :+0.00,
                              'grass' :+0.02,
                              'water' :-9999}}

  buildingSet = { ( 1, 1):'townhall',
                  ( 1, 2):'woodmill' }                          

  buildingDef = { 'townhall':{},
                  'woodmill':{'wood':+2,
                             'human':-2,
                             'forest':-2} }
  
  humanSpreadThreshold = 10
            
  vsize = 128
  hsize = 128
  
  seedPopulation = 10
  
  d = {'resources'            : resources,
       'waterLevel'           : waterLevel,
       'influenceMatrix'      : influenceMatrix,
       'buildingSet'          : buildingSet,
       'buildingDef'          : buildingDef,
       'humanSpreadThreshold' : humanSpreadThreshold,
       'vsize'                : vsize,
       'hsize'                : hsize,
       'seedPopulation'       : seedPopulation}
               
  w = world.world(d)
  
  
  

# load images from file
def loadImages():
  tiles = {}
  tilesRaw1       = pyglet.image.load('resources/tileset.png')
  tilesRaw2       = pyglet.image.ImageGrid(tilesRaw1, 8, 4)
  #tiles['water'] = tilesRaw2[20]
  tiles['water']  = pyglet.image.ImageGrid(pyglet.image.load('resources/water.png'), 4, 4)
  #tiles['land']  = tilesRaw2[21]
  tiles['land']   = pyglet.image.ImageGrid(pyglet.image.load('resources/land.png'), 4, 4)
  tiles['house']  = pyglet.image.ImageGrid(pyglet.image.load('resources/houses2.png'), 1, 8)
  tiles['forest'] = pyglet.image.ImageGrid(pyglet.image.load('resources/forest.png'), 1, 4)
  
  return tiles
  


# update game state
def update(dt):
  global imageList, tiles, t
  t = t + dt
  w.update(dt)
  
  # fill batch with images
  
  # TODO: figure out how not to keep adding sprites to the tile list!!!!
  tiles = graphics.fillBatch(w, imageList, main_batch, tiles)
  print len(tiles)
  
  # output to terminal
  print('time: {0}, pop: {1}, forest: {2}').format(t, int(w.cumulative('human')), int(w.cumulative('forest')))

# draw decorator
@window.event 
def on_draw(): 
  window.clear()
  main_batch.draw()



# load world from file
loadWorld()

# load images into sprites
imageList = loadImages()

# initialize batch
main_batch = pyglet.graphics.Batch()


# run game
if __name__ == '__main__':
  # initial filling of batch
  tiles = graphics.fillBatch(w, imageList, main_batch, [])
  print len(tiles)
  
  # set update interval in seconds
  pyglet.clock.schedule_interval(update, 1)
  
  # run
  pyglet.app.run()

