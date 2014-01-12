testinfo = "s, q"
tags = "TMX, tiles, Driver"

import pyglet
from pyglet.window import key
from pyglet.window import mouse

pyglet.resource.path.append(pyglet.resource.get_script_home())
pyglet.resource.reindex()

import cocos
from cocos import tiles, actions, layer

class DriveCar(actions.Driver):
    def step(self, dt):
        # handle input and move the car
        self.target.rotation += (keyboard[key.RIGHT] - keyboard[key.LEFT]) * 150 * dt
        self.target.acceleration = (keyboard[key.UP] - keyboard[key.DOWN]) * 400
        if keyboard[key.SPACE]: self.target.speed = 0
        super(DriveCar, self).step(dt)
        scroller.set_focus(self.target.x, self.target.y)
       

def main():
    global keyboard, mouse, scroller
    from cocos.director import director
    director.init(width=800, height=600, do_not_scale=True, resizable=True)

   
    #car_layer = layer.ScrollableLayer()
    #car = cocos.sprite.Sprite('car.png')
    #car_layer.add(car)
    #car.position = (200, 100)
    #car.max_forward_speed = 200
    #car.max_reverse_speed = -100
    #car.do(DriveCar())

    scroller = layer.ScrollingManager()
    test_layer = tiles.load('road-map.tmx')['map0']
    scroller.add(test_layer)
    #scroller.add(car_layer)

    main_scene = cocos.scene.Scene(scroller)

    keyboard = key.KeyStateHandler()
    #mouse = mouse.MouseStateHandler()
    
    director.window.push_handlers(keyboard)
    #director.window.push_handlers(mouse)

    def on_mouse_motion(x, y, dx, dy):
      scroller.set_focus(x+200, y+150)
        
    def on_key_press(key, modifier):        
      if key == pyglet.window.key.Z:
        if scroller.scale == .75:
          scroller.do(actions.ScaleTo(1, 2))
        else:
          scroller.do(actions.ScaleTo(.75, 2))
      elif key == pyglet.window.key.D:
        test_layer.set_debug(True)
            
    director.window.push_handlers(on_key_press)
    director.window.push_handlers(on_mouse_motion)    

    director.run(main_scene)

if __name__ == '__main__':
    main()
