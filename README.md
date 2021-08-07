# PSD lockdown

Power spectral density (PSD) is a common methodology to measure the energy of waves. This project focuses on the calculation of PSD of seismic waves in order to measure the impact of culture noise during the COVID-19 pandemic according to "*Global quieting of high-frequency seismic noise due to COVID-19 pandemic lockdown measures*" from Lecocq et al. (2020). 

Inputs to the project includes daily miniseed waveform file, instrument response file, station list, and duration of the project, which can be downloaded easily via various sites. In this project, GDMS database from the Central Weather Bureau (CWB) was used to measure the impact of soft lockdown measures starting from the mid-May.

The outputs include a CSV file including all PSD values and a daily average along with the corresponding `matplotlib` datetime values and a PNG file plottet using matplotlib.pyplot.
