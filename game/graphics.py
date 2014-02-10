import pyglet
import random
import cocos
import world

# the graphics class generates a graphical representation of the data
# stored in the world object
class graphics():

  def __init__(self, layers, world):

    self.layers = layers
    self.tileset = self.loadTileset()

    # create scroller
    self.scroller = cocos.layer.ScrollingManager()
    
    # create cells for layer
    self.cellMatrices = {}
    self.fillCellMatrices(world)
    
    # generate layers
    self.fillLayers()


  # load tileset images from file
  def loadTileset(self):

    tileset = {}
    tilesRaw1       = pyglet.image.load('resources/tileset.png')
    tilesRaw2       = pyglet.image.ImageGrid(tilesRaw1, 8, 4)
    #tiles['water'] = tilesRaw2[20]
    tileset['water']  = pyglet.image.ImageGrid(pyglet.image.load('resources/water.png'), 4, 4)
    #tiles['land']  = tilesRaw2[21]
    tileset['land']   = pyglet.image.ImageGrid(pyglet.image.load('resources/land.png'), 4, 4)
    tileset['house']  = pyglet.image.ImageGrid(pyglet.image.load('resources/houses2.png'), 1, 8)
    tileset['forest'] = pyglet.image.ImageGrid(pyglet.image.load('resources/forest.png'), 1, 4)
    tileset['empty'] = tilesRaw2[3]
    
    return tileset



  # creates a cell matrix based on data in the world object
  def createCellMatrix(self, layer, world):

    emptyImage = self.tileset['empty'] 
   
    if layer in self.cellMatrices:
      result = self.cellMatrices[layer]
    else:
      result = [ [None]*world.hsize for i in range(world.vsize) ]
      
    for v in range(world.vsize):
      for h in range(world.hsize):

        if world.changeMap[v][h] != 0:
        
          tile = None
          image = None
          
          if layer == 'land':    
            # determine terrain type
            terrainType = world.resourceMap['land'][v][h]
            if terrainType == 0:
              r1 = random.randrange(0,16)
              image = self.tileset['water'][r1]
            elif terrainType == 1:
              r2 = random.randrange(0,16)
              image = self.tileset['land'][r2]
            
            #tile = cocos.tiles.Tile('land', {}, image, None)
          
          elif layer == 'human':
          
            # determine houses
            pop = world.resourceMap['human'][v][h]
            idx = min(int(pop/2),7)
            if pop > 0:
              image = self.tileset['house'][idx]
            #else:  
            #  image = None
              
            #tile = cocos.tiles.Tile('human', {}, image, None)
          
          elif layer == 'forest':
          
            # determine forest
            forest = world.resourceMap['forest'][v][h]
            idx = min(int(forest/20),3)
            if forest > 0:
              image = self.tileset['forest'][idx]
            #else:
            #  image = None
  
          # create tile
          if image != None:            
            tile = cocos.tiles.Tile(layer, {}, image, None)

          # add tile to cell matrix
          result[v][h] = cocos.tiles.RectCell(h*16, v*16, 1, 1, None, tile)  
         
    return result
  
  
  
  
  # fills a list of cell matrices based on data in world 
  def fillCellMatrices(self, world):
   
    for layer in self.layers:
      c = self.createCellMatrix(layer, world)
      self.cellMatrices[layer] = c
  
      
      
      
  # adds RectMapLayers to scroller one by one
  def fillLayers(self):
    
    for layer in self.layers:   
      rectMapLayer = self.getRectMapLayer(layer)
      layerSortOrder = self.layers.index(layer)
      self.scroller.add(rectMapLayer, layerSortOrder, layer) 


  def updateLayers(self):
  
    for layer in self.layers:
      self.scroller.remove(layer)

      rectMapLayer = self.getRectMapLayer(layer)
      layerSortOrder = self.layers.index(layer)
      self.scroller.add(rectMapLayer, layerSortOrder, layer) 
      

  # obtains a layer by applying rules (specific for that layer) to 
  # data stored in a world object
  def getRectMapLayer(self, layer):

    result = cocos.tiles.RectMapLayer(layer, 16, 16, self.cellMatrices[layer], None, {})    
    return result
