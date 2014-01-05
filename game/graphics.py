import pyglet
import random

# TODO: change this so that multiple batches are updated (if necessary). each batch corresponding to a resource.
# see http://www.pyglet.org/doc/programming_guide/displaying_images.html (halfway down page)
def fillBatch(world, imageList, batch, oldListOfSprites):

  background = pyglet.graphics.OrderedGroup(0)
  foreground = pyglet.graphics.OrderedGroup(1)
  
  for v in range(world.vsize):
    for h in range(world.hsize):
    
      if world.changeMap[v][h] != 0:
      
        # determine terrain type
        terrainType = world.resourceMap['land'][v][h]
        if terrainType == 0:
          r1 = random.randrange(0,16)
          image = imageList['water'][r1]
        elif terrainType == 1:
          r2 = random.randrange(0,16)
          image = imageList['land'][r2]      
        else:
          image = tiles[terrainType]

        oldListOfSprites.append(pyglet.sprite.Sprite(img=image, x=h*16, y=v*16, batch=batch, group=background))

        # determine houses
        pop = world.resourceMap['human'][v][h]
        idx = min(int(pop/2),7)
        if pop > 0:
          #print v, h, pop, idx
          oldListOfSprites.append(pyglet.sprite.Sprite(img=imageList['house'][idx], x=h*16, y=v*16, batch=batch, group=foreground))
        
        # determine forest
        forest = world.resourceMap['forest'][v][h]
        idx = min(int(forest/20),3)
        if forest > 0:
          oldListOfSprites.append(pyglet.sprite.Sprite(img=imageList['forest'][idx], x=h*16, y=v*16, batch=batch, group=foreground))
      
  return oldListOfSprites
