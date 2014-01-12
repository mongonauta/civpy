import cocos

cocos.director.director.init()
r = cocos.tiles.load('tiled_examples/desert.tmx')
map = r['Ground']
map.set_view(0, 0, map.px_width, map.px_height)

scene = cocos.scene.Scene(map)
cocos.director.director.run(scene)

manager = cocos.tiles.ScrollingManager()
manager.add(map)
manager.set_focus(20, 20)

