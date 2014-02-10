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

    
  def __init__( self, d ): # resources, influenceMatrix, buildingDef, buildingSet, humanSpreadThreshold, vsize, hsize 

    # age of world
    self.age = 0
    
    # a list with resource names
    self.resources = d['resources']

    self.waterLevel = d['waterLevel']
    
    # a dictionary ("sparse matrix") containing resource dependencies
    self.influenceMatrix = d['influenceMatrix']

    # a dictionary with building definitions
    self.buildingDef = d['buildingDef']
    
    # a dictionary with building locations
    self.buildingSet = d['buildingSet']
    
    self.humanSpreadThreshold = d['humanSpreadThreshold']
    
    # map size parameters
    self.vsize = d['vsize']
    self.hsize = d['hsize']

    self.seedPopulation = d['seedPopulation']
    
    # range of influence
    self.rng = 1

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
   
        # determine 'calculability' (i.e. indicates if we should bother calculating on this tile)
        # TODO: make this work!!!!
        calculability = True #self.determineCalculability(v, h)
        
        # only do something if people are present on the tile (or if tile is near populated tile)
        #if resourceMap['calculable'][v][h] > 0:
        if calculability == True:
        
          # list of resources affected by building
          s1 = {k:0 for k in self.resources}
          
          # buildings reduce growth in return for resources. 
          # canUseBuilding is True when there are enough resources for the building to operate
          canUseBuilding = True
          
          # check if there's a building on the current tile
          if (v, h) in self.buildingSet:
          
            bdg = self.buildingSet[(v, h)]
            
            # loop through resources used by building
            for m in self.buildingDef[bdg]:
              # for each resource affected by building, substract
              amountToAdd = self.buildingDef[bdg][m]
              s1[m] = self.resourceMap[m][v][h] + amountToAdd
              if s1[m] < 0:
                canUseBuilding = False
                   
          # calculate base growth 
          # s2: list of resources on tile
          s2 = {k:self.resourceMap[k][v][h] for k in self.resources}
          growth = self.calcGrowthrate(s2)

          for k in self.resources:
            if self.resourceMap[k][v][h] > 0:
              # we can only grow resources if they are already there ("seeds") 
              if canUseBuilding == True:
                bdgChange = s1[k]
              else:
                bdgChange = 0

              newMap[k][v][h] = max(0, self.resourceMap[k][v][h] + dt * (growth[k] + bdgChange))
            
            # probably expand statement below to handle any kind of resource, instead of just humans
            elif k == 'human':
              # humans cannot spread to this tile unless there's enough humans in surrounding area
              s = self.getSurroundings(v, h, self.rng)
              if self.humanSpreadThreshold <= s[k]:
                newMap[k][v][h] = max(0, self.resourceMap[k][v][h] + dt * growth[k] + bdgChange)
                #print v, h, s[k]

    # determine where change has taken place, important for rendering map
    self.changeMap = self.determineChange(self.resourceMap, newMap)

    # add delta to resource map
    self.resourceMap = newMap


  # calculate growth rate of a set of different resources (compounded over an area)
  def calcGrowthrate( self, s ):

    result = {k:0 for k in self.resources}

    for k in self.resources:
      if k in self.influenceMatrix:
        for m in self.influenceMatrix[k]:
          result[k] = result[k] + self.influenceMatrix[k][m] * s[m]

    return result



  # returns a list of resources compounded over an area (tile v, h plus surroundings)
  def getSurroundings(self, v, h, e):

    # create dictionary with resources 
    result = {k:0 for k in self.resources}
    
    # sum resources over an area
    for k in self.resources:
      for vv in range(max(0, v-e), min(self.vsize, v+e+1)):
        for hh in range(max(0, h-e), min(self.hsize, h+e+1)):
          result[k] = result[k] + self.resourceMap[k][vv][hh]

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
  def setWorld(self, resources, influenceMatrix, resourceMap, buildingDef, buildingSet, humanSpreadThreshold ):
    self.resources = resources
    self.influenceMatrix = influenceMatrix
    self.resourceMap = resourceMap
    self.buildingDef = buildingDef
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

  buildingDef = { 'townhall':{},
                  'woodmill':{'wood':+2,
                             'human':-2,
                             'forest':-2} }
  
  humanSpreadThreshold = 1

  d = {'resources':resources, 'influenceMatrix':influenceMatrix, 'resourceMap':resourceMap, 'humanSpreadThreshold':humanSpreadThreshold}

  w2 = world(resources, influenceMatrix,               buildingDef, buildingSet, humanSpreadThreshold, 10, 10)
  w2.setWorld(resources, influenceMatrix, resourceMap, buildingDef, buildingSet, humanSpreadThreshold)

  dt = 0.1
  #for t in range(1000):
  #  print t
  #  w2.update(dt)
  #  print w2.toString()
