#!/bin/bash

# large activation test
inputdims=(100)
nbFixedPoints=(20 50 80)
nbLayers=(2)
hiddenDims=(1000)
Dirs=('/n/scratchlfs02/pehlevan_lab/yibo_autoencoder_eig_linear')
Acts=('sigmoid' 'tanh')

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

# # 3-layer
# inputdims=(16)
# nbFixedPoints=(1 5 20 100)
# nbLayers=(3)
# hiddenDims=(100 1000 10000)
# Dirs=('/n/scratchlfs02/pehlevan_lab/yibo_autoencoder_eig')

# # 2-layer change input dims
# inputdims=(8 32)
# nbFixedPoints=(1 5 20 100)
# nbLayers=(2)
# hiddenDims=(1000 10000 100000 500000 1000000)
# Dirs=('/n/scratchlfs02/pehlevan_lab/yibo_autoencoder_eig')