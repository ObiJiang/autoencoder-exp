# Auto Encoder Experiments

### How to run it?
Example Usage:
```
python auto_encoder_gd.py --input_dim 32 --nb_fixed_point 2  --constant 1 --nb_layer 2 --hidden_dim 1000 --act sigmoid
```

Please use `python auto_encoder_gd.py -h` to get info on what those parameters are.

### Output
The program will print the following data:

````
input_dim, constant, nb_fixed_point, nb_layer, hidden_dim, average iteration to converge, average initial loss, average final loss, average initial Jacobian norm, final Jacobian norm, the average difference between initial and final Jacobian norm
````

It will also save all the output data in NumPy arrays, including the Jacobina matrices of networks. Please refer to the code to get details on that. 