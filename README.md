# Blender_APX_Addon

## Content of the addon

 Import/export .apx cloth, hair and destruction simulation files into/from blender.
 Developed for Blender 4.2.0, other versions are not tested.
 
 The geometry nodes implementation of (X)PBD simulations is the work of [Lukas Tönne](https://github.com/lukas-toenne/node-assets). 

 This tool comes with a side panel in the 3D Viewport with:
 - Ragdoll subpanel offers easy ragdoll creation, generation and mirroring
 - Cloth painting subpanel offers clear visualization and easy painting of the constraints used by apex clothing, along with common paint tools **(requires an active mesh)**
 - Cloth simulation subpanel offers control over general simulation parameters over the entire asset (e.g. gravity, wind, simulation thickness, etc)
 - Cloth material subpanel offers control over the simulation paramaters defining the kind of fabric/material used by a specific mesh **(requires an active mesh)**
 - Hair pin subpanel offers easy pin creation
 - Hair tools subpanel offers an efficient toolkit for curves generation and conversion
 - Hair material subpanel offers control over the physical and graphical parameters that define the simulation and looks of an hairworks asset
 
 ## Recommendations
 
 - In order to read .apb files, you must indicate the path to the APEX SDK command line .exe in the addon preferences.
 ![Imgur](https://i.imgur.com/5Vnfx5P.png)
 You can get that **ParamToolPROFILE.exe** by downloading the APEX SDK (v1.3.0 or v1.3.1) [here](https://developer.nvidia.com/gameworksdownload#?search=physX).
 
 ## Limitations
 
 - Cloth real-time simulation performs decently on small meshes, but might not offer suitable performances on dense meshes. It also only has rest edge length constraints as implementing shearing, bending and tether constraints would worsen the performances even further,
 - The addon leverages Blender's builtin simulations (for hair and destruction assets) which are extremely far from PhysX simulation,
 - Blender freezes when importing some destruction assets. For some reason it fails at separating a mesh by selected vertices sometimes,
 - Destruction assets import is incomplete and export is non-existent at the moment.
 
 ## Demonstration
 
 Clothing APX - Import:
 
 [![APX Clothing Importer Video](https://i.ytimg.com/vi/QH6N0Q8Ue74/maxresdefault.jpg)](https://www.youtube.com/watch?v=QH6N0Q8Ue74)
 
 Hairworks APX - Export and Import:
 
 [![APX Hairworks Exporter Importer Video](https://i.ytimg.com/vi/Q2ByGES0_-s/maxresdefault.jpg)](https://www.youtube.com/watch?v=Q2ByGES0_-s)
 
 ## Documentation
 
 [Official APEX Cloth Documentation](https://gameworksdocs.nvidia.com/APEX/1.4/docs/APEX_Clothing/Index.html)
 
 [Official Hairworks Documentation](https://docs.nvidia.com/gameworks/content/artisttools/hairworks/product.html)
 
 Copyright (c) 2021 Ard Carraigh
 
 This project is licensed under the terms of the Creative Commons Attribution-NonCommercial 4.0 International Public License.
