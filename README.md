# **A tracking analyzer for MiniDTs**
This code reconstructs muon tracks from the MiniDTs detectors data. It plots the distributionssw of track quantities (number of hits, slope, intercept, chi-square, residuals) during a run of data taking and saves them in .png format. The code can reconstruct tracks in two ways, either exploiting information from the DAQ system, or with a Hough Transform based method, which is under optimization.
Additionally, this code provides monitoring of hit rates, throughout a run, for each layer or each cell in the MiniDT detectors. 

## Table of Contents
* [The MiniDTs detectors](#the-minidts-detectors)
* [Code Structure](#structure)
* [Usage](#usage)

## The MiniDTs detectors
The MiniDTs are miniature versions of the CMS Drift Tubes, built with spare material of the original detectors at INFN National Laboratories in Legnaro. The basic element of the DT detector is the drift cell. Its transverse size is 42 x 13 mm^2 with a 50 μm diameter gold-plated stainless steel anode wire at the center, and cathode and strip electrodes glued on the cell walls. The gas is an 85:15 mixture of Ar:Co2, which provides a saturated drift velocity of about 54 μm/ns. Four half-staggered layers of parallel cells form a superlayer (SL), which allows for solving single-hit ambiguities in position by providing the measurement of two-dimensional segments.
Each MiniDT is consitued of one superlayer.
The readout is based on the one for the CMS DT Phase-2 Upgrade. For the scope of this project, it is important to highlight the presence of two readout boards for the MiniDTs signals: an On-detector Board for Drift Tube (OBDT) for the time to digital conversion (TDC), and a Xilinx Virtex UltraScale+ FPGA VC118, that, amongst other functions, computes the firmware reconstructed tracks. 

Two MiniDT detectors were installed, in March 2025, in the SND@LHC (Scattering and Neutrino Detector) experiment at CERN, as part of its muon system, to provide high resolution x-y measurements. SND@LHC is a compact and standalone experiment in the LHC tunnel, at 480 m from the ATLAS interaction point. Its signal events are neutrinos coming from IP1 and, possibly, dark sector particles. An improvement in the SND@LHC muon tracking, as the one that MiniDtTs would provide, is essential for a better discrimination between signal and background, _i.e._ muon neutrino interactions and muons that undergo DIS in the material surrounding the detector. 
The MiniDTs are operated with the same high voltage and gas mixture conditions used in CMS.

This code was used during the first stages of commissioning with cosmic rays data, that are provided in `/afs/cern.ch/work/l/lmozzina/public/example_data_cosmic_rays` as an example to test the analyzer with. These data were collected in April 2025, when the MiniDTs were already installed in the LHC tunnel. The Hough Transform based method for track fitting will be used to build MiniDTs standalone track, in order to make MiniDTs data available to the whole SND@LHC collaboration.

### MiniDTs data
The example data are values provided by the MiniDTs readout. The `doc.txt` file in the data folder contains all the information that is necessary to access them.

The MiniDTs data are divided into two streams: 
- Single hits
- Trigger primitives generators (TPG): firmware reconstructed tracks of 3 or 4 hits (low _vs_ high quality TPGs). More documentation on how TPGs are computed can be found [here](https://www.sciencedirect.com/science/article/pii/S0168900223000931?via%3Dihub).

For each hit, the readout provides the values for the station, layer and cell (wire) it was collected in; the orbit counter (OC), the bunch crossing counter (BX) values at the time the board collected the hits; finally, a finer TDC value that allows a time resolution of 0.78 ns. 

For each TPG, this code makes use of the readout of the collision time (t0), and the list of hits belonging to the track with their corresponding 'laterality' to solve the left-right ambiguity.

Even though this code exploits both streams, the goal for MiniDTs standalone tracks will be to completely get rid of the use of TPGs.

## Code Structure
The code is structured as follows:
- [TimestampsTPMatching.py](TimestampsTPMatching.py): the functions that are contained here assign global timestamps to the hit and TPGs stream contained in the raw data and define a way to correctly match the TPGs in the two chambers (possibly a muon that has crossed both detectors) and their corresponding hits. The timestamps assignement takes into account the data congestion in the readout boards that may cause some mess in their ordering.
The time windows for TPGs matching and hits-TPG matching are both user-defined, keeping in mind that they should be narrow enough to ensure a low mismatching rate, but large enough not to be too prohibitive.
- [RecHit.py](RecHit.py): the definition of the reconstructed hit class. To completely reconstruct a hit, three quantities are needed: a time pedestal (in this code, t0 from the matched TPG), a drift velocity value (here fixed to 53.5 μm/ns) and the correct laterality (here solved with track fitting). Generally, the correct time pedestal and drift velocity values are calibrated by plotting the 2d track residuals distribution.
- [RecTrack.py](RecTrack.py): the definition of the reconstructed track class. To initialize the track, a list of hits and a TPG of reference are required, that have been previously matched with the [TimestampsTPMatching.py](TimestampsTPMatching.py) functions. The list of hits is then reduced by selecting the ones that actually belong to the TPG.
Two fits options are implemented: with RecTrack.FitTPLateralities(), the left-right ambiguity is solved by the values contained in the TPG; with RecTrack.HoughFit(), the left-right ambiguity is solved with a Hough Transform based method. Further documentation on the Hough Transform method that was chosen can be found [here](https://www.sciencedirect.com/science/article/abs/pii/S0168900216307355?fr=RR-2&ref=pdf_download&rr=977d2df8dea0edc4).
- [Plots.py](Plots.py): in here, the functions that plot the number of hits, slopes, intercepts, chi-square and residuals of reconstructed tracks. The residuals 2d plot serves as a probe for the correct time pedestal and drift velocity values choice, as mentioned before.
- [Rates.py](Rates.py): in here, the functions that plot the hit rates, throughout a run, for each layer or each cell in the MiniDT detectors.
- [TrackFitting.ipynb](TrackFitting.ipynb): a notebook that shows how to use the code.

A more complete and thorough explanation of each file and the functions contained therein can be found in the very same file.

## Usage
This [notebook](TrackFitting.ipynb) shows an example on how to use this code. The timestamping procedure requires some minutes to be complete.
 

### Output 
This code plots the distribution of track quantities (number of hits, slope, intercept, chi-square, residuals) during a run of data taking and saves them in .png format. The ouput directory name is specified by the run name and the time window for TPGs matching. 

Moreover, it is possible to inspect  hit rates, throughout a run, for each layer or each cell in the MiniDT detectors. 

Finally, the user can display, for each event, the reconstructed track and its selected hits in a cross-section view of the chamber. If the Hough Transform fit option is chosen, the so-called _Hough accumulator_ is depicted as well. 

Example plots can be found in [here](Plots_example_data_cosmic_rays_15ns).

Below, an example of the reconstructed track and of the _Hough accumulator_.

**Event display**

<img src="https://github.com/licia-mozzina/MiniDT_Tracking/blob/main/Plots_example_data_cosmic_rays_15ns/event_display.png" width="500">

**Hough accumulator**

<img src="https://github.com/licia-mozzina/MiniDT_Tracking/blob/main/Plots_example_data_cosmic_rays_15ns/Hough_accumulator.png" width="500">


