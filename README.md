civpy
-----

github.com/CaptainHennessey/civpy

(c) Captain Hennessey 2013-2014

A civilization game written in Python.

License
-------

Civpy is released under the terms of the MIT license. See [COPYING](COPYING) for more
information or see http://opensource.org/licenses/MIT.

Software Requirements
---------------------
Currently, no clear software requirements are defined. To develop and test,
the following OS/software was used:

- Mac OS X 10.8 Mountain Lion
- Python 2.7
- Pyglet 1.2alpha1
- Cocos2d 0.6.0

Objective
---------
The goal is to maximize human population. There is only one player.

The game takes place on a 2D map. Each tile roughly represents a 100x100m square.

Human population is influenced by its surroundings. There are multiple resources
that make up these surroundings. A positive influence is grassland (enabling
farming) and water (enabling fishing). A negative influence is wilderness
(areas of the map where population is 0): this keeps a town from expanding
indefinitely.

Grassland is negatively affected by forests (because of the trees) and the
presence of humans.

Besides these influences, there are constraints in place. Humans can't live on
water, and population in forests is severely restricted by the presence of trees.

Each resource has a different influence range. For now, most resources have
an influence range of 1, meaning that e.g. humans on a certain tile can only
benefit from grassland on the same tile or at most 1 tile away.
