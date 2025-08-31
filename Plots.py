import sys
import ROOT

# slope cut?

def FillHist(values, hist):
    """
    This function fills a given histogram with values it takes as argument. The list of values can have elements that are lists themselves: in this case, the histogram will be fill with the first object of that list
    
    -----------
    Parameters
    -----------
    
    values: the list or array of values to fill the histogram with
    
    hist: the name of the histogram to fill
    
    """
    for value in values:
        if type(value) != int and len(value) > 1:
            hist.Fill(value[0])
        elif type(value) == int:
            hist.Fill(value)
            
def FillHistResiduals(values, hist, dim = 1):
    """
    This function fills a given histogram with values of track residuals it takes as argument. The histogram can either be 1D (residuals only) or 2D (residuals vs wire distance). 
    
    -----------
    Parameters
    -----------
    
    values: the list or array of values to fill the histogram with
    
    hist: the name of the histogram to fill
    
    dim: the histogram dimension, 1 for 1D or 2 for 2D. Default is 1
    
    """    
    if dim == 1:
        for value in values:
            hist.Fill(value[0][0])
            
    elif dim == 2:
        for value in values:
            hist.Fill(value[0][1], value[0][0])

    else:
        print("Invalid value for residuals histogram dimension. Choose 1 (1D) or 2 (2D, residual vs distance)", file = sys.stderr)        

def PlotHits(n_hits_X, n_hits_Y, run, out_dir):    
    """
    This function plots the distribution of track hits multiplicity as a histogram and saves it in .png format
    
    -----------
    Parameters
    -----------
    
    n_hits_X: a list containing the amount of hits in a MiniDT X track, in a specific event
    
    n_hits_Y: a list containing the amount of hits in a MiniDT Y track, in a specific event
    
    run: the run number for the plot title
    
    out_dir: the directory where the .png will be saved
    
    """
        
    histo_X = ROOT.TH1F("Hits_X", "MiniDT X Track hits multiplicity; # Hits; Occurrences", 2, 2.5, 4.5)
    histo_Y = ROOT.TH1F("Hits_Y", "MiniDT Y Track hits multiplicity; # Hits; Occurrences", 2, 2.5, 4.5)

    FillHist(n_hits_X, histo_X)
    FillHist(n_hits_Y, histo_Y)
    
    max_X = histo_X.GetMaximum()
    max_Y = histo_Y.GetMaximum()

    c = ROOT.TCanvas("c", "c", 1000, 400)
    c.Divide(2, 1)
    c.cd(1)
    histo_X.SetAxisRange(0, 1.5 * max_X, "Y")
    histo_X.Draw()
    c.cd(2)
    histo_Y.SetAxisRange(0, 1.5 * max_Y, "Y")
    histo_Y.Draw()
    c.Draw()

    c.SaveAs(f"{out_dir}/TrackHitsMultiplicity_{run}.png")
    

def PlotSlopes(slope_X, slope_Y, run, out_dir, n_hits = 0):
    """
    This function plots the distribution of track slopes (all tracks, 3-hit and 4-hit tracks) as histograms and saves it in .png format
    
    -----------
    Parameters
    -----------
    
    slope_X: a list containing the slopes of MiniDT X tracks, in each event of the run
    
    slope_Y: a list containing the slopes of MiniDT Y tracks, in each event of the run
    
    run: the run number for the plot title
    
    out_dir: the directory where the .png will be saved
        
    n_hits: int to select plot content, depending on amount of hits in a track (3- or 4-hits tracks). Default (0) is all tracks 
            
    """
    
    if n_hits == 3:
        slope_3hits_X = [slope for slope in slope_X if slope[1] == 3]
        histo_X = ROOT.TH1F("Slope_3hits_X", "MiniDT X Slope (3 hits); Slope; Occurrences", 70, -20, 20)
        FillHist(slope_3hits_X, histo_X)

        slope_3hits_Y = [slope for slope in slope_Y if slope[1] == 3]
        histo_Y = ROOT.TH1F("Slope_3hits_Y", "MiniDT Y Slope (3 hits); Slope; Occurrences", 70, -20, 20)
        FillHist(slope_3hits_Y, histo_Y)
        
        image_title = "3-hit-tracks"
 
    elif n_hits == 4:
        slope_4hits_X = [slope for slope in slope_X if slope[1] == 4]
        histo_X = ROOT.TH1F("Slope_4hits_X", "MiniDT X Slope (4 hits); Slope; Occurrences", 50, -20, 20)
        FillHist(slope_4hits_X, histo_X)

        slope_4hits_Y = [slope for slope in slope_Y if slope[1] == 4]
        histo_Y = ROOT.TH1F("Slope_4hits_Y", "MiniDT Y Slope (4 hits); Slope; Occurrences", 50, -20, 20)
        FillHist(slope_4hits_Y, histo_Y)
    
        image_title = "4-hit-tracks"
    
    elif n_hits == 0:
        histo_X = ROOT.TH1F("Slope_X", "MiniDT X Slope; Slope; Occurrences", 100, -40, 40)
        FillHist(slope_X, histo_X)

        histo_Y = ROOT.TH1F("Slope_Y", "MiniDT Y Slope; Slope; Occurrences", 100, -40, 40)
        FillHist(slope_Y, histo_Y)
        
        image_title = "all-tracks"
        
    else:
        print("Invalid value for hits track multiplicity. Choose 0 (all tracks), 3 (3-hits track) or 4 (4-hits tracks)", file = sys.stderr)
        
    max_X = histo_X.GetMaximum()
    max_Y = histo_Y.GetMaximum()

    c = ROOT.TCanvas("c", "c", 1000, 400)
    c.Divide(2, 1)
    c.cd(1)
    histo_X.SetAxisRange(0, 1.5 * max_X, "Y")
    histo_X.Draw()
    c.cd(2)
    histo_Y.SetAxisRange(0, 1.5 * max_Y, "Y")
    histo_Y.Draw()
    c.Draw()

    c.SaveAs(f"{out_dir}/TrackSlopes_{run}_{image_title}.png")

