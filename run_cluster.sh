#!/bin/bash

# 2-layer 40 point test
inputdims=(16 32)
nbFixedPoints=(40)
nbLayers=(2)
hiddenDims=(1000 10000 100000 500000 1000000)
Dirs=('/n/scratchlfs02/pehlevan_lab/yibo_autoencoder_eig_add_on')
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

# 3-layer, single point test
inputdims=(16, 32)
nbFixedPoints=(1)
nbLayers=(3, 4)
hiddenDims=(100 1000 10000)
Dirs=('/n/scratchlfs02/pehlevan_lab/yibo_autoencoder_eig_add_on')
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

# large activation test for eigen spectrum
inputdims=(16, 32)
nbFixedPoints=(20)
nbLayers=(2)
hiddenDims=(1000, 10000, 100000)
Dirs=('/n/scratchlfs02/pehlevan_lab/yibo_autoencoder_eig_add_on')
Acts=('sigmoid' 'tanh' 'erf')

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