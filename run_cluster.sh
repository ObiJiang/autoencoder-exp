#!/bin/bash

# basin of attraction
inputdims=(32)
nbFixedPoints=(5 10 15 20 25 30 35 40)
nbLayers=(2)
hiddenDims=(10000)
Dirs=('/n/scratchlfs02/pehlevan_lab/yibo_autoencoder_eig_basin')
Acts=('sigmoid')

for inputDim in "${inputdims[@]}"
do

for nbFixedPoint in "${nbFixedPoints[@]}"
do

for nbLayer in "${nbLayers[@]}"
do

for hiddenDim in "${hiddenDims[@]}"
do

for Dir in "${Dirs[@]}"
do

for Act in "${Acts[@]}"
do

echo $inputDim, $nbFixedPoint, $nbLayer, $hiddenDim, $Dir, $Act, 0.1, 1, 10
export inputDim nbFixedPoint nbLayer hiddenDim Dir Act

sbatch -o out_eig_i${inputDim}_np${nbFixedPoint}_nl${nbLayer}_h${hiddenDim}_a${Act}.stdout.txt \
-e err_eig_i${inputDim}_np${nbFixedPoint}_nl${nbLayer}_h${hiddenDim}_a${Act}.stdout.txt \
--job-name=auto_encoder_ri${inputDim}_np${nbFixedPoint}_nl${nbLayer}_h${hiddenDim}_a${Act} \
run_script.sbatch

sleep 1

done
done
done
done
done
done