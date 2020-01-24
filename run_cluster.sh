#!/bin/bash
inputdims=(16)
nbFixedPoints=(1, 5, 20, 100)
nbLayers=(2)
hiddenDims=(1000, 10000, 100000, 500000, 1000000)
Dirs=('/n/scratchlfs02/pehlevan_lab/yibo_autoencoder')

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

echo $inputDim, $nbFixedPoint, $nbLayer, $hiddenDim, $Dir, 0.1, 1, 10
export inputDim nbFixedPoint nbLayer hiddenDim Dir

sbatch -o out_i${inputDim}_np${nbFixedPoint}_nl${nbLayer}_h${hiddenDim}.stdout.txt \
-e err_i${inputDim}_np${nbFixedPoint}_nl${nbLayer}_h${hiddenDim}.stdout.txt \
--job-name=auto_encoder_ri${inputDim}_np${nbFixedPoint}_nl${nbLayer}_h${hiddenDim} \
run_script.sbatch

sleep 1

done
done
done
done
done