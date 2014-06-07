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
  global i, j, fx, fy, winx, winy, scrollablex, scrollabley

  # coordinates of current cell
  i = 0
  j = 0

  winx = 800
  winy = 600

  # sprite size
  spritex = 16
  spritey = 16

  from cocos.director import director
  director.init(width=winx, height=winy, do_not_scale=True, resizable=False)

  # load world
  world = loadWorld()

  # map size (pixels)
  canvasx = world.hsize * spritex
  canvasy = world.vsize * spritey

  # amount of pixels we can scroll around
  scrollablex = max(0, canvasx - winx)
  scrollabley = max(0, canvasy - winy)

  # create graphics object
  layers = ['land','forest','human']
  g = graphics.Graphics(layers, world)

  hud_layer = graphics.HeadUpDisplay(16, 0, 0, 10)

  main_scene = cocos.scene.Scene(g.scroller)
  main_scene.add(hud_layer, 999, 'HUD')

  keyboard = key.KeyStateHandler()

  director.window.push_handlers(keyboard)

  def on_mouse_motion(x, y, dx, dy):

    global i, j, winx, winy, scrollablex, scrollabley

    x_focus = (1.0*x)/winx * scrollablex + winx/2
    y_focus = (1.0*y)/winy * scrollabley + winy/2

    g.scroller.set_focus(x_focus, y_focus)

    # determine where cursor is on the map
    mx, my = g.scroller.pixel_from_screen(x, y)

    # given pixel coordinates, determine which cell cursor is at
    layer = g.scroller.get('land')
    cell = layer.get_at_pixel(mx, my)

    # change HUD to display attributes of cell
    if cell:
      i = cell.position[0]/16
      j = cell.position[1]/16

      altitude = world.resourceMap['altitude'][i][j]
      forest = world.resourceMap['forest'][i][j]
      human = world.resourceMap['human'][i][j]
      building = world.buildingAtCell(j, i)

      hud_layer.label[0].element.text = 'coordinates (x, y) / (fx,fy) / (mx,my) / (j,i): (' + str(x) + ',' + str(y) + ') / (' + str(x_focus) + ',' + str(y_focus) + ') / (' + str(mx) + ',' + str(my) + ') / (' + str(j) + ',' + str(i) + ')'
      hud_layer.label[1].element.text = 'altitude   : ' + str(world.resourceMap['altitude'][i][j])
      hud_layer.label[2].element.text = 'land       : ' + str(world.resourceMap['land'][i][j])
      hud_layer.label[3].element.text = 'forest     : ' + str(world.resourceMap['forest'][i][j])
      hud_layer.label[4].element.text = 'grass      : ' + str(world.resourceMap['grass'][i][j])
      hud_layer.label[5].element.text = 'wilderness : ' + str(world.resourceMap['wilderness'][i][j])
      hud_layer.label[6].element.text = 'human      : ' + str(world.resourceMap['human'][i][j])
      hud_layer.label[7].element.text = 'hum.srrndng: ' + str(world.calcOneSurrounding(j,i,'human',1))
      hud_layer.label[9].element.text = 'building   : ' + str(building)


      #hud_layer.changeHud(altitude, forest, human)


  def on_key_press(key, modifier):

    global fx, fy, offsetx, offsety

    if key == pyglet.window.key.ENTER:
      # next turn

      print('time: {0}, pop: {1}, forest: {2}, wilderness: {3}, change: {4}').format(world.age,
                                                                              int(world.cumulative('human')),
                                                                              int(world.cumulative('forest')),
                                                                              int(world.cumulative('wilderness')),
                                                                              int(world.totalChange()))

      t = time.time()
      world.update(1)
      print 'world update: ', time.time() - t

      t = time.time()
      g.fillCellMatrices(world)
      print 'fill cells: ', time.time() - t

      t = time.time()
      g.updateLayers()
      print 'update layers: ', time.time() - t

    elif key == pyglet.window.key.Z:
      # zoom

      if g.scroller.scale == .50:
        g.scroller.do(actions.ScaleTo(1, 0))
      else:
        g.scroller.do(actions.ScaleTo(.50, 0))

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
  director.window.push_handlers(on_mouse_motion)

  director.run(main_scene)


# run game
if __name__ == '__main__':
  main()
