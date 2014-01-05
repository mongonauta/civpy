import math
import random


  
def calcAltitude(mean, amplitude):
  return random.gauss(mean, amplitude)
  
  
  
# recursively generates a random, fractalized, normalized altitude map given horizontal, vertical coordinates 
# (in mathematical terms: the mapping {0,..,hsize} x {0,..,vsize} -> [0,1])
# algorithm based loosely on Mandelbrot
def generateAltitudeMap(vsize, hsize):
  
  nodeDict = {}
  
  # determine how many iterations, based on given map sizes
  iterations = math.log(min(vsize, hsize), 2)
  if iterations > math.floor(iterations):
    iterations = math.floor(iterations) + 1
  iterations = int(iterations)
  
  n = 2**iterations
  
  # seed values
  nodeDict[(0,0)] = calcAltitude(0, n)
  nodeDict[(0,n)] = calcAltitude(0, n)
  nodeDict[(n,0)] = calcAltitude(0, n)
  nodeDict[(n,n)] = calcAltitude(0, n)
  
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
        nodeDict[top]    = calcAltitude((a00+a01)/2,s)
        nodeDict[bottom] = calcAltitude((a10+a11)/2,s)
        nodeDict[left]   = calcAltitude((a00+a10)/2,s)
        nodeDict[right]  = calcAltitude((a01+a11)/2,s)
        nodeDict[middle] = calcAltitude((a00+a01+a10+a11)/4,s)
      
  minAlt = min(nodeDict.values())
  maxAlt = max(nodeDict.values())
  norm = max(1.0e-6, maxAlt - minAlt)
  
  altitude = [[0]*hsize for i in range(vsize)]
  relief = [[0]*hsize for i in range(vsize)]
  
  # normalize altitudes and return map as 2 dimensional list.
  # also return relief map which is a 
  # NOTE: if vsize, hsize are not square, and not a power of 2, returned map will be clipped     
  for i in range(vsize):
    for j in range(hsize):
    
      # calculate average altitude of tile (in between 4 corner nodes)
      avg = ( nodeDict[(i,j)] + nodeDict[(i,j+1)] + nodeDict[(i+1,j)] + nodeDict[(i+1,j+1)] ) / 4
      
      altitude[i][j] = (avg - minAlt) / norm
      
      # calculate relief as difference between highest and lowest point
      relief[i][j] = ( max( nodeDict[(i,j)], nodeDict[(i,j+1)], nodeDict[(i+1,j)], nodeDict[(i+1,j+1)] ) - \
                       min( nodeDict[(i,j)], nodeDict[(i,j+1)], nodeDict[(i+1,j)], nodeDict[(i+1,j+1)] ) ) / norm
                     
  return altitude, relief 
        
if __name__ == "__main__":

  altitudeMap, reliefMap  = generateAltitudeMap(4,4)  
  print altitudeMap, reliefMap
