# from glob import glob
import numpy as np
import matplotlib.pyplot as plt

def PlotLayerRates(hits, run, out_dir):
    """
    This function plots the hits rate in each layer of both MiniDT X and MiniDT Y, and saves it in .png format. Each point is averaged over the LHC orbit duration. The function requires hits that have already been assigned global timestamps.
    
    -----------
    Parameters
    -----------
    
    hist: the run hits collection
    
    run: the run number for the plot title
    
    out_dir: the directory where the .png will be saved
    
    """   
    binsize = 10 # binning in seconds
    rate_x = []
    rate_y = []
    time = []

    rate_step = np.array([[0,0,0,0], [0,0,0,0]])
    time_step = 524288 * 1e-6 * 3564 / 40.0789
    this_step = 0

    orbit_max_counter = 0

    for j, h in enumerate(hits):
        ts, st, ly = h['timestamp'], h['st'], h['ly']
        if h['timestamp'] > this_step + time_step:
            rate_x.append(rate_step[0] / time_step)
            rate_y.append(rate_step[1] / time_step)
            time.append(this_step)
            rate_step = np.array([[0,0,0,0], [0,0,0,0]])
            this_step += time_step
        else:
            rate_step[st][ly] += 1

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    plt.rc('font', family='serif')
    plt.rc('image', cmap='viridis')
    plt.suptitle(f"{run}_corr", fontsize=13)
    titles = ["MiniDT X ", "MiniDT Y"]

    labels = ['L1', 'L2', 'L3', 'L4']

    axes[0].plot(time[1:], rate_x[1:], label = labels) # first one may start at high OC number, fake small rate
    axes[1].plot(time[1:], rate_y[1:], label = labels)
    for i in range(2):
        plt.rc('font', family='serif')
        plt.rc('image', cmap='viridis')
        axes[i].set_xlabel('Time (s)')
        axes[i].set_ylabel('Rate (Hz)')
        axes[i].set_title(titles[i])
        axes[i].legend()

    plt.tight_layout()
    plt.show()
    fig.savefig(f"{out_dir}/LayersRate_{run}.png", dpi=300, bbox_inches='tight')
    
    
def PlotCellRates(hits, run, out_dir):
    """
    This function plots the hits rate in each cell of both MiniDT X and MiniDT Y, averaged over the interval between the first and last hit timestamps, and saves it in .png format. The function requires hits that have already been assigned global timestamps.
    
    -----------
    Parameters
    -----------
    
    hist: the run hits collection
    
    run: the run number for the plot title
    
    out_dir: the directory where the .png will be saved
    
    """
    start_time = hits[0]['timestamp']
    stop_time = hits[-1]['timestamp']

    histo = np.array([[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]],
        [[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]]])
    
    for j, h in enumerate(hits):
        st, ly, wi = h['st'], h['ly'], h['wi']
        histo[st][ly][wi] += 1

    histo_rate = histo / (stop_time - start_time)

    fig, axes = plt.subplots(1, 2, figsize = (12, 5))
    plt.suptitle(f"{run}", fontsize = 13)
    titles = ["MiniDT X ", "MiniDT Y"]

    for i in range(2): 
        ax = axes[i]
        img = ax.imshow(histo_rate[i], cmap = 'viridis', aspect = 'auto', origin = 'lower')  
        ax.set_xlabel('Channels')
        ax.set_ylabel('Layers')
        ax.set_title(titles[i])
        fig.colorbar(img, ax = ax, label = 'Rate')  

    plt.tight_layout()
    plt.show()
    fig.savefig(f"{out_dir}/CellsRate_{run}.png", dpi = 300, bbox_inches = 'tight')
