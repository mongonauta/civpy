import pyglet
import cocos
import random
import json
import time
from pyglet.window import key, mouse
from cocos import tiles, actions, layer
from game import world, graphics

# load world from file
def loadWorld():

  f = open('params.json','r')
  dataRaw = f.read()
  f.close()
  d = json.loads(dataRaw)

  #global w
  return world.World(d)


def main():
  global keyboard, mouse, scroller, world, g
  global i, j, fx, fy, winx, winy, canvasx, canvasy, layers, scrollSpeed

  # coordinates of current cell
  i = 0
  j = 0

  # window size
  winx = 1024
  winy = 600

  # focus coordinates
  fx = 0
  fy = 0

  # sprite size
  spritex = 16
  spritey = 16

  # scroll speed
  scrollSpeed = 1

  from cocos.director import director
  director.init(width=winx, height=winy, do_not_scale=True, resizable=False)

  # load world
  world = loadWorld()

  # map size (pixels)
  canvasx = world.hsize * spritex
  canvasy = world.vsize * spritey

  # create graphics object
  layers = ['land','forest','human']
  g = graphics.Graphics(layers, world)

  hud_layer = graphics.HeadUpDisplay(16, 0, 0, 10)
  menu_layer = graphics.Menu()

  main_scene = cocos.scene.Scene(g.scroller)
  main_scene.add(hud_layer, 998, 'HUD')
  #main_scene.add(menu_layer, 999, 'menu')

  keyboard = key.KeyStateHandler()

  director.window.push_handlers(keyboard)


  def setFocus(x, y):
    global layers, canvasx, canvasy

    t = time.time()

    # given pixel coordinates, determine which cell cursor is at
    for layer_id in layers:
      # x, y, w, h, x_offset, y_offset
      g.scroller.get(layer_id).set_view(0, 0, canvasx, canvasy, -x, -y)

    print 'focus:', time.time() - t

  def on_mouse_press(x, y, buttons, modifiers):

    global winx, winy, fx, fy, canvasx, canvasy, scrollSpeed

    if buttons & mouse.LEFT:

      mx, my = g.scroller.pixel_from_screen(x, y)

      fx = min(canvasx - winx, max(0, mx))
      fy = min(canvasy - winy, max(0, my))

      setFocus(fx, fy)

  '''
  def on_mouse_drag(x, y, dx, dy, buttons, modifiers):

    global winx, winy, fx, fy, canvasx, canvasy, scrollSpeed

    if buttons & mouse.LEFT:

      fx = min(canvasx - winx, max(0, fx - scrollSpeed * dx))
      fy = min(canvasy - winy, max(0, fy - scrollSpeed * dy))

      setFocus(fx, fy)
  '''

  def on_mouse_motion(x, y, dx, dy):

    global i, j, winx, winy, fx, fy, scrollablex, scrollabley, canvasx, canvasy, layers

    #fx = (1.0*x)/winx * (canvasx - winx)
    #fy = (1.0*y)/winy * (canvasy - winy)

    #setFocus(fx, fy)

    # determine where cursor is on the map
    mx, my = g.scroller.pixel_from_screen(x, y)

    # given pixel coordinates, determine which cell cursor is at
    layer = g.scroller.get(layers[0])
    cell = layer.get_at_pixel(mx, my)

    #tile = cocos.tiles.Tile('land', {}, g.tileset['house'][4], None)
    #g.scroller.get(layers[0]).cells[20][20] = cocos.tiles.RectCell(0, 0, 16, 16, {}, tile)

    # change HUD to display attributes of cell
    if cell:
      i = cell.position[0]/16
      j = cell.position[1]/16

      building = world.buildingAtCell(j, i)

      hud_layer.label[0].element.text = 'coordinates (x, y) / (fx,fy) / (mx,my) / (j,i): (' + str(x) + ',' + str(y) + ') / (' + str(fx) + ',' + str(fy) + ') / (' + str(mx) + ',' + str(my) + ') / (' + str(j) + ',' + str(i) + ')'
      hud_layer.label[1].element.text = 'alt/shadow   : ' + str(world.resourceMap['altitude'][i][j]) + ' / ' + str(world.resourceMap['shadow'][i][j])

      hud_layer.label[2].element.text = 'land         : ' + str(world.resourceMap['land'][i][j])
      hud_layer.label[3].element.text = 'forest (tot) : ' + str(world.resourceMap['forest'][i][j]) + '(' + str(world.cumulative('forest'))+ ')'
      hud_layer.label[4].element.text = 'grass (tot)  : ' + str(world.resourceMap['grass'][i][j]) + '(' + str(world.cumulative('grass'))+ ')'
      hud_layer.label[5].element.text = 'wldrnss (tot): ' + str(world.resourceMap['wilderness'][i][j]) + '(' + str(world.cumulative('wilderness'))+ ')'
      hud_layer.label[6].element.text = 'human (tot)  : ' + str(world.resourceMap['human'][i][j]) + '(' + str(world.cumulative('human'))+ ')'
      hud_layer.label[7].element.text = 'hum.srrndngs : ' + str(world.calcOneSurrounding(i,j,'human',1))
      hud_layer.label[8].element.text = 'updtbl tiles : ' + str(len(world.listOfUpdateableTiles))
      hud_layer.label[9].element.text = 'building     : ' + str(building)
      hud_layer.label[10].element.text = 'age         : ' + str(world.age)

  def on_key_press(key, modifier):

    global fx, fy, offsetx, offsety, canvasx, canvasy, q

    if key == pyglet.window.key.ENTER:
      # next turn

      t = time.time()
      world.update(1)
      print 'world update: ', time.time() - t

      #t = time.time()
      #g.fillCellMatrices(world)
      #print 'fill cells: ', time.time() - t

      t = time.time()
      g.updateLayers(world, False)

      print 'update layers: ', time.time() - t

    elif key == pyglet.window.key.Z:
      # zoom

      if g.scroller.scale == .50:
        g.scroller.do(actions.ScaleTo(1, 5))
      else:
        g.scroller.do(actions.ScaleTo(.50, 5))

    elif key == pyglet.window.key.R:
      # reset world
      pass

    elif key == pyglet.window.key.H:
      # toggle HUD on/off

      layer = main_scene.get('HUD')
      if layer.visible == False:
        layer.visible = True
      else:
        layer.visible = False

    elif key == pyglet.window.key.SPACE:
      result = world.buildBuilding(j, i, 'townhall')
      if result == True:
        print 'yay'
      else:
        print 'cant build townhall'

  director.window.push_handlers(on_key_press)
  director.window.push_handlers(on_mouse_press)
  #director.window.push_handlers(on_mouse_drag)
  director.window.push_handlers(on_mouse_motion)

  print director.get_window_size()
  director.run(main_scene)

# run game
if __name__ == '__main__':
  main()
