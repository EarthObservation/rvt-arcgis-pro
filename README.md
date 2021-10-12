# Relief Visualization Toolbox ArcGIS Pro Python Raster Functions 

Relief Visualization Toolbox was produced to help scientist visualize raster elevation model datasets. We have narrowed down the selection to include techniques that have proven to be effective for identification of small scale features. Default settings therefore assume working with high resolution digital elevation models, derived from airborne laser scanning missions (lidar).

## Installation

For ArcGIS Pro use, copy whole repository folder (_rvt-arcgis-pro_) to:
```
<ArcGIS Pro install path>/Resources/Raster/Functions/Custom
```
Usually the path is: c:\Program Files\ArcGIS\Pro\Resources\Raster\Functions\Custom\
For Server use, copy the whole repository folder (_rvt-arcgis-pro_) to every federated Server machine of your enterprise Setup:
```
<ArcGIS Server install path> /framework/runtime/ArcGIS/Resources/Raster/Functions/Custom
```

Run/restart ArcGIS Pro. Open pane Raster functions:
```
Imagery > Raster functions
```
Under _Raster functions_ pane you will have tab _Custom_ where will be _rvt-arcgis-pro_ directory with RVT raster functions.

## Documentation

Documentation of the package and its usage is available at [Relief Visualization Toolbox in Python documentation](https://rvt-py.readthedocs.io/).

## References

When using the tools, please cite:

*   Kokalj, Ž., Somrak, M. 2019. Why Not a Single Image? Combining Visualizations to Facilitate Fieldwork and On-Screen Mapping. Remote Sensing 11(7): 747.
*   Zakšek, K., Oštir, K., Kokalj, Ž. 2011. Sky-View Factor as a Relief Visualization Technique. Remote Sensing 3: 398-415.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please report any bugs and suggestions for improvements.

## Acknowledgment

Development of RVT was part financed by the European Commission's Culture Programme through the ArchaeoLandscapes Europe project and by the Slovenian Research Agency core funding No. P2-0406, and by research projects No. J6-7085 and No. J6-9395.

## License
This project is licensed under the terms of the [Apache License](LICENSE).

