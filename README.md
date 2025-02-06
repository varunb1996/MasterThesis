MACHINE LEARNING FOR THE CHARACTERIZATION OF THE MICRO-STRUCTURE OF POROUS TRANSPORT LAYERS OF ELECTROLYZERS

This master's thesis centers around the parameterization of a stochastic structural model for the 
porous transport layer within electrolysers. It utilizes fundamental micro-structure models and 
employs transport simulation tools that operate on parallel computer clusters. To validate these 
foundational models, empirical relationships from existing literature will be utilized. The thesis 
is structured around three main objectives: 
1. Conducting a comprehensive literature review concerning the characterization of 
porous materials. 
2. Generating micro-structures, executing transport simulations, and subsequently 
analyzing the outcomes. 
3. Employing Machine Learning techniques to forecast the permeability of the 
underlying micro-structures.

GEOMETRY MODEL:
A geometry model based on spheres is used, wherein parameters 
such as sphere diameter, base distance, and porosity are employed to create a three-dimensional 
micro-structure through stochastic methods. This generates artificial structures represented by 
the black and white image series which would be further used for simulation.
40 data points are generated with 200 images per data point. But this is not enough hence, augmentation is performed to obtain 320 data points with 200 images per data point. the oroginal 40 data points are uploaded here 
but the augmented images are not added because they are too big and cannot be uploaded. So each data point has 200 images so for 320 images there are 64000 images.

LATTICE BOLTZMANN METHOD (LBM) SIMULATION:
Palabos was used to perform the LBM simulations on the original 40 data points to obtain permeability value (the augmented points will have the same permeability as the original data points).

ML ALGORITHM:
A CNN was trained to predict the permeability value of the micro-structures. k-fold Cross validation method used to validate the model.
Various hyper-parameter tuning methods were used. A validation accuracy of 95% achieved with such less data.

