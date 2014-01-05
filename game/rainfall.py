import math
import random



def generateRainfallMap(altitudeMap):
  vsize = len(altitudeMap)
  hsize = len(altitudeMap[0])
  return [ [random.random()]*hsize for i in range(vsize) ]