def PlotXIntercepts(x_intercept_X, x_intercept_Y, run, our_dir, n_hits = 0):
    """
    This function plots the distribution of track intercepts with the chamber's lower edge (all tracks, 3-hit and 4-hit tracks) as histograms and saves it in .png format
    
    -----------
    Parameters
    -----------
    
    x_intercept_X: a list containing the intercepts with the chamber's lower edge of MiniDT X tracks, in each event of the run
    
    x_intercept_Y: a list containing the intercepts with the chamber's lower edge of MiniDT Y tracks, in each event of the run
    
    run: the run number for the plot title
    
    out_dir: the directory where the .png will be saved
    
    n_hits: int to select plot content, depending on amount of hits in a track (3- or 4-hits tracks). Default (0) is all tracks 
            
    """
    
    if n_hits == 3:
        x_intercept_3hits_X = [x_intercept for x_intercept in x_intercept_X if x_intercept[1] == 3]
        histo_X = ROOT.TH1F("XIntercept_3hits_X", "MiniDT X XIntercept (3 hits); XIntercept; Occurrences", 70, 0, 72)
        FillHist(x_intercept_3hits_X, histo_X)

        x_intercept_3hits_Y = [x_intercept for x_intercept in x_intercept_Y if x_intercept[1] == 3]
        histo_Y = ROOT.TH1F("XIntercept_3hits_Y", "MiniDT Y XIntercept (3 hits); XIntercept; Occurrences", 70, 0, 72)
        FillHist(x_intercept_3hits_Y, histo_Y)
        
        image_title = "3-hit-tracks"
 
    elif n_hits == 4:
        x_intercept_4hits_X = [x_intercept for x_intercept in x_intercept_X if x_intercept[1] == 4]
        histo_X = ROOT.TH1F("XIntercept_4hits_X", "MiniDT X XIntercept (4 hits); XIntercept; Occurrences", 50, 0, 72)
        FillHist(x_intercept_4hits_X, histo_X)

        x_intercept_4hits_Y = [x_intercept for x_intercept in x_intercept_Y if x_intercept[1] == 4]
        histo_Y = ROOT.TH1F("XIntercept_4hits_Y", "MiniDT Y XIntercept (4 hits); XIntercept; Occurrences", 50, 0, 72)
        FillHist(x_intercept_4hits_Y, histo_Y)
    
        image_title = "4-hit-tracks"
    
    elif n_hits == 0:
        histo_X = ROOT.TH1F("XIntercept_X", "MiniDT X XIntercept; XIntercept; Occurrences", 100, 0, 72)
        FillHist(x_intercept_X, histo_X)

        histo_Y = ROOT.TH1F("XIntercept_Y", "MiniDT Y XIntercept; XIntercept; Occurrences", 100, 0, 72)
        FillHist(x_intercept_Y, histo_Y)
        
        image_title = "all-tracks"
        
    else:
        print("Invalid value for hits track multiplicity. Choose 0 (all tracks), 3 (3-hits track) or 4 (4-hits tracks)", file = sys.stderr)
        
    max_X = histo_X.GetMaximum()
    max_Y = histo_Y.GetMaximum()

    c = ROOT.TCanvas("c", "c", 1000, 400)
    c.Divide(2, 1)
    c.cd(1)
    histo_X.SetAxisRange(0, 1.5 * max_X, "Y")
    histo_X.Draw()
    c.cd(2)
    histo_Y.SetAxisRange(0, 1.5 * max_Y, "Y")
    histo_Y.Draw()
    c.Draw()

    c.SaveAs(f"{out_dir}/TrackXIntercepts_{run}_{image_title}.png")
    
