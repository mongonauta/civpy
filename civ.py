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
    
    self.label1 = cocos.text.Label('HUD text 1', anchor_x='left', anchor_y='bottom')
    self.label2 = cocos.text.Label('HUD text 2', anchor_x='left', anchor_y='bottom')
    self.label3 = cocos.text.Label('HUD text 3', anchor_x='left', anchor_y='bottom')
    self.label4 = cocos.text.Label('HUD text 4', anchor_x='left', anchor_y='bottom')
    self.label5 = cocos.text.Label('HUD text 5', anchor_x='left', anchor_y='bottom')
    self.label6 = cocos.text.Label('HUD text 5', anchor_x='left', anchor_y='bottom')
                 
    self.label1.position = 0,0
    self.label2.position = 0,16
    self.label3.position = 0,32
    self.label4.position = 0,48
    self.label5.position = 0,64
    self.label6.position = 0,80
        
    self.add(self.label1)
    self.add(self.label2)
    self.add(self.label3)
    self.add(self.label4)
    self.add(self.label5)
    self.add(self.label6)
             
  #def changeHud(self, label1text, label2text, label3text):
  #  self.label1.element.text = label1text
  #  self.label2.element.text = label2text
  #  self.label3.element.text = label3text
             
     
class MouseDisplay(cocos.layer.Layer):

    is_event_handler = True     #: enable director.window events

    def __init__(self):
        super( MouseDisplay, self ).__init__()

        self.posx = 0
        self.posy = 0
        self.text = cocos.text.Label('No mouse events yet', font_size=18, x=self.posx, y=self.posy, anchor_x='left', anchor_y='bottom' )
        self.add( self.text )

    def update_text (self, x, y):
        text = 'Mouse @ %d,%d' % (x, y)
        self.text.element.text = text
        self.text.element.x = self.posx
        self.text.element.y = self.posy

    def on_mouse_motion (self, x, y, dx, dy):
        """Called when the mouse moves over the app window with no button pressed

        (x, y) are the physical coordinates of the mouse
        (dx, dy) is the distance vector covered by the mouse pointer since the
          last call.
        """
        self.update_text (x, y)

    def on_mouse_drag (self, x, y, dx, dy, buttons, modifiers):
        """Called when the mouse moves over the app window with some button(s) pressed

        (x, y) are the physical coordinates of the mouse
        (dx, dy) is the distance vector covered by the mouse pointer since the
          last call.
        'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
        'modifiers' is a bitwise or of pyglet.window.key modifier constants
           (values like 'SHIFT', 'OPTION', 'ALT')
        """
        self.update_text (x, y)

    def on_mouse_press (self, x, y, buttons, modifiers):
        """This function is called when any mouse button is pressed

        (x, y) are the physical coordinates of the mouse
        'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
        'modifiers' is a bitwise or of pyglet.window.key modifier constants
           (values like 'SHIFT', 'OPTION', 'ALT')
        """
        self.posx, self.posy = director.get_virtual_coordinates (x, y)
        self.update_text (x,y)        
        
                
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
  director.init(width=512, height=512, do_not_scale=True, resizable=True)

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
  
    # set focus
    graphics.scroller.set_focus(x, y)
    
    # determine pixel coordinates of cursor
    mx, my = graphics.scroller.pixel_from_screen(x, y)
    
    # determine which cell cursor is at
    layer = graphics.scroller.get('land')
    cell = layer.get_at_pixel(mx, my)
    
    # change HUD to display attributes of cell
    if cell:
     j = cell.position[1]/16
     i = cell.position[0]/16
     altitude = world.resourceMap['altitude'][i][j]
     forest = world.resourceMap['forest'][i][j]
     human = world.resourceMap['human'][i][j]
       
     hud_layer.label1.element.text = 'altitude: ' + str(world.resourceMap['altitude'][i][j])
     hud_layer.label2.element.text = 'forest: ' + str(world.resourceMap['forest'][i][j])
     hud_layer.label3.element.text = 'human: ' + str(world.resourceMap['human'][i][j])
     hud_layer.label4.element.text = 'land: ' + str(world.resourceMap['land'][i][j])
     hud_layer.label5.element.text = 'temperature: ' + str(world.resourceMap['temperature'][i][j])
     hud_layer.label6.element.text = 'coordinates (x,y) / (j,i): (' + str(mx) + ',' + str(my) + ') / (' + str(j) + ',' + str(i) + ')'
     
     
     #hud_layer.changeHud(altitude, forest, human)
     
      
  def on_key_press(key, modifier):
    if key == pyglet.window.key.ENTER:
      world.update(1)      
      graphics.fillCellMatrices(world)
      graphics.updateLayers()
      print('time: {0}, pop: {1}, forest: {2}, change: {3}').format(world.age, int(world.cumulative('human')), int(world.cumulative('forest')), int(world.totalChange()))
      
    elif key == pyglet.window.key.Z:
      if graphics.scroller.scale == .50:
        graphics.scroller.do(actions.ScaleTo(1, 0))
      else:
        graphics.scroller.do(actions.ScaleTo(.50, 0))
          
  director.window.push_handlers(on_key_press)
  director.window.push_handlers(on_mouse_motion)    

  director.run(main_scene)
    

# run game
if __name__ == '__main__':
  main()

