##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################

import altitude
import random
import time
import numpy as np

class World:

  # on initialization, create:
  # * an empty resource map defined by vertical and horizontal sizes
  # * an empty capacity map defined by vertical and horizontal sizes


  def __init__( self, d ): # resources, influenceMatrix, buildingInfluence, buildingSet, humanSpreadThreshold, vsize, hsize

    # age of world
    self.age = 0

    # map size parameters
    self.vsize = d['vsize']
    self.hsize = d['hsize']

    # a list with resource names
    self.resources = d['resources']

    self.altitude = index(self.resources['altitude']])
    self.relief = index(self.resources['relief']])
    self.land = index(self.resources['land']])
    self.water = index(self.resources['water']])
    self.rainfall = index(self.resources['rainfall']])
    self.temperature = index(self.resources['temperature']])
    self.forest = index(self.resources['forest']])
    self.grass = index(self.resources['grass']])
    self.human = index(self.resources['human']])
    self.wilderness = index(self.resources['wilderness']])
    self.altitude = index(self.resources['']])

    self.waterLevel = d['waterLevel']

    # resources that are updated throughout the game
    self.updateableResources = d['updateableResources']

    # determines distance at which surrounding resources have influence
    self.resourceInfluenceRange = d['resourceInfluenceRange']

    self.productionFlow = d['productionFlow']

    # a dictionary with building definitions
    self.buildingInfluence = d['buildingInfluence']

    # cost to build a building, taken from surrounding resources
    self.buildingCost = d['buildingCost']

    # gives range of values per resource where buildings cannot be built
    # e.g. relief = [0.5, 9999] means we cannot build when relief in
    # that location is higher than 0.5 (and, theoretically, lower than 9999)
    self.buildingNotAllowed = d['buildingNotAllowed']

    # if sum of humans on surrounding tiles exceeds this number, tile gets a human
    self.humanSpreadThreshold = d['humanSpreadThreshold']

    self.seedPopulation = d['seedPopulation']

    # range of influence
    self.maxBuildingDistance = 1

    # set of buildings
    self.buildingSet = {}

    # create map with all bells & whistles
    self.createMap()

    # changeMap[v][h] = 1 if tile has changed since last update, 0 if not
    # for obvious reasons, set changeMap to 1 on first go
    self.changeMap = np.ndarray(shape=(self.hsize, self.vsize), dtype=np.uint16)

    # initial set of updateable tiles is empty, to be filled with changemap
    self.listOfUpdateableTiles = [(v, h) for v in range(self.vsize) for h in range(self.hsize)]


  # returns a land map. depending on altitude, landMap is either land or water
  def generateLandMap(self, altitudeMap):
    result = [ [0]*self.hsize for i in range(self.vsize) ]
    for v in range(self.vsize):
      for h in range(self.hsize):
        if altitudeMap[v][h] > self.waterLevel:
          result[v][h] = 1

    return result

  # returns a water map. waterMap is the reverse of landMap. it is there to prevent people living on water
  def generateWaterMap(self, altitudeMap):
    result = [ [0]*self.hsize for i in range(self.vsize) ]
    for v in range(self.vsize):
      for h in range(self.hsize):
        if altitudeMap[v][h] <= self.waterLevel:
          result[v][h] = 1

    return result



  # returns a map with temperature values, according to the algorithm specified
  def generateTemperatureMap(self, altitudeMap):
    return [ [abs(self.vsize/2)-abs(i-self.vsize/2)]*self.hsize for i in range(self.vsize) ]



  # returns a map with rainfall values, according to the algorithm specified
  def generateRainfallMap(self, altitudeMap):
    result = []
    for v in range(self.vsize):
      result.append([])
      for h in range(self.hsize):
        result[v].append(random.random())

    return result



  # returns a map with grass values, according to the algorithm specified
  def generateGrassMap(self, rainfallMap, forestMap):
    result = []
    for v in range(self.vsize):
      result.append([])
      for h in range(self.hsize):
        result[v].append(max(0, 8 - forestMap[v][h]))

    return result



  # returns a map with forest values, according to the algorithm specified
  def generateForestMap(self):
    result = []
    for v in range(self.vsize):
      result.append([])
      for h in range(self.hsize):
        value = 0
        if self.resourceMap[self.altitude][v][h] > 0.7:
          value = self.resourceMap[self.temperature][v][h] * self.resourceMap[self.rainfall][v][h]
        result[v].append(value)

    return result

  def generateWildernessMap(self):
    result = []
    for v in range(self.vsize):
      result.append([])
      for h in range(self.hsize):
        value = 1
        if self.resourceMap[self.human][v][h] > 0:
          value = 0

        result[v].append(value)

    return result

  # returns a 3d matrix filled with zeros
  def zeroMap( self ):
    return 0 * np.ndarray(shape=(len(self.resources), self.vsize, self.hsize), dtype=np.uint16)

  # create a 2d map of size vsize x hsize containing a dict of items in each location.
  # each resource is set to its default
  def createMap( self ):

    # initial map only contains zeros
    self.resourceMap = 0 * np.ndarray(shape=(len(self.resources), self.vsize, self.hsize), dtype=np.uint16)

    # generate a vsize x hsize altitude map and relief map
    self.resourceMap[self.altitude], self.resourceMap[self.relief] = altitude.generateAltitudeMap(self.vsize, self.hsize)

    # determine where to put land, where to put sea
    self.resourceMap[self.land] = self.generateLandMap()

    # determine where to put land, where to put sea
    self.resourceMap[self.water] = self.generateWaterMap()

    # calculate temperature
    self.resourceMap[self.temperature] = self.generateTemperatureMap()

    # calculate rainfall
    self.resourceMap[self.rainfall] = self.generateRainfallMap()

    # calculate forest
    self.resourceMap[self.forest] = self.generateForestMap()

    # calculate grass
    self.resourceMap[self.grass] = self.generateGrassMap()

    #calculate where to seed human population
    v = int(self.vsize/2)
    h = int(self.hsize/2)

    while self.resourceMap[self.land][v][h] == 0:
      v = min(self.vsize-1, max(0, v + random.randrange(-1,2)))
      h = min(self.hsize-1, max(0, h + random.randrange(-1,2)))

    self.resourceMap[self.human][v][h] = self.seedPopulation

    # calculate wilderness (places where people aren't)
    self.resourceMap[self.land] = self.generateWildernessMap()

    return result

  # update state of world given by amount of time passed
  def update( self, dt ):

    newlistOfUpdateableTiles = []

    # increase age
    self.age += dt

    # map that records delta (=change) in resources
    newMap = self.zeroMap()
    self.changeMap = [[0]*self.hsize for i in range(self.vsize)]

    # for v in range(self.vsize):
    #   for h in range(self.hsize):

    # calculate surroundings (only where we expect change)
    for c in self.listOfUpdateableTiles:
      v, h = c[0], c[1]

      self.calcAllSurroundings(v, h)

    # whiz bang matrix calculation of all resources at once!
    # does not take into account humans on sea impossibility nor spawn threshold yet

    # first, make 4d matrices so they can be easily manipulated
    a = self.resourceMap[np.newaxis,:,:,:]
    b = self.surroundingsMap[np.newaxis,:,:,:]

    # then, flatten
    newMap = sum(a * self.inplaceManipulation) + sum(b * self.surroundingsManipulation) 

      # determine change in values of tile TODO: only do this for resources that actually change e.g. humans, grass
      for k in self.updateableResources:

        newMap[k][v][h] = self.updateTile(v, h, k, surroundings)

       # determine if change has taken place, important for rendering map
        if self.changeMap[v][h] == 0 and newMap[k][v][h] != self.resourceMap[k][v][h]:
          self.changeMap[v][h] = 1
          newlistOfUpdateableTiles = list(set(newlistOfUpdateableTiles) | set(self.getListOfSurroundingCoordinates(v, h, 1)))

    # add delta to resource map
    for k in self.updateableResources:
      self.resourceMap[k] = newMap[k]

    # renew tilestobeupdated list, adding/substracting tiles that were not
    self.listOfUpdateableTiles = newlistOfUpdateableTiles

  def calcAllSurroundings( self, v, h ):
    # based on the type of surroundings
    result = {k:0 for k in self.resources}
    resourceRange = self.resourceInfluenceRange
    for k in self.resources:
      result[k] = self.calcOneSurrounding( v, h, k, resourceRange[k] )

    return result

  def getListOfSurroundingCoordinates( self, v, h, d):
    result = []

    # add corner coordinates (always 4)
    result.append( (v - d, h - d) )
    result.append( (v - d, h + d) )
    result.append( (v + d, h - d) )
    result.append( (v + d, h + d) )

    # add edge coordinates (4x d)
    for i in range(-d + 1, d):
      result.append( (v - d, h + i) )
      result.append( (v + d, h + i) )
      result.append( (v + i, h - d) )
      result.append( (v + i, h + d) )

    return result

  def calcOneSurrounding( self, v, h, k, r ):
    # sum resources surrounding tile (v, h) by running circles around (v, h)
    # until the target tile is too far away (defined by r)

    # by default, the value of the tile itself is automatically included
    result = self.resourceMap[k][v][h]

    if r > 0:

      # set flag to determine if we should look in a wider circle
      increaseDiameter = True

      # set initial diameter of "circle" around (v, h). This number will increase
      # if we keep finding tiles whose distance is less than the resource range
      circleDiameter = 0

      while increaseDiameter == True:

        # At this point, set flag to False: if we encounter one or more tiles
        # that are within distance, it will be set to True (meaning that if we
        # find tiles within distance in this circle, chances are this is true
        # in a wider circle)
        increaseDiameter = False

        # increase circle diameter
        circleDiameter += 1
        # make a list of coordinates that circle (v, h) d tiles away
        coordList = self.getListOfSurroundingCoordinates(v, h, circleDiameter)

        # look at each coordinate. If it's not outside the map and the distance is
        # not too great, add corresponding value to the sum total, penalized by distance
        for c in coordList:
          vv = c[0]
          hh = c[1]
          distance = self.distance((v,h), (vv,hh))

          if vv >= 0 and vv < self.vsize and hh >= 0 and hh < self.hsize and distance <= r:
            increaseDiameter = True
            distancePenalty = 1.0 * (r+1 - distance) / (r+1)
            result += self.resourceMap[k][vv][hh] * distancePenalty

    return result


  def updateTile( self, v, h, k, surroundings ):
    result = 0
    # formula for population (TODO: should be formalized by a matrix of some sort)


    # ooooooolllllldddddddd (spookyvoice)
    if  k == 'human':
      if surroundings['human'] >= self.humanSpreadThreshold:
        result = max(0,  0.25 * surroundings['grass']  # produces food
                       #- min(0, -10 + 0.10 * surroundings['human']) # source of disease
                       - 1.00 * self.resourceMap['forest'][v][h] # you can't live where the trees are
                       - 9999.0 * self.resourceMap['water'][v][h] # you can't live where the fish are
                       + 2.0 * surroundings['water'] # but you can eat fish around you
                       - 0.2 * surroundings['wilderness']) # 'wolves' to prevent edge of town to be more populated than center

    # formula for grass (notice grass and humans are interdependent:
    # human needs grass, but grass and human can't coexist on same tile)
    elif k == 'grass':
      result = max(0, 8 - 1.00 * self.resourceMap['forest'][v][h]
                        - 0.20 * self.resourceMap['human'][v][h])

    # formula for wilderness:
    elif k == 'wilderness':
      result = 1
      if self.resourceMap['human'][v][h] > 0:
        result = 0

    # don't bother with the rest for now
    else:
      result = self.resourceMap[k][v][h]

    # eeeeendddddd ooooffff oooooolllllllddddd

    return result


  def distance( self, coord1, coord2 ):

    result = None

    v1 = coord1[0]
    h1 = coord1[1]

    v2 = coord2[0]
    h2 = coord2[1]

    result = abs(v1 - v2) + abs(h1 - h2)

    return result


  # load a world from a dict passed to the function
  def setWorld(self, resources, influenceMatrix, resourceMap, buildingInfluence, buildingSet, humanSpreadThreshold ):
    self.resources = resources
    self.influenceMatrix = influenceMatrix
    self.resourceMap = resourceMap
    self.buildingInfluence = buildingInfluence
    self.buildingSet = buildingSet
    self.humanSpreadThreshold = humanSpreadThreshold
    k = resources.keys()
    self.vsize = len(resourceMap[k[0]])
    self.hsize = len(resourceMap[k[0]][0])



  # return world as a dict returned from the function
  def putWorld( self ):

    return self.resources, self.influenceMatrix, self.resourceMap, self.humanSpreadThreshold



  # returns cumulative quantity of a certain resource
  def cumulative( self, key ):

    c = 0

    for v in range(self.vsize):
      for h in range(self.hsize):
        c = c + self.resourceMap[key][v][h]

    return c


  # returns number of cells that are "subject to change"
  def totalChange( self ):

    c = 0

    for v in range(self.vsize):
      for h in range(self.hsize):
        c = c + self.changeMap[v][h]

    return c


  # builds a building of certain type on location x, y
  def buildBuilding(self, j, i, buildingType):

    success = False

    if not((j, i) in self.buildingSet):
      # nothing should be built on location (x, y) yet
      self.buildingSet[(j, i)] = buildingType

      self.changeMap[i][j] = 1
      success = True

    return success



  def buildingAtCell(self, j, i):

    result = None

    if (j, i) in self.buildingSet:

      result = self.buildingSet[(j, i)]

    return result



# only run this if world.py is called directly from command line
if __name__ == "__main__":

  print 'Youre doing it wrong'