def PlotChiSquares(chi_square_X, chi_square_Y, run, out_dir, n_hits = 0):
    """
    This function plots the distribution of track chi squares (all tracks, 3-hit and 4-hit tracks) as a histogram and saves it in .png format
    
    -----------
    Parameters
    -----------
    
    chi_square_X: a list containing the chi square of MiniDT X tracks, in a specific event
    
    chi_square_Y: a list containing the chi square of MiniDT Y tracks, in a specific event
    
    run: the run number for the plot title
    
    out_dir: the directory where the .png will be saved
    
    n_hits: int to select plot content, depending on amount of hits in a track (3- or 4-hits tracks). Default (0) is all tracks
    
    """
    
    if n_hits == 3:
        chi_square_3hits_X = [chi_square for chi_square in chi_square_X if chi_square_X[1] == 3]
        histo_X = ROOT.TH1F("ChiSquare_3hits_X", "MiniDT X ChiSquare (3 hits); ChiSquare; Occurrences", 80, 0, 1.5)
        FillHist(chi_square_3hits_X, histo_X)

        chi_square_3hits_Y = [chi_square for chi_square in chi_square_Y if chi_square_Y[1] == 3]
        histo_Y = ROOT.TH1F("ChiSquare_3hits_Y", "MiniDT Y ChiSquare (3 hits); ChiSquare; Occurrences", 80, 0, 1.5)
        FillHist(chi_square_3hits_Y, histo_Y)
        
        image_title = "3-hit-tracks"
 
    elif n_hits == 4:
        chi_square_4hits_X = [chi_square for chi_square in chi_square_X if chi_square_X[1] == 4]
        histo_X = ROOT.TH1F("ChiSquare_4hits_X", "MiniDT X ChiSquare (4 hits); ChiSquare; Occurrences", 80, 0, 1.5)
        FillHist(chi_square_4hits_X, histo_X)

        chi_square_4hits_Y = [chi_square for chi_square in chi_square_Y if chi_square_Y[1] == 4]
        histo_Y = ROOT.TH1F("ChiSquare_4hits_Y", "MiniDT Y ChiSquare (4 hits); ChiSquare; Occurrences", 80, 0, 1.5)
        FillHist(chi_square_4hits_Y, histo_Y)
    
        image_title = "4-hit-tracks"
    
    elif n_hits == 0:
        histo_X = ROOT.TH1F("ChiSquare_X", "MiniDT X ChiSquare; ChiSquare; Occurrences", 80, 0, 1.5)
        FillHist(chi_square_X, histo_X)

        histo_Y = ROOT.TH1F("ChiSquare_Y", "MiniDT Y ChiSquare; ChiSquare; Occurrences", 80, 0, 1.5)
        FillHist(chi_square_Y, histo_Y)
        
        image_title = "all-tracks"
        
    else:
        print("Invalid value for hits track multiplicity. Choose 0 (all tracks), 3 (3-hits track) or 4 (4-hits tracks)", file = sys.stderr)
        
    max_X = histo_X.GetMaximum()
    max_Y = histo_Y.GetMaximum()

    c = ROOT.TCanvas("c", "c", 1000, 400)
    c.Divide(2, 1)
    c.cd(1)
    histo_X.SetAxisRange(0, 1.5 * max_X, "Y")
    histo_X.Draw()
    c.cd(2)
    histo_Y.SetAxisRange(0, 1.5 * max_Y, "Y")
    histo_Y.Draw()
    c.Draw()

    c.SaveAs(f"{out_dir}/TrackChiSquare_{run}_{image_title}.png")
    
