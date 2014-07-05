import pyglet
import random
import cocos
import world
import time

# the graphics class generates a graphical representation of the data
# stored in the world object
class HeadUpDisplay(cocos.layer.Layer):

  def __init__(self, nrOfLabels, xAnchor, yAnchor, labelHeight):
    super(HeadUpDisplay, self).__init__()

    # empty list of labels
    self.label = []

    for k in range(nrOfLabels):
      # create label
      self.label.append(cocos.text.Label('', anchor_x='left', anchor_y='bottom', font_size=labelHeight))
      self.label[k].position = xAnchor, yAnchor + k * labelHeight

      # add label to layer
      self.add(self.label[k])

class Menu(cocos.menu.Menu):

  def __init__(self):
    super(Menu, self).__init__()

    l = []
    l.append(cocos.menu.MenuItem('Options', self.do_something()))
    self.create_menu(l)

  def do_something(self):
    print 'options'

class Graphics():

  def __init__(self, layers, world):

    self.layers = layers
    self.tileset = self.loadTileset()

    # create scroller (and underlying rectMapLayers)
    self.scroller = cocos.layer.ScrollingManager()

    # create empty cells
    self.cells = self.createEmptyCells(world.hsize, world.vsize)

    # create empty layers
    self.createRectMapLayers()

    self.updateLayers(world, True)

    #self.fillCells(world)


  # load tileset images from file
  def loadTileset(self):

    tileset = {}
    tilesRaw1       = pyglet.image.load('resources/tileset.png')
    tilesRaw2       = pyglet.image.ImageGrid(tilesRaw1, 8, 4)
    #tiles['water'] = tilesRaw2[20]
    tileset['water']  = pyglet.image.ImageGrid(pyglet.image.load('resources/water3.png'), 8, 1)
    #tiles['land']  = tilesRaw2[21]
    tileset['land']   = pyglet.image.ImageGrid(pyglet.image.load('resources/land3.png'), 7, 1)
    tileset['house']  = pyglet.image.ImageGrid(pyglet.image.load('resources/houses3.png'), 1, 8)
    tileset['forest'] = pyglet.image.ImageGrid(pyglet.image.load('resources/forest3.png'), 12, 4)
    tileset['grass'] = pyglet.image.ImageGrid(pyglet.image.load('resources/grass3.png'), 12, 4)
    tileset['empty'] = tilesRaw2[3]
    tileset['townhall'] = tilesRaw2[12]
    return tileset

  ## fills a list of cell Cells based on data in world
  #def fillCells(self, world):
  #
  #  for layer_id in self.layers:
  #    self.cells[layer_id] = self.createCells(layer_id, world)

  def createEmptyCells(self, hsize, vsize):

    cells = {}
    emptyImage = self.tileset['empty']

    for layer_id in self.layers:
      dummyTile = cocos.tiles.Tile(layer_id, {}, emptyImage, None)
      cells[layer_id] = [ [ cocos.tiles.RectCell(h, v, 16, 16, {}, dummyTile) for h in range(hsize) ] for v in range(vsize)]

    return cells

  # adds RectMapLayers to scroller one by one
  def createRectMapLayers(self):

    for layer_id in self.layers:
      rectMapLayer = cocos.tiles.RectMapLayer(layer_id, 16, 16, self.cells[layer_id], None, {})
      layerSortOrder = self.layers.index(layer_id)

      self.scroller.add(rectMapLayer, layerSortOrder, layer_id)

  # obtains a layer by applying rules (specific for that layer) to
  # data stored in a world object
  def getRectMapLayer(self, layer_id):
    return cocos.tiles.RectMapLayer(layer_id, 16, 16, self.Cells[layer_id], None, {})

  # creates a cell matrix based on data in the world object.
  # the matrix holds an image for every cell
  def updateLayers(self, world, init):

    emptyImage = self.tileset['empty']

    if init == True:
      # initial situation: update every cell in every RectMapLayer
      tilesToUpdate = [(v,h) for v in range(0, world.vsize) for h in range(0, world.hsize)]
    else:
      tilesToUpdate = world.listOfUpdateableTiles
      print tilesToUpdate

    for c in tilesToUpdate:

      v = c[0]
      h = c[1]

      image = None
      tile = None

      for layer_id in self.layers:

        if layer_id == 'land':

          # determine terrain type
          terrainType = world.resourceMap['land'][v][h]
          if terrainType == 0:
            #r1 = random.randrange(0,16)
            waterDepth = int(min(7,max(0,world.resourceMap['altitude'][v][h] / world.waterLevel * 8)))
            image = self.tileset['water'][waterDepth]
          elif terrainType == 1:
            #r2 = random.randrange(0,16)
            shadowValue = int(min(6,max(0,3 - world.resourceMap['shadow'][v][h] / 4)))
            image = self.tileset['land'][shadowValue]

        elif layer_id == 'human':

          # determine houses (which are not actual "buildings")
          pop = world.resourceMap['human'][v][h]
          idx = max(0,min(int(pop/2),7))
          if pop > 0:
            image = self.tileset['house'][idx]

          # determine if a building is present
          building = world.buildingAtCell(h, v)

          if building != None:
            image = self.tileset[building]

        elif layer_id == 'forest':

          # determine forest
          forest = world.resourceMap['forest'][v][h]
          grass = world.resourceMap['grass'][v][h]
          if forest > grass:
            idx = min(3,max(int(forest/4),0))
            rnd = int(12 * random.random())
            image = self.tileset['forest'][rnd*4+idx]
          elif world.resourceMap['land'][v][h] == 1:
            idx = min(3,max(int(grass/2),0))
            rnd = int(12 * random.random())
            image = self.tileset['grass'][rnd*4+idx]

        # create tile
        if image != None:
          tile = cocos.tiles.Tile(layer_id, {}, image, None)

        #print 'yay! ', c, layer_id
        #self.cells[layer_id][v][h] = cocos.tiles.RectCell(h, v, 16, 16, {}, tile)

        #print self.scroller.get(layer_id).cells[v][h]
        self.scroller.get(layer_id).cells[v][h] = cocos.tiles.RectCell(h, v, 16, 16, {}, tile)

        if init==False:
          del self.scroller.get(layer_id)._sprites[(h*16, v*16)]

    # screen refresh
    for layer_id in self.layers:
      x, y = self.scroller.get(layer_id).position #, self.scroller.get(layer_id).view_y
      # x, y, w, h, x_offset, y_offset
      self.scroller.get(layer_id).set_view(0, 0, 1024, 1024)

if __name__ == '__main__':

  def loadWorld():

    import json

    f = open('params.json','r')
    dataRaw = f.read()
    f.close()
    d = json.loads(dataRaw)

    #global w
    return world.World(d)

  layers = ['land', 'human', 'forest']
  w = loadWorld()

  cocos.director.director.init(width=512, height=512, do_not_scale=True, resizable=False)

  g = Graphics(layers, w)
