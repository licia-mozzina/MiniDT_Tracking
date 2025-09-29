# **A tracking analyzer for MiniDTs**
This code reconstructs muon tracks from the MiniDTs detectors data. It plots the distributionssw of track quantities (number of hits, slope, intercept, chi-square, residuals) during a run of data taking and saves them in .png format. The code can reconstruct tracks in two ways, either exploiting information from the DAQ system, or with a Hough Transform based method, which is under optimization.
Additionally, this code provides monitoring of hit rates, throughout a run, for each layer or each cell in the MiniDT detectors. 

## Table of Contents
* [The MiniDTs detectors](#the-minidts-detectors)
* [Code Structure](#code-structure)
* [Usage](#usage)
    * [Output](#output)

## The MiniDTs detectors
The MiniDTs are miniature versions of the CMS Drift Tubes, built with spare material of the original detectors at INFN National Laboratories in Legnaro. The basic element of the DT detector is the drift cell. Its transverse size is 42 x 13 mm^2 with a 50 μm diameter gold-plated stainless steel anode wire at the center, and cathode and strip electrodes glued on the cell walls. The gas is an 85:15 mixture of Ar:Co2, which provides a saturated drift velocity of about 54 μm/ns. Four half-staggered layers of parallel cells form a superlayer (SL), which allows for solving single-hit ambiguities in position by providing the measurement of two-dimensional segments.
Each MiniDT is consitued of one superlayer.
The readout is based on the one for the CMS DT Phase-2 Upgrade. For the scope of this project, it is important to highlight the presence of two readout boards for the MiniDTs signals: an On-detector Board for Drift Tube (OBDT) for the time to digital conversion (TDC), and a Xilinx Virtex UltraScale+ FPGA VC118, that, amongst other functions, computes the firmware reconstructed tracks. 

Two MiniDT detectors were installed, in March 2025, in the SND@LHC (Scattering and Neutrino Detector) experiment at CERN, as part of its muon system, to provide high resolution x-y measurements. SND@LHC is a compact and standalone experiment in the LHC tunnel, at 480 m from the ATLAS interaction point. Its signal events are neutrinos coming from IP1 and, possibly, dark sector particles. An improvement in the SND@LHC muon tracking, as the one that MiniDtTs would provide, is essential for a better discrimination between signal and background, _i.e._ muon neutrino interactions and muons that undergo DIS in the material surrounding the detector. 
The MiniDTs are operated with the same high voltage and gas mixture conditions used in CMS.

This code was used during the first stages of commissioning with cosmic rays data, that are provided in `/afs/cern.ch/work/l/lmozzina/public/example_data_cosmic_rays` as an example to test the analyzer with. For those who are not in possess of the credential to access the data, the folder can be downloaded [here](https://cernbox.cern.ch/s/Aw8rWyDHVfV9sgZ) (please make sure to downnload **all** its contents). These data were collected in April 2025, when the MiniDTs were already installed in the LHC tunnel. The Hough Transform based method for track fitting will be used to build MiniDTs standalone track, in order to make MiniDTs data available to the whole SND@LHC collaboration.

### MiniDTs data
The example data are values provided by the MiniDTs readout. The [`doc.txt`](https://cernbox.cern.ch/s/vlnWWajKKYVFcec) file in the data folder contains all the information that is necessary to access them.

The MiniDTs data are divided into two streams: 
- Single hits. For each hit, the following values are provided and can be accessed with the labels in the list:
    * `st`: chamber id (0 == MiniDT X, 1 == MiniDT Y)
    * `ly`: layer number 
    * `wi`: wire number 
    * `bctr`: bunch counter value at the time the hit was produced 
    * `tdc`: fine TDC value, with 0.78 ns resolution 
- Trigger primitives generators (TPG): firmware reconstructed tracks of 3 or 4 hits (low _vs_ high quality TPGs). More documentation on how TPGs are computed can be found [here](https://www.sciencedirect.com/science/article/pii/S0168900223000931?via%3Dihub). These trigger primitives contain the information at chamber level about the muon candidates position, direction, and collision time (_t0_), and are used as input in the L1 CMS trigger. These quantities can be analytically determined from only three hits in different layers belonging to the muon track. There are two separate streams, for MiniDT X and MiniDT Y TPGs, respectively. For each TPG, the following values are provided and can be accessed with the labels in the list:
    * `t0`: the track collision time (its reference time is the start of the LHC orbit, 0.78 ns resolution)
    * `position`: the track intercept in a reference plane
    * `slope`: the track slope 
    * `chi2`: the chi-square of the track
    * `hits`: the list of hits the TPG was built with. The hits contain the layer and wire values, and a time value `ti`, whose origin is the same as the TPG's _t0_. Moreover, two additional fields, `valid` and `lat`, provide information about the hit validity (whether it belong to the track or not) and about the hit laterality (whether the hit is left or right of the anode wire, solved with track fitting), respectively.

Moreover, both streams encode an additional information that is used in this code, to compute when a hit/TPG was produced: 
- `arrival`: it provides the following values, which can be accessed with the labels in the list:
    * `OC` : orbit counter, reset every 40 s, approximately
    * `BX` : bunch crossing number
    
This code does **not** make use of the `position`, `slope` and `chi2` values of TPGs. Instead, it exploits the collision time (t0), and the list of hits belonging to the track with their corresponding 'laterality' to solve the left-right ambiguity, characteristic of the Drift Tube detectors (each hit can be reconstructed either left or right the anode wire).

Even though this code employs both data streams, the goal for MiniDTs standalone tracks will be to completely get rid of the use of TPGs.

The stream objects under the module are list-like. They can be indexed (stream\[3\]), sliced (stream\[3:7\]) or iterated (for datum in stream), and their length queried (len(stream)).
 A simple way to directly access the data is the following. Go to the parent folder, open a python console, then do:
```
## this line imports the whole dump as a module, which has the individual dump data streams
import example_data_cosmic_rays as dump

## this lines show how to access the first item in each data stream. Some may be empty and raise an exception
print(dump.hits[0])
print(dump.tpgs_mb1[0])
print(dump.tpgs_mb2[0])
print(dump.hits[0]['wi'])
print(dump.hits[0]['arrival']['BX'])
print(dump.tpgs_mb1[0]['t0'])

```

## Code Structure
The code is structured as follows:
- [TimestampsTPMatching.py](TimestampsTPMatching.py): the functions that are contained here assign global timestamps to the hit and TPGs stream contained in the raw data and define a way to correctly match the TPGs in the two chambers (possibly a muon that has crossed both detectors) and their corresponding hits. The timestamps assignement takes into account the data congestion in the readout boards that may cause some mess in their ordering.
The time windows for TPGs matching and hits-TPG matching are both user-defined, keeping in mind that they should be narrow enough to ensure a low mismatching rate, but large enough not to be too prohibitive.
- [RecHit.py](RecHit.py): the definition of the reconstructed hit class. To completely reconstruct a hit, three quantities are needed: a time pedestal (in this code, _t0_ from the matched TPG), a drift velocity value (here fixed to 53.5 μm/ns) and the correct laterality (here solved with track fitting). Generally, the correct time pedestal and drift velocity values are calibrated by plotting the 2d track residuals distribution.
- [RecTrack.py](RecTrack.py): the definition of the reconstructed track class. To initialize the track, a list of hits and a TPG of reference are required, that have been previously matched with the [TimestampsTPMatching.py](TimestampsTPMatching.py) functions. The list of hits is then reduced by selecting the ones that actually belong to the TPG.
Two fits options are implemented: with RecTrack.FitTPLateralities(), the left-right ambiguity is solved by the values contained in the TPG; with RecTrack.HoughFit(), the left-right ambiguity is solved with a Hough Transform based method. Further documentation on the Hough Transform method that was chosen can be found [here](https://www.sciencedirect.com/science/article/abs/pii/S0168900216307355?fr=RR-2&ref=pdf_download&rr=977d2df8dea0edc4). The effectiveness of Hough Transform algorithms and their robustness against spurious hits, ambiguities and noise in offline track reconstruction are known features.
- [Plots.py](Plots.py): in here, the functions that plot the number of hits, slopes, intercepts, chi-square and residuals of reconstructed tracks. The residuals 2d plot serves as a probe for the correct time pedestal and drift velocity values choice, as mentioned before. The functions that plot the hit rates, throughout a run, for each layer or each cell in the MiniDT detectors, are contained here as well.
- [TrackFitting.ipynb](TrackFitting.ipynb): a notebook that shows how to use the code.

A more complete and thorough explanation of each file and the functions contained therein can be found in the very same file.

## Usage
This [notebook](TrackFitting.ipynb) shows an example on how to use this code. The timestamping procedure requires some minutes to be complete.
 

### Output 
This code plots the distribution of track quantities (number of hits, slope, intercept, chi-square, residuals) during a run of data taking and saves them in .png format. The ouput directory name is specified by the run name and the time window for TPGs matching. Below, an example of the plots:

**Hits distribution**: the distribution of the number of hits in a track, whose amount can be either 3 or 4.

<img src="https://github.com/licia-mozzina/MiniDT_Tracking/blob/main/Plots_example_data_cosmic_rays_15ns/TrackHitsMultiplicity_example_data_cosmic_rays.png" width="500">

**Slopes distribution**: the distribution of track slopes (the track angular coefficient in the local frame of reference, whose origin is in the chamber lower left angle). Shown here, the values for all tracks, but there are plots contanining only 3-hits or 4-hits tracks as well.

<img src="https://github.com/licia-mozzina/MiniDT_Tracking/blob/main/Plots_example_data_cosmic_rays_15ns/TrackSlopes_example_data_cosmic_rays_all-tracks.png" width="500">

**Intercepts distribution**: the distribution of track intercepts (the track intercept in the lower bound of the chamber, the chamber lower left angle being the origin of the local frame of reference). Shown here, the values for all tracks, but there are plots contanining only 3-hits or 4-hits tracks as well.

<img src="https://github.com/licia-mozzina/MiniDT_Tracking/blob/main/Plots_example_data_cosmic_rays_15ns/TrackXIntercepts_example_data_cosmic_rays_all-tracks.png" width="500">

**Chi-square distribution**: the distribution of the chi-square of tracks. Shown here, the values for all tracks, but there are plots contanining only 3-hits or 4-hits tracks as well.

<img src="http://github.com/licia-mozzina/MiniDT_Tracking/blob/main/Plots_example_data_cosmic_rays_15ns/TrackChiSquare_example_data_cosmic_rays_all-tracks.png" width="500">

**Residuals distribution**: the distribution of track residuals (the difference in position between the expected hit position, from the track fit, and the actual hit position). Shown here, the values for all tracks, but there are plots contanining only 3-hits or 4-hits tracks as well.

<img src="https://github.com/licia-mozzina/MiniDT_Tracking/blob/main/Plots_example_data_cosmic_rays_15ns/TrackResiduals_example_data_cosmic_rays_all-tracks.png" width="500">

**Residuals vs distance from anode wire distribution**: the distribution of track residuals (the difference in position between the expected hit position, from the track fit, and the actual hit position) versus the distance from the anode wire. To completely reconstruct a hit, three quantities are needed: a time pedestal, a drift velocity value and the correct laterality. Generally, the correct time pedestal and drift velocity values are calibrated by plotting the 2d track residuals distribution.

<img src="https://github.com/licia-mozzina/MiniDT_Tracking/blob/main/Plots_example_data_cosmic_rays_15ns/TrackResidualsVsDistance_example_data_cosmic_rays.png" width="500">

Moreover, it is possible to inspect  hit rates, throughout a run, for each layer or each cell in the MiniDT detectors. 

**Hit rates per layer**

<img src="https://github.com/licia-mozzina/MiniDT_Tracking/blob/main/Plots_example_data_cosmic_rays_15ns/LayersRate_example_data_cosmic_rays.png" width="500">

**Hit rates per channel**

<img src="https://github.com/licia-mozzina/MiniDT_Tracking/blob/main/Plots_example_data_cosmic_rays_15ns/CellsRate_example_data_cosmic_rays.png" width="500">

Finally, the user can display, for each event, the reconstructed track and its selected hits in a cross-section view of the chamber. If the Hough Transform fit option is chosen, the so-called _Hough accumulator_ is depicted as well. 

**Event display**

<img src="https://github.com/licia-mozzina/MiniDT_Tracking/blob/main/Plots_example_data_cosmic_rays_15ns/event_display.png" width="500">

**Hough accumulator**: the Hough Transform method computes, for each hit, the function c = x[i] + m * y, where x and y are the hit position 
                    values (both the left and right x options are considered), and both m and c are unknown. More precisely, m is the inverse angular coefficient of 
                    the RecTrack and c is the track interception on the lower bound of the cell (i.e. at y = 0). Hits belonging to the same 
                    track will share the same m and c values, therefore the corresponding bin of the 2d histogram of m (horizontal) and c (vertical) values, the so-
                    called 'Hough accumulator' will be the most populated and will be used to compute the RecTrack values. 

<img src="https://github.com/licia-mozzina/MiniDT_Tracking/blob/main/Plots_example_data_cosmic_rays_15ns/Hough_accumulator.png" width="500">

All example plots can be found in [here](Plots_example_data_cosmic_rays_15ns).