def PlotResiduals(residual_X, residual_Y, run, out_dir, n_hits = 0):
    """
    This function plots the distribution of track residuals (all tracks, 3-hit and 4-hit tracks) as a histogram and saves it in .png format
    
    -----------
    Parameters
    -----------
    
    residual_X: a list containing the residual of MiniDT X tracks, in a specific event
    
    residual_Y: a list containing the residual of MiniDT Y tracks, in a specific event
    
    run: the run number for the plot title
    
    out_dir: the directory where the .png will be saved
        
    n_hits: int to select plot content, depending on amount of hits in a track (3- or 4-hits tracks). Default (0) is all tracks
    
    """
    
    if n_hits == 3:
        residual_3hits_X = [residual for residual in residual_X if residual_X[1] == 3]
        histo_X = ROOT.TH1F("Residuals_3hits_X", "MiniDT X Residuals (3 hits); Residual (cm); Occurrences", 150, -0.5, 0.5)
        FillHistResiduals(residual_3hits_X, histo_X)

        residual_3hits_Y = [residual for residual in residual_Y if residual_Y[1] == 3]
        histo_Y = ROOT.TH1F("Residuals_3hits_Y", "MiniDT Y Residuals (3 hits); Residual (cm); Occurrences", 150, -0.5, 0.5)
        FillHistResiduals(residual_3hits_Y, histo_Y)
        
        image_title = "3-hit-tracks"
 
    elif n_hits == 4:
        residual_4hits_X = [residual for residual in residual_X if residual_X[1] == 4]
        histo_X = ROOT.TH1F("Residuals_4hits_X", "MiniDT X Residuals (4 hits); Residual (cm); Occurrences", 150, -0.5, 0.5)
        FillHistResiduals(residual_4hits_X, histo_X)

        residual_4hits_Y = [residual for residual in residual_Y if residual_Y[1] == 4]
        histo_Y = ROOT.TH1F("Residuals_4hits_Y", "MiniDT Y Residuals (4 hits); Residual (cm); Occurrences", 150, -0.5, 0.5)
        FillHistResiduals(residual_4hits_Y, histo_Y)
    
        image_title = "4-hit-tracks"
    
    elif n_hits == 0:
        histo_X = ROOT.TH1F("Residuals_X", "MiniDT X Residuals; Residual (cm); Occurrences", 150, -0.5, 0.5)
        FillHistResiduals(residual_X, histo_X)

        histo_Y = ROOT.TH1F("Residuals_Y", "MiniDT Y Residuals; Residual (cm); Occurrences", 150, -0.5, 0.5)
        FillHistResiduals(residual_Y, histo_Y)
        
        image_title = "all-tracks"
        
    else:
        print("Invalid value for hits track multiplicity. Choose 0 (all tracks), 3 (3-hits track) or 4 (4-hits tracks)", file = sys.stderr)
        
    max_X = histo_X.GetMaximum()
    max_Y = histo_Y.GetMaximum()

    c = ROOT.TCanvas("c", "c", 1000, 400)
    c.Divide(2, 1)
    c.cd(1)
    histo_X.SetAxisRange(0, 1.5 * max_X, "Y")
    histo_X.Draw()
    c.cd(2)
    histo_Y.SetAxisRange(0, 1.5 * max_Y, "Y")
    histo_Y.Draw()
    c.Draw()

    c.SaveAs(f"{out_dir}/TrackResiduals_{run}_{image_title}.png")
    
def PlotResidualsVsDistance(residual_X, residual_Y, run, out_dir):
    """
    This function plots the 2D distribution of track residuals (all tracks, 3-hit and 4-hit tracks) vs the distance from the anode wire of the corresponding hit as a histogram and saves it in .png format
    
    -----------
    Parameters
    -----------
    
    residual_X: a list containing the residual of MiniDT X tracks, in a specific event
    
    residual_Y: a list containing the residual of MiniDT Y tracks, in a specific event
    
    run: the run number for the plot title
    
    out_dir: the directory where the .png will be saved
            
    """
    
    histo_X = ROOT.TH2F("Residuals_Wire_Distance_X", "MiniDT X Residuals; Distance from anode wire (cm); Residual (cm)", 150, 0, 2.1, 150, -0.5, 0.5)
    FillHistResiduals(residual_X, histo_X, 2)

    histo_Y = ROOT.TH2F("Residuals_Wire_Distance_Y", "MiniDT Y Residuals; Distance from anode wire (cm); Residual (cm)", 150, 0, 2.1, 150, -0.5, 0.5)
    FillHistResiduals(residual_Y, histo_Y, 2)
    
    max_X = histo_X.GetMaximum()
    max_Y = histo_Y.GetMaximum()

    c = ROOT.TCanvas("c", "c", 1000, 400)
    c.Divide(2, 1)
    c.cd(1)
    histo_X.Draw()
    c.cd(2)
    histo_Y.Draw()
    c.Draw()

    c.SaveAs(f"{out_dir}/TrackResidualsVsDistance_{run}.png")
    

    
