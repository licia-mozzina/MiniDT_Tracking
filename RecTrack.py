from RecHit import RecHit
import numpy as np
import math
import matplotlib.pyplot as plt
import ROOT


CellLength = 4.2 # cm
CellHeight = 1.3 # cm

class RecTrack:
    def __init__(self, hits, tp):
        self.Hits = hits
        self.nHits = 0
        self.TP = tp
        self.Slope = 0
        self.Intercept = 0
        self.XIntercept = 0 # between 2nd and 3rd layer
        self.ChiSquare = 0 
            
    def Fit_TP_lateralities(self): # one station at a time
        HitsValidLateral_x = []
        HitsValidLateral_y = []
        SelectedHits = []
        
        for layer, hit in enumerate(self.TP['hits']): # progressive layers
            wire = hit['wi']  
            if hit['valid'] == 1: # TP quality can be inferred from this
                for i, matching_hit in enumerate (self.Hits): # match con ts forse quasi impossibile, 
                                                              # meglio con wi, ly (si può averne più di una, pace)
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
            
    def Plot_Fit(self): # it just depends on hits that belong to the RecTrack
        PlotCells = {}
        PlotWires = {}
        PlotHits = {}
        
        WireList = [1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,8,9,9,9,9,10,10,10,10,11,11,11,11,12,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,16,16,16,16]
        
        LayerList = [4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1,4,2,3,1]
        
        b=4.2 # da mettere in cm e da prendere da RecHit
        h=1.3
#         off=[0,-b/2,0,-b/2]
        off=[b/2,0,b/2,0]
        
        plt.figure(figsize=(12, 10), dpi=300)
        plt.gca().axes.xaxis.set_ticklabels([])
        plt.gca().yaxis.set_ticklabels([])
        plt.tick_params(bottom = False, left=False) 
        
        for cell in range(0,64):
            mfc = 'w'
            x = b * (WireList[cell] - 1) + off[LayerList[cell] - 1] # + x0
            y = h * (LayerList[cell] - 1) # + y0
            PlotCells['L'+str(LayerList[cell])+'W'+str(WireList[cell])] = plt.Rectangle((x,y),b,h,ec='k',fc=mfc)
            PlotWires['L'+str(LayerList[cell])+'W'+str(WireList[cell])] = plt.Circle((x + b/2, y + h/2),radius=0.1,fc='k')
            
            plt.gca().add_patch(PlotCells['L'+str(LayerList[cell])+'W'+str(WireList[cell])])
            plt.gca().add_patch(PlotWires['L'+str(LayerList[cell])+'W'+str(WireList[cell])])
            plt.axis('scaled')
        
        for hit in self.Hits:
            mfc = 'powderblue'
            x = b * (hit.Wire) + off[hit.Layer] # + x0
            y = h * (hit.Layer) + h / 2 # + y0
                        
            PlotCells['L'+str(hit.Layer + 1)+'W'+str(hit.Wire + 1)] = plt.Rectangle((x, y - h/2),b,h,ec='k',fc=mfc)
            PlotWires['L'+str(hit.Layer + 1)+'W'+str(hit.Wire + 1)] = plt.Circle((x + b/2, y),radius=0.1,fc='k')
            plt.gca().add_patch(PlotCells['L'+str(hit.Layer + 1)+'W'+str(hit.Wire + 1)])
            plt.gca().add_patch(PlotWires['L'+str(hit.Layer + 1)+'W'+str(hit.Wire + 1)])
                        
#             plt.axis('scaled')
                                                
            PlotHits['L'+str(hit.Layer + 1)+'W'+str(hit.Wire + 1)] = plt.Circle((hit.Position[hit.Laterality][0] + 8.25 * CellLength, hit.Position[hit.Laterality][1] + 2 * CellHeight),radius=0.2,fc='royalblue')
                              
            plt.gca().add_patch(PlotHits['L'+str(hit.Layer + 1)+'W'+str(hit.Wire + 1)])
            
            plt.axis('scaled')
                
        plt.axline((8.25 * CellLength, (self.Intercept + 2 * CellHeight)), slope = self.Slope, linewidth=1, color='mediumvioletred')
        plt.show()
        print(f"Slope: {self.Slope}, Intercept: {self.XIntercept} cm, ChiSquare: {self.ChiSquare}")
       
    
    def Residual_Hit_Wire_Distance(self): # solo con 4 hit?
#         result = []
        for hit in self.Hits:
            x = hit.Position[hit.Laterality][0]
            y = hit.Position[hit.Laterality][1]
            x_offset = hit.Wire * CellLength + (0.5 if (hit.Layer % 2 == 1) else 1) * CellLength
            LayerIntercept = (y - self.Intercept) / self.Slope
            if hit.Laterality == 0:
#                 result.append((x - LayerIntercept, abs(x - x_offset))) 
                return(x - LayerIntercept, abs(x - x_offset))
            else:
#                 result.append((LayerIntercept - x, abs(x - x_offset)))
                return(LayerIntercept - x, abs(x - x_offset))
#         return result
        
        