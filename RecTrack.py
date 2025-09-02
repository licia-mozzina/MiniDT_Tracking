from RecHit import RecHit
import numpy as np
import math
import matplotlib.pyplot as plt
import ROOT

CellLength = 4.2 # cm
CellHeight = 1.3 # cm

class RecTrack: 
    """
    --------
    Members
    --------
    
    Hits: the hits associated with the track, loosely selected based on the trigger primitive of reference with the SelectHits() function. 
          After applying the class FitTPLateralities() method, the hits are reduced to the 3 or 4 hits most likely belonging to the 
          reference TP. Necessary to initialize a RecTrack instance
    
    nHits: the number of hits of the track, after the FitTPLateralities() method. It is initiated to 0
    
    TP: the trigger primitive of reference. Necessary to initialize a RecTrack instance
    
    Slope: the track slope (the angular coefficient of y = mx + q, where (0,0) is the chamber's lower left angle), after the 
           FitTPLateralities() method. It is initiated to 0 
    
    Intercept: the track vertical intercept (q in y = mx + q), after the FitTPLateralities() method. It is initiated to 0 
    
    XIntercept: the track horizontal intercept (between the 2nd and the 3rd layers of the MiniDT), after the FitTPLateralities() method. 
                It is initiated to 0 
    
    ChiSquare: the track chi square, after the FitTPLateralities() method. It is initiated to 0 
    
    
    --------
    Methods
    --------
    
    __init__(self, hits, tp): RecTrack initialization. To initialize, a selection of hits and their corresponding trigger primitive are
                              required
    
    FitTPLateralities(self): from the collection of hits associated with the trigger primitive at initialization, it selects the ones most
                             likely belonging to the TP, i.e. they share the same layer and wire values.
                             It retrieves the TP-computed laterality value for each hit, and it fits the resulting positions with the 
                             ROOT framework.
                             The resulting slope, intercept, Xintercept and chi square values are assigned to the RecTrack members
    
    PlotFit(self): this function plots RecTrack (hits and fitted track) after the FitTPLateralities() results, in a cross-section view of
                   the MiniDT
    
    ResidualHitWireDistance(self): this function computes the difference between the measured horizontal hit position and the expected hit
                                   position from the track fitting, for a selection of hits in the whole run. It returns this difference 
                                   and the distance of the hit orizontal position from the corresponding cell's anodic wire
    
    HoughFit(self): this function exploits a Hough Transform (HT) method fit on the hits selected by the FitTPLateralities() method. 
                    For each hit, it computes the function c = x[i] + m * y, where x and y are the hit.Position values (both the left and 
                    right x options are considered), and both m and c are unknown. More precisely, m is the inverse angular coefficient of 
                    the RecTrack and c is the track interception on the lower bound of the cell (i.e. at y = 0). Hits belonging to the same 
                    track will share the same m and c values, therefore the corresponding bin of the 2d histogram of m and c values, the so-
                    called 'Hough accumulator' will be the most populated and will be used to compute the RecTrack values. 
                    The range of values for m and c that will define the histogram bounds are still under optimization. For now, the bins
                    for m values are 20 mrad wide, in the [-60°, +60°] interval circa wrt the normal to the MiniDT layers, 
                    while the bins for c values are 2 mm wide, covering a length of approximately 1 m
                    -----------
                    CAVEAT
                    -----------
                    The chi-square value for this method is not computed, and set to 0 by default.
    
    
    """
    def __init__(self, hits, tp):
        self.Hits = hits
        self.nHits = 0
        self.TP = tp
        self.Slope = 0
        self.Intercept = 0
        self.XIntercept = 0
        self.ChiSquare = 0 
            
    def FitTPLateralities(self): 
        HitsValidLateral_x = []
        HitsValidLateral_y = []
        SelectedHits = []
        
        for layer, hit in enumerate(self.TP['hits']): # the trigger primitive is defined with progressive layers
            wire = hit['wi']  
            if hit['valid'] == 1: # check for hit validity in trigger primitive
                for i, matching_hit in enumerate (self.Hits):
                    if matching_hit.Layer == layer and matching_hit.Wire == wire:
                        self.nHits += 1
                        SelectedHits.append(matching_hit)
                        laterality = hit['lat']
                        matching_hit.SetHitLaterality(laterality)
                        HitsValidLateral_x.append(self.Hits[i].Position[laterality][0])
                        HitsValidLateral_y.append(self.Hits[i].Position[laterality][1])
        
        HitsValidLateral_x = np.array(HitsValidLateral_x)
        HitsValidLateral_y = np.array(HitsValidLateral_y)
        
        self.Hits = SelectedHits
        
        if len(HitsValidLateral_x) != 0 and len(HitsValidLateral_y) != 0:
            HitsGraph = ROOT.TGraph(len(HitsValidLateral_x), HitsValidLateral_x, HitsValidLateral_y)
            FitFunction = ROOT.TF1("FitFunction", "[0]*x + [1]") 
            
            HitsGraph.Fit("FitFunction", "q")

            self.Slope = FitFunction.GetParameter(0) 
            self.Intercept = FitFunction.GetParameter(1)
            self.XIntercept = (2 * CellHeight - FitFunction.GetParameter(1)) / FitFunction.GetParameter(0)
            self.ChiSquare = FitFunction.GetChisquare()
            
    def PlotFit(self): 
        PlotCells = {}
        PlotWires = {}
        PlotHits = {}
        
        WireList = [1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,11,11,11,12,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,16,16,16,16]
        
        LayerList = [4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1]
        
        b = 4.2 
        h = 1.3
        off = [b/2, 0, b/2, 0]
        
        plt.figure(figsize = (12, 10), dpi = 300)
        plt.gca().axes.xaxis.set_ticklabels([])
        plt.gca().yaxis.set_ticklabels([])
        plt.tick_params(bottom = False, left = False) 
        
        for cell in range(0,64):
            mfc = 'w'
            x = b * (WireList[cell] - 1) + off[LayerList[cell] - 1]
            y = h * (LayerList[cell] - 1)
            PlotCells['L' + str(LayerList[cell]) + 'W' + str(WireList[cell])] = plt.Rectangle((x, y), b, h, ec = 'k', fc = mfc)
            PlotWires['L' + str(LayerList[cell]) + 'W' + str(WireList[cell])] = plt.Circle((x + b / 2, y + h / 2),radius = 0.1,fc = 'k')
            
            plt.gca().add_patch(PlotCells['L' + str(LayerList[cell]) + 'W' + str(WireList[cell])])
            plt.gca().add_patch(PlotWires['L' + str(LayerList[cell]) + 'W' + str(WireList[cell])])
            plt.axis('scaled')
        
        for hit in self.Hits:
            mfc = 'powderblue'
            x = b * (hit.Wire) + off[hit.Layer]
            y = h * (hit.Layer) + h / 2
                        
            PlotCells['L' + str(hit.Layer + 1) + 'W' + str(hit.Wire + 1)] = plt.Rectangle((x, y - h / 2), b, h, ec='k', fc=mfc)
            PlotWires['L' + str(hit.Layer + 1) + 'W' + str(hit.Wire + 1)] = plt.Circle((x + b / 2, y), radius = 0.1, fc = 'k')
            plt.gca().add_patch(PlotCells['L' + str(hit.Layer + 1) + 'W' + str(hit.Wire + 1)])
            plt.gca().add_patch(PlotWires['L' + str(hit.Layer + 1) + 'W' + str(hit.Wire + 1)])
                        
            PlotHits['L' + str(hit.Layer + 1) + 'W' + str(hit.Wire + 1)] = plt.Circle((hit.Position[hit.Laterality][0], hit.Position[hit.Laterality][1]),radius = 0.2,fc = 'royalblue')
                              
            plt.gca().add_patch(PlotHits['L' + str(hit.Layer + 1) + 'W' + str(hit.Wire + 1)])
            
            plt.axis('scaled')
                
        plt.axline((0, (self.Intercept)), slope = self.Slope, linewidth = 1, color = 'mediumvioletred')
        plt.show()
        print(f"Slope: {self.Slope}, Intercept: {self.XIntercept} cm, ChiSquare: {self.ChiSquare}")
       
    
    def Residual_Hit_Wire_Distance(self): 
        for hit in self.Hits:
            x = hit.Position[hit.Laterality][0]
            y = hit.Position[hit.Laterality][1]
            x_offset = hit.Wire * CellLength + (0.5 if (hit.Layer % 2 == 1) else 1) * CellLength
            LayerIntercept = (y - self.Intercept) / self.Slope
            if hit.Laterality == 0:
                return(x - LayerIntercept, abs(x - x_offset))
            else:
                return(LayerIntercept - x, abs(x - x_offset))
            
    def HoughFit(self, c_values, m_values):
        accumulator = np.zeros((c_values, m_values))
        dm = 4 / m_values

        m_plot = []
        c_plot = []

        for hit in self.Hits:
            x = [hit.Position[0][0], hit.Position[1][0]]
            y = hit.Position[0][1]

            for m_index in range(m_values):
                for i in range (2):
                    m = m_index * dm - 2    # [0, 4] --> [-2, 2]
                    c = x[i] + m * y
                    accumulator[int(round(c * (c_values / 100)))][m_index] += 1

                    m_plot.append(m)
                    c_plot.append(c)

        accumulator_max = np.argmax(accumulator, axis=None)
        if accumulator_max < 3: 
            m_track = 999
            c_track = 999
        else:
            accumulator_peak = np.unravel_index(np.argmax(accumulator, axis=None), accumulator.shape)
            m_track = accumulator_peak[1] * dm - 2
            c_track = accumulator_peak[0] / (c_values / 100)

        hist, xedges, yedges, image = plt.hist2d(m_plot, c_plot, bins=[1000,1000], range=[[-2, 2],[-20, 80]])
        plt.colorbar()
        plt.show()
        plt.clf()

        HT_track_slope = - 1 / m_track
        HT_track_intercept = - c_track * HT_track_slope 
        
        SelectedHits = []
        for layer in range(4):
            x = (((layer + 0.5) * CellHeight) - HT_track_intercept) / HT_track_slope
            layer_hits = [hit for hit in self.Hits if hit.Layer == layer]
            x_diff_0 = [(abs(x - hit.Position[0][0]) if abs(x - hit.Position[0][0]) < CellLength / 2 else 1000) for hit in layer_hits]
            x_diff_1 = [(abs(x - hit.Position[1][0]) if abs(x - hit.Position[1][0]) < CellLength / 2 else 1000) for hit in layer_hits]

            if (len(x_diff_0) != 0):
                if (min(x_diff_0) < min(x_diff_1)):
                    layer_hits[x_diff_0.index(min(x_diff_0))].Laterality = 0
                    SelectedHits.append(layer_hits[x_diff_0.index(min(x_diff_0))]) 
                else:
                    layer_hits[x_diff_1.index(min(x_diff_1))].Laterality = 1
                    SelectedHits.append(layer_hits[x_diff_1.index(min(x_diff_1))]) 

        self.Hits = SelectedHits
        self.Slope = HT_track_slope 
        self.Intercept = HT_track_intercept
        self.XIntercept = (2 * CellHeight - HT_track_intercept) / HT_track_slope
        self.ChiSquare = 0


        