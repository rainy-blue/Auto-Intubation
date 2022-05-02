import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d
import time

# arduino upon bootup wait for motor reset commands from rpi 
# arduino wait while loop for rpi command to be sent
def connect():
    pass

# read json file
def resetMotors():
    pass

def minLocator(data, arr_shape, numCheck):
    data_size = arr_shape[0] * arr_shape[1]
    indices = np.arange(data_size)
    temp_list = np.column_stack((data, indices))
    temp_sorted = temp_list[np.argsort(temp_list[:,0])] #sort by 2nd column

    min_temps = temp_sorted[:numCheck,0] ##
    min_indices = temp_sorted[:numCheck,1] # list of min ~ locations with lowest temperatures
    print("min indices=", min_indices) ##
    print("min temps" , min_temps) ##
    
    data_array = np.reshape(data, arr_shape)

    sum_neighbors = convolve2d(data_array, np.ones((3,3), dtype=int),'same') - data_array # convolve with 3x3 matrix to sum neighboring elements
    #print(sum_neighbors)
    #print(sum_neighbors.shape)

    for ix,iy in np.ndindex(sum_neighbors.shape): 
        if ix == 0 or ix == arr_shape[0]-1:
            if iy == 0 or iy == arr_shape[1]-1:
                sum_neighbors[ix,iy] /= 3 
            else:
                sum_neighbors[ix,iy] /= 5
        elif iy == 0 or iy == arr_shape[1]-1:
            sum_neighbors[ix,iy] /= 5
        else:
            sum_neighbors[ix,iy] /= 8
    
    temp = np.reshape(sum_neighbors, data_size) # (192,)
    avg_temps = [temp[int(x)] for x in min_indices] # list of lowest averages
    min_temp, min_idx = min((min_temp, min_idx) for (min_idx, min_temp) in enumerate(avg_temps)) # find min temp and idx

    #print(avg_temps)##
    print(f"Min temp region of {min_temp:0.2f} C recorded at index {int(min_indices[min_idx])}")
    #print("min coord192", min_indices[min_idx])##

    return min_temps[min_idx], int(min_indices[min_idx]) # minimum temp and 12x16 coordinate location

