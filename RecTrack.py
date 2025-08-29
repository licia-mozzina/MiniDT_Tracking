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
          After applying the class FitTPLateralities() method, the hits are reduced to the 3 or 4 hits most likely belonging to the reference TP. Necessary to initialize a RecTrack instance
    
    nHits: the number of hits of the track, after the FitTPLateralities() method. It is initiated to 0
    
    TP: the trigger primitive of reference. Necessary to initialize a RecTrack instance
    
    Slope: the track slope, after the FitTPLateralities() method. It is initiated to 0 
    
    Intercept: the track vertical intercept, after the FitTPLateralities() method. It is initiated to 0 
    
    XIntercept: the track horizontal intercept (between the 2nd and the 3rd layers of the MiniDT), after the FitTPLateralities() method. It is initiated to 0 
    
    ChiSquare: the track chi square, after the FitTPLateralities() method. It is initiated to 0 
    
    
    --------
    Methods
    --------
    
    __init__(self, hits, tp): RecTrack initialization. To initialize, a selection of hits and their corresponding trigger primitive are required
    
    FitTPLateralities(self): from the collection of hits associated with the trigger primitive at initialization, it selects the ones most likely belonging to the TP, i.e. they share the same layer and wire values.
                             It retrieves the TP-computed laterality value for each hit, and it fits the resulting positions with the ROOT framework.
                             The resulting slope, intercept, Xintercept and chi square values are assigned to the RecTrack members.
    
    PlotFit(self): it plots RecTrack (hits and fitted track) after the FitTPLateralities() results, in a cross-section view of the MiniDT.
    
    
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
            
    def PlotFit(self): # it just depends on hits that belong to the RecTrack
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
        
        