import pyglet
from pyglet.window import key, mouse
import cocos
from cocos import tiles, actions, layer
import random
import json
from game import world, graphics



class HeadUpDisplay(cocos.layer.Layer):

  def __init__(self):
    super( HeadUpDisplay, self ).__init__()
    
    label = cocos.text.Label('HUD text',
                            font_name='Times New Roman',
                            font_size=16,
                            anchor_x='center', anchor_y='center')
                
    label.position = 100,500
    self.add(label)
             
             
                
# load world from file
def loadWorld():

  f = open('params.json','r')
  dataRaw = f.read()
  f.close()
  d = json.loads(dataRaw)

  #global w 
  return world.world(d)
           

def main():
  global keyboard, mouse, scroller, world, graphics
  
  from cocos.director import director
  director.init(width=800, height=600, do_not_scale=True, resizable=True)

  # load world
  world = loadWorld()

  # create graphics object
  layers = ['land','forest','human']#,'grass','swamp']
  graphics = graphics.graphics(layers, world)
 
  hud_layer = HeadUpDisplay()
  
  main_scene = cocos.scene.Scene(graphics.scroller)
  main_scene.add(hud_layer, 999, 'HUD')

  keyboard = key.KeyStateHandler()
  
  director.window.push_handlers(keyboard)
    
  def on_mouse_motion(x, y, dx, dy):
    graphics.scroller.set_focus(x * 1024 / 800, y * 1024 / 600)
      
  def on_key_press(key, modifier):
    if key == pyglet.window.key.ENTER:
      world.update(1)      
      graphics.fillCellMatrices(world)
      graphics.updateLayers()
      print('time: {0}, pop: {1}, forest: {2}, change: {3}').format(world.age, int(world.cumulative('human')), int(world.cumulative('forest')), int(world.totalChange()))
      
    elif key == pyglet.window.key.Z:
      if graphics.scroller.scale == .50:
        graphics.scroller.do(actions.ScaleTo(1, 1))
      else:
        graphics.scroller.do(actions.ScaleTo(.50, 1))
          
  director.window.push_handlers(on_key_press)
  director.window.push_handlers(on_mouse_motion)    

  director.run(main_scene)
    

# run game
if __name__ == '__main__':
  main()

