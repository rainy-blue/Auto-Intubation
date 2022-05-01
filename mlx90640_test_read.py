'''
Vcc 1
SDA 3
SCL 5
GND 6
RPi to Mega2560 via Serial
'''
import serial
import matplotlib.pyplot as plt
import numpy as np
import time
import board,busio
import adafruit_mlx90640
import tkinter as tk
import sys


# I2C
i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) # 400kbits/s recommended baudrate, max 1Mbits (overheat)
mlx = adafruit_mlx90640.MLX90640(i2c) # 0x33 address
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_8_HZ # DO NOT GO ABOVE 16HZ, if "too many retries" exception then lower
    
mlx_shape = (24,32)

    
def update_plot():
    print("test")
def close():
    root.destroy()
    sys.exit(0)
def check_battery():
    pass

if __name__ == '__main__':
    
    
    #root = tk.Tk()
    #plot_btn = tk.Button(root, command = update_plot, height=2, width=10, text= "Test")
    #plot_btn.pack()
    
    #exit2 = tk.Button(root,command = close, height =2, width = 12, text = "close")
    #.pack()
    
    #root.mainloop()
    # setup the figure for plotting
    plt.ion() # enables interactive plotting
    fig,ax = plt.subplots(figsize=(8,5))
    therm1 = ax.imshow(np.zeros(mlx_shape),vmin=0,vmax=60) #start plot with zeros
    cbar = fig.colorbar(therm1) # setup colorbar for temps
    cbar.set_label('Temperature [$^{\circ}$C]',fontsize=10) # colorbar label
    
    

    frame = np.zeros((24*32,)) # setup array for storing all 768 temperatures
    
    t_array = []
    while True:
        t1 = time.monotonic()
        try:
            Ta, Vdd = mlx.getFrame(frame) # read MLX temperatures into frame var
            print(Ta, Vdd)
            #print(mlx._GetTa(frame))
            data_array = (np.reshape(frame,mlx_shape)) # reshape to 24x32
            therm1.set_data(np.fliplr(data_array)) # flip left to right
            therm1.set_clim(vmin=np.min(data_array),vmax=np.max(data_array)) # set bounds
            #cbar.on_mappable_changed(therm1) # update colorbar range
            plt.pause(0.001) # required
            #fig.savefig('mlx90640_test_fliplr.png',dpi=300,facecolor='#FCFCFC',
                        #bbox_inches='tight') # comment out to speed up
            t_array.append(time.monotonic()-t1)
            print('Sample Rate: {0:2.1f}fps'.format(len(t_array)/np.sum(t_array)))
        except ValueError:
            continue # if error, just read again


# ambient sensor, if > body temp then switch to hot reading vs cold reading mode 