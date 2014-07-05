import math
import random



def rndAltitude(mean, amplitude):
  return random.gauss(mean, amplitude)

def normalizeAltitude(hsize, vsize, nodeDict, minAlt, norm):
  result = [ [0]*hsize for i in range(vsize) ]

  for i in range(vsize):
    for j in range(hsize):
      avg = ( nodeDict[(i,j)] + nodeDict[(i,j+1)] + nodeDict[(i+1,j)] + nodeDict[(i+1,j+1)] ) / 4
      result[i][j] = (avg - minAlt) / norm

  return result

def calcRelief(hsize, vsize, nodeDict, norm):
  result = [ [0]*hsize for i in range(vsize) ]

  for i in range(vsize):
    for j in range(hsize):

      result[i][j] = ( max( nodeDict[(i,j)], nodeDict[(i,j+1)], nodeDict[(i+1,j)], nodeDict[(i+1,j+1)] ) - \
                       min( nodeDict[(i,j)], nodeDict[(i,j+1)], nodeDict[(i+1,j)], nodeDict[(i+1,j+1)] ) ) / norm

  return result

def calcShadow(hsize, vsize, nodeDict):
  result = [ [0]*hsize for i in range(vsize) ]

  for i in range(vsize):
    for j in range(hsize):
      result[i][j] = nodeDict[(i,j)] - nodeDict[(i+1,j+1)]

  return result

def calcIterations(vsize, hsize):
  # determine how many iterations, based on given map sizes
  iterations = math.log(min(vsize, hsize), 2)

  if iterations > math.floor(iterations):
    iterations = math.floor(iterations) + 1

  return int(iterations)

def calcRandomNodes(vsize, hsize):
  nodeDict = {}

  iterations = calcIterations(vsize, hsize)

  n = 2**iterations

  # seed values
  nodeDict[(0,0)] = rndAltitude(0, n)
  nodeDict[(0,n)] = rndAltitude(0, n)
  nodeDict[(n,0)] = rndAltitude(0, n)
  nodeDict[(n,n)] = rndAltitude(0, n)

  # recursively fill in map, starting with outer edges, working inwards
  for i in range(iterations):
    for j in range(2**i):
      for k in range(2**i):

        # step size (declines as i increases)
        s = 2**(iterations-i)

        jj = j*s
        kk = k*s

        # calculate coordinates of in between nodes
        top    = (jj,       kk + s/2)
        bottom = (jj + s,   kk + s/2)
        left   = (jj + s/2, kk      )
        right  = (jj + s/2, kk + s  )
        middle = (jj + s/2, kk + s/2)

        # get altitudes of corner nodes
        a00 = nodeDict[(jj  ,kk  )]
        a01 = nodeDict[(jj  ,kk+s)]
        a10 = nodeDict[(jj+s,kk  )]
        a11 = nodeDict[(jj+s,kk+s)]

        # given corner nodes, calculate altitudes of in between nodes
        nodeDict[top]    = rndAltitude((a00+a01)/2,s)
        nodeDict[bottom] = rndAltitude((a10+a11)/2,s)
        nodeDict[left]   = rndAltitude((a00+a10)/2,s)
        nodeDict[right]  = rndAltitude((a01+a11)/2,s)
        nodeDict[middle] = rndAltitude((a00+a01+a10+a11)/4,s)

  minAlt = min(nodeDict.values())
  maxAlt = max(nodeDict.values())
  norm = max(1.0e-6, maxAlt - minAlt)

  return nodeDict, minAlt, maxAlt, norm

# recursively generates a random, fractalized, normalized altitude map given horizontal, vertical coordinates
# (in mathematical terms: the mapping {0,..,hsize} x {0,..,vsize} -> [0,1])
# algorithm based loosely on Mandelbrot
def generateAltitudeMap(vsize, hsize, test):

  if test == False:
    nodeDict, minAlt, maxAlt, norm = calcRandomNodes(vsize, hsize)

  else:
    nodeDict, minAlt, maxAlt, norm = calcTestNodes(vsize, hsize)

  altitude = normalizeAltitude(hsize, vsize, nodeDict, minAlt, norm)
  relief   = calcRelief(hsize, vsize, nodeDict, norm)
  shadow   = calcShadow(hsize, vsize, nodeDict)

  return altitude, relief, shadow

def calcTestNodes(vsize, hsize):
  nodeDict = {}

  for i in range(vsize+1):
    for j in range(hsize+1):
      y = (1.0*i/vsize - 0.5) * 4 * math.pi
      x = (1.0*j/hsize - 0.5) * 4 * math.pi

      nodeDict[(i,j)] = 0.5 + 0.5 * math.cos(math.sqrt(x**2 + y**2))

  minAlt = min(nodeDict.values())
  maxAlt = max(nodeDict.values())
  norm = max(1.0e-6, maxAlt - minAlt)

  return nodeDict, minAlt, maxAlt, norm

if __name__ == "__main__":

  altitudeMap, reliefMap, shadowMap  = generateAltitudeMap(16,16, False)

  altitudeMap, reliefMap, shadowMap  = generateAltitudeMap(64, 64, True)
