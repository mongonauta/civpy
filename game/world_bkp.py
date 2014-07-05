##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################
##############################################################################

import altitude
import random

class world:



  # on initialization, create:
  # * an empty resource map defined by vertical and horizontal sizes
  # * an empty capacity map defined by vertical and horizontal sizes


  def __init__( self, d ): # resources, influenceMatrix, buildingInfluence, buildingSet, humanSpreadThreshold, vsize, hsize

    # age of world
    self.age = 0

    # a list with resource names
    self.resources = d['resources']

    self.waterLevel = d['waterLevel']

    # a dictionary ("sparse matrix") containing resource dependencies
    self.influenceMatrix = d['influenceMatrix']

    self.productionFlow = d['productionFlow']

    self.harvestable = d['harvestable']

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

    # map size parameters
    self.vsize = d['vsize']
    self.hsize = d['hsize']

    self.seedPopulation = d['seedPopulation']

    # range of influence
    self.maxBuildingDistance = 1

    # set of buildings
    self.buildingSet = {}

    # create map with all bells & whistles
    self.resourceMap = self.createMap()

    # changeMap[v][h] = 1 if tile has changed since last update, 0 if not
    # for obvious reasons, set changeMap to 1 on first go
    self.changeMap = [[1]*self.hsize for i in range(self.vsize)]


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
    return [ [(self.vsize/2)**2-(i-self.vsize/2)**2]*self.hsize for i in range(self.vsize) ]



  # returns a map with rainfall values, according to the algorithm specified
  def generateRainfallMap(self, altitudeMap):
    result = []
    for v in range(self.vsize):
      result.append([])
      for h in range(self.hsize):
        result[v].append(random.random())

    return result



  # returns a map with grass values, according to the algorithm specified
  def generateGrassMap(self, altitudeMap, rainfallMap):
    result = []
    for v in range(self.vsize):
      result.append([])
      for h in range(self.hsize):
        result[v].append(random.random() * 10)

    return result



  # returns a map with grass values, according to the algorithm specified
  def generateForestMap(self, altitudeMap, rainfallMap, temperatureMap):
    result = []
    for v in range(self.vsize):
      result.append([])
      for h in range(self.hsize):
        value = 0
        if altitudeMap[v][h] > 0.75:
          value = temperatureMap[v][h] * rainfallMap[v][h]
        result[v].append(value)

    return result



  # returns a 2d matrix filled with zeros
  def zeroMap( self ):
    result = {}

    # then, generate empty maps for resources/states
    for k in self.resources:
      result[k] = [[0]*self.hsize for i in range(self.vsize)]

    return result



  # returns a 2d matrix containing 1s or 0s that determine if we should bother calculating on a specific tile
  # 1: perform calculations on this tile
  # 0: don't perform calculations
  #
  # right now, whenever we're near an inhabited tile -> 1, else 0
  def determineCalculability( self, v, h ):
    result = False

    for vv in range(max(0, v-1), min(self.vsize, v+1)):
      if result == True:
        break

      for hh in range(max(0, h-1), min(self.hsize, h+1)):
        if self.resourceMap['human'][vv][hh] > 0:
          result = True
          break

    return result



  # create a 2d map of size vsize x hsize containing a dict of items in each location.
  # each resource is set to its default
  def createMap( self ):

    result = self.zeroMap()

    # generate a vsize x hsize altitude map and relief map
    result['altitude'], result['relief'] = altitude.generateAltitudeMap(self.vsize, self.hsize)

    # determine where to put land, where to put sea
    result['land'] = self.generateLandMap(result['altitude'])

    # determine where to put land, where to put sea
    result['water'] = self.generateWaterMap(result['altitude'])

    # calculate temperature
    result['temperature'] = self.generateTemperatureMap(result['altitude'])

    # calculate rainfall
    result['rainfall'] = self.generateRainfallMap(result['altitude'])

    # calculate grass
    result['grass'] = self.generateGrassMap(result['altitude'], result['rainfall'])

    # calculate forest
    result['forest'] = self.generateForestMap(result['altitude'], result['rainfall'], result['temperature'])

    #calculate where to seed human population
    v = int(self.vsize/2)
    h = int(self.hsize/2)

    while result['land'][v][h] == 0:
      v = min(self.vsize-1, max(0, v + random.randrange(-1,2)))
      h = min(self.hsize-1, max(0, h + random.randrange(-1,2)))

    result['human'][v][h] = self.seedPopulation

    return result



  def determineChange( self, aResourceMap, aNewMap ):

    result = []

    for v in range(self.vsize):
      result.append([0]*self.hsize)
      for h in range(self.hsize):
        for k in self.resources:
          if aResourceMap[k][v][h] != aNewMap[k][v][h]:
            result[v][h] = 1

    return result



  # update state of world given by amount of time passed
  def update( self, dt ):

    # increase age
    self.age += dt

    # map that records delta (=change) in resources
    newMap = self.zeroMap()

    # calculate growth per tile
    for v in range(self.vsize):
      for h in range(self.hsize):

        # influenceModifier is a vector that modifies the influence matrix for that particular tile
        influenceVector = {}

        # determine 'calculability' (i.e. indicates if we should bother calculating on this tile)
        # TODO: make this work!!!!
        calculability = True #self.determineCalculability(v, h)

        # only do something if people are present on the tile (or if tile is near populated tile)
        #if resourceMap['calculable'][v][h] > 0:
        if calculability == True:

          # s: list of resources on tile
          s = {k:0 for k in self.resources}

          # u: list of cumulative resources in surrounding area (including tile (v, h))
          u = self.getSurroundings(v, h, self.maxBuildingDistance, self.harvestable)

          # calculate growth rate determined by resources, influence matrix and influence vector
          growth = self.calcGrowthrate(u, self.influenceMatrix, influenceVector)

          # calc production
          production = self.calcProduction(s['human'], u)

          # add growth and production
          for k in s:
            delta = 0
            if s[k] > 0:
              delta = growth[k]

            # production. only humans can produce something other than themselves
            if s['human'] > 0 and k != 'human':
              delta =+ production[k]

            newMap[k][v][h] = max(0, s[k] + dt * delta)

    # determine where change has taken place, important for rendering map
    self.changeMap = self.determineChange(self.resourceMap, newMap)

    # add delta to resource map
    self.resourceMap = newMap


  # calculate growth rate of a set of different resources (compounded over an area)
  def calcGrowthrate( self, s, influenceMatrix, influenceVector ):

    result = {k:0 for k in s}

    # modifier
    for k in result:
      if k in influenceVector:
        result[k] = result[k] + influenceVector[k] * s[k]

      if k in influenceMatrix:
        for m in influenceMatrix[k]:
          result[k] = result[k] + influenceMatrix[k][m] * s[m]

    return result


  def distance( self, coord1, coord2 ):

    result = None

    v1 = coord1[0]
    h1 = coord1[1]

    v2 = coord2[0]
    h2 = coord2[1]

    result = abs(v1 - v2) + abs(h1 - h2)

    return result


  # returns modifier of building
  def buildingModifier(self, v, h, k):
    result = 1.0

    if (v, h) in self.buildingSet:
      bdgInf = self.buildingInfluence[self.buildingSet[(v, h)]]

      if k in bdgInf:
        result = bdgInf[k]

    return result

  # returns a list of resources compounded over an area (tile v, h plus surroundings plus indicator if we can "harvest" this resource)
  def getSurroundings(self, v, h, e, harvestable):

    # create dictionary with resources
    result = {k:0 for k in self.resources}

    # sum resources over an area
    for k in self.resources:
      if harvestable[k] == False:

        # if we cannot "harvest" the surrounding area (i.e. temperature cannot be "harvested"), then only measure resource at center tile
        # if a building is present, add its influence to the sum of resources
        result[k] = self.resourceMap[k][v][h] * self.buildingModifier(v, h, k)

      else:

        # forest etc. can be harvested so look in surrounding tiles
        for vv in range(max(0, v-e), min(self.vsize, v+e+1)):
          for hh in range(max(0, h-e), min(self.hsize, h+e+1)):
            result[k] =+ self.resourceMap[k][vv][hh] * self.buildingModifier(vv, hh, k)

    return result

  def calcProduction(self, population, surroundings):
    result = {k:0 for k in self.resources}

    for k in result:
      if k in self.productionFlow:
        f = self.productionFlow[k]
        result[f] =+ population * surroundings[k]

    return result

  # returns resources as string
  def toString(self):

    s = ''

    for k in self.resources:

      s = s + k + '\n----------\n'
      for v in range(self.vsize):
        for h in range(self.hsize):
          s = s + str(self.resourceMap[k][v][h]) + '\t'
        s = s + '\n'
      s = s + '\n\n'

    return s



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


  # example 2
  resources = {'forest':0, 'swamp':0, 'grass':0, 'human':0, 'wood':0}

  influenceMatrix = {'human':{'human' :-0.01,
                              'forest':-0.01,
                              'swamp' :+0.00,
                              'grass' :+0.02,
                              'water' :-9999}
                    }

  resourceMap = {'grass': [[ 2, 2, 2, 2, 1, 1, 0, 0, 0, 0 ],
                           [ 2, 2, 2, 1, 1, 1, 0, 0, 0, 0 ],
                           [ 2, 2, 3, 1, 1, 0, 0, 0, 0, 0 ],
                           [ 2, 2, 1, 1, 1, 0, 0, 0, 0, 0 ],
                           [ 2, 1, 1, 1, 0, 0, 0, 1, 1, 0 ],
                           [ 1, 1, 0, 0, 0, 0, 1, 1, 1, 0 ],
                           [ 1, 1, 0, 0, 0, 0, 1, 1, 1, 0 ],
                           [ 1, 1, 1, 1, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 2, 2, 2, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 1, 2, 3, 2, 1, 1, 0, 0 ]],

                 'forest':[[ 0, 0, 0, 0, 0, 0, 1, 1, 3, 2 ],
                           [ 0, 0, 0, 0, 0, 0, 1, 1, 3, 2 ],
                           [ 0, 0, 0, 0, 0, 1, 2, 2, 3, 1 ],
                           [ 0, 0, 0, 0, 0, 1, 2, 2, 3, 1 ],
                           [ 0, 0, 0, 0, 0, 1, 1, 0, 0, 1 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 1 ],
                           [ 0, 0, 0, 0, 0, 0, 1, 1, 1, 1 ],
                           [ 0, 0, 0, 0, 0, 1, 1, 1, 2, 1 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 1, 1 ]],

                 'swamp' :[[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 1, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 1, 1, 1, 1, 0, 0, 0, 0 ],
                           [ 0, 0, 1, 1, 1, 1, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 1, 1, 0, 0, 0, 0 ],
                           [ 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 ]],

                 'human' :[[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 1, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]],

                 'wood'  :[[ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0,10, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
                           [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ]]}



  buildingSet = { ( 1, 1):'townhall',
                  ( 1, 2):'woodmill' }

  buildingInfluence = { 'townhall':{},
                  'woodmill':{'wood':+2,
                             'human':-2,
                             'forest':-2} }

  humanSpreadThreshold = 1

  d = {'resources':resources, 'influenceMatrix':influenceMatrix, 'resourceMap':resourceMap, 'humanSpreadThreshold':humanSpreadThreshold}

  w2 = world(resources, influenceMatrix,               buildingInfluence, buildingSet, humanSpreadThreshold, 10, 10)
  w2.setWorld(resources, influenceMatrix, resourceMap, buildingInfluence, buildingSet, humanSpreadThreshold)

  dt = 0.1
  #for t in range(1000):
  #  print t
  #  w2.update(dt)
  #  print w2.toString()