def cvtCoords(index, arr_shape):
    return [index//arr_shape[1], index%arr_shape[1]] # (192,) -> (12,16)

''' Might need to compute variance between the entries to determine if and where to execute motor move'''
# hierarchical cluster next iteration https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/
# https://docs.scipy.org/doc/scipy/reference/cluster.hierarchy.html
def cmdMoveQueue(queue):
    queue.sort()

    diff = [y - x for x, y in zip(*[iter(queue)] * 2)] # avg diff between sequential elemnents
    avg = sum(diff) / len(diff)

    group_queue = [[queue[0]]]  # initial group

    for x in queue[1:]: # group nums whose diff < avg
        if x - group_queue[-1][0] < avg:
            group_queue[-1].append(x)
        else:
            group_queue.append([x])
    #print("First cmdMoveQueue func", group_queue)
    return group_queue

def cmdMoveQueue2(queue):
    queue.sort()

    diff = [queue[i+1]-queue[i] for i in range(len(queue)-1)]
    avg = sum(diff) / len(diff)

    group_queue = [[queue[0]]]

    for x in queue[1:]:
        if x - group_queue[-1][-1] < avg:
            group_queue[-1].append(x)
        else:
            group_queue.append([x])
    #print("Second cmdMoveQueue func", group_queue)
    return group_queue

# Select which coordinate to direct motor movement
def selectMovePriority(move_array):
    max = 0
    select = []
    for arr in move_array:
        if len(arr) > max:
            max = len(arr)
            select = arr 
    return select[len(select)//2]

# conversions, weighting bias closer to middle  
def idx2Motor():
    pass

def updateHMap(plt, ax, heatmap, coords, data, cmd):
    for obj in ax.findobj(match = type(plt.Circle(1,1))):
        obj.remove() #clear circle  
    if cmd == "move":
        circ = plt.Circle((15-coords[1],coords[0]), 1, color ='m', fill = False) # Graphing global minima, note inverting axis
    else: 
        circ = plt.Circle((15-coords[1],coords[0]), 1, color ='r', fill = False) # Graphing global minima, note inverting axis
    ax.add_patch(circ)

    heatmap.set_data(np.fliplr(data)) # flip left to right
    heatmap.set_clim(vmin=np.min(data),vmax=np.max(data)) # set bounds

'''timer fun
tic = time.perf_counter() ##
toc = time.perf_counter()
print(f"Time: {toc - tic:0.4f} seconds")
'''

def main():
        
    mlx_shape = (12,16)

    plt.ion()
    fig,ax = plt.subplots(figsize=(8,5))
    therm1 = ax.imshow(np.zeros(mlx_shape),vmin=0,vmax=60) # start plot with zeros
    cbar = fig.colorbar(therm1) # setup colorbar for temps
    cbar.set_label('Temperature [$^{\circ}$C]',fontsize=10) # colorbar label
    
    line = "30.39,31.32,31.69,30.86,28.98,29.56,31.28,29.08,27.95,29.24,28.66,28.04,28.07,29.51,28.95,28.91,30.05,31.61,32.51,32.23,29.89,29.22,30.48,29.56,29.66,28.64,28.07,28.49,28.89,28.89,28.26,28.84,28.88,29.76,31.46,30.90,29.75,29.26,29.35,29.69,29.76,27.72,28.45,29.79,29.25,27.56,28.73,29.07,27.01,28.57,29.59,28.44,26.16,26.55,26.43,28.59,27.76,27.76,29.61,29.60,27.63,27.62,28.72,28.94,28.05,27.70,27.24,25.16,24.54,24.97,27.93,27.99,27.86,28.67,29.12,28.78,28.17,28.57,29.65,29.62,26.98,24.73,25.16,25.03,24.35,24.39,27.15,27.44,27.05,28.37,29.55,29.89,29.07,29.16,30.64,30.69,24.06,24.13,25.12,25.17,24.32,24.37,25.82,27.33,27.13,27.53,28.70,28.99,28.90,29.12,30.91,30.73,24.30,24.24,25.11,24.91,24.42,24.30,25.20,25.54,26.23,27.51,27.57,28.43,29.46,30.54,29.54,31.53,24.22,24.18,24.75,24.96,24.20,24.52,25.19,25.15,24.45,26.24,28.87,30.64,31.48,30.63,31.47,31.41,24.12,24.16,25.49,24.95,24.35,24.29,24.98,25.09,24.48,25.75,29.70,32.02,30.89,30.57,31.17,31.32,24.12,24.19,25.30,24.93,23.92,24.18,25.40,25.22,24.43,24.47,28.45,30.45,30.62,30.28,31.79,31.70,23.82,24.10,25.11,25.52,24.19,24.45,25.62,25.47,24.55,24.27,25.72,30.94,30.11,30.36,32.06,32.16,"


    df = np.fromstring(line, dtype = float, sep=',') # shape=(192,)
    ##if df.shape != 192 then except error

    min_avg_temp,min_idx = minLocator(df,mlx_shape,numCheck=10)
    coords = cvtCoords(min_idx, mlx_shape)
    #print(cvtCoords(min_idx, mlx_shape))


    #print(cmdMoveQueue2([176,164,  96, 177, 160, 144,  97, 145, 165, 129]))
    '''
    ADD A CHECK TO SEE IF THIS MIN TEMP IS ACTUALLY ~31-33 C??'''
    #### WHILE TRUE HERE

    data_array = np.reshape(df, mlx_shape)
    updateHMap(plt, ax, therm1, coords, data_array, "move")

    ''' BRUTE FORCE MINIMUM, DELETE
    [11,0] is minima, seems to be flipped from displayed plot'''
    # res = np.where(data_array == np.min(data_array))
    # min_idx = list(zip(res[1],res[0]))[0]
    # circ = plt.Circle((15-min_idx[0],min_idx[1]), 1, color ='r', fill = False) # Graphing global minima, note inverting axis
    # ax.add_patch(circ)
                        

    
    #cbar.on_mappable_changed(therm1) # update colorbar range, seems to be patched out
    plt.ioff()
    plt.show()
    #plt.pause(0.001) # required
    # 
    # 

main()