# -*- coding: utf-8 -*-
"""Copy of Auto-encoder-GD.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aljmBqugFjWhqBdFD4KEHklfI6rHQuWV
"""

# Commented out IPython magic to ensure Python compatibility.
import torch 
import numpy
from torch import nn
from torch.autograd import Variable
import numpy as np
from tqdm import tqdm
# %matplotlib inline
import argparse

import matplotlib.pyplot as plt

class Multivariate_Jacobian_Network(nn.Module):
  def __init__(self, input_dim, hidden_dim, nb_layer, act, host, device):
    super(Multivariate_Jacobian_Network, self).__init__()
    self.input_dim = input_dim
    self.hidden_dim = hidden_dim
    self.nb_layer = nb_layer
    self.act_flag = act

    self.w_in = torch.nn.Parameter(torch.randn(input_dim, self.hidden_dim)  , requires_grad = True) 

    self.w_list = nn.ParameterList([])
    if self.nb_layer > 2:
      for _ in range(self.nb_layer - 2):
        prev_hidden_dim = self.hidden_dim 
        self.w_list.append(torch.nn.Parameter(torch.randn(prev_hidden_dim, self.hidden_dim), requires_grad = True)) 

    self.w_out = torch.nn.Parameter(torch.randn(self.hidden_dim, input_dim) , requires_grad = True)

    self.host = host
    self.device = device
    
  def act(self, x):
    if self.act_flag == 'sigmoid':
      return torch.sigmoid(x) 
    if self.act_flag == 'tanh':
      return torch.tanh(x)
    if self.act_flag == 'erf':
      return torch.erf(x)

  def forward(self, x):
    constant = 1

    x_w_grad = Variable(x.clone(), requires_grad = True)
    self.hid = self.act(x_w_grad @ self.w_in / np.sqrt(self.input_dim) * constant) 

    for i,w in enumerate(self.w_list):
      self.hid = self.act(self.hid @ w / np.sqrt(self.hidden_dim) * constant) 

    y = (self.hid @ self.w_out / np.sqrt(self.hidden_dim) * constant) 
    
    return y, x_w_grad
  
  def forward_with_jacobian(self, x):
    y, x_w_grad = self.forward(x)
    
    jac = self.compute_jacobian(y, x_w_grad)
    
    return y, jac

  def compute_jacobian(self, y, x):
    norm_loss = 0
    mini_batch_size = x.shape[0]

    dim = y.shape[1]
    
    jacobian = torch.zeros(dim, mini_batch_size, dim, device=self.device)
    grad_one_hot = torch.zeros(mini_batch_size, dim, device=self.device)
    
    for i in range(dim):
      grad_one_hot.zero_()
      grad_one_hot[:,i] = 1
      jacobian[i] = torch.autograd.grad(y, x, grad_one_hot, create_graph=True)[0]
      
    return torch.transpose(jacobian, dim0 = 0, dim1 = 1)

  def forward_with_jacobian_with_weight(self, x, w):
    y, x_w_grad = self.forward(x)
    
    jac = self.compute_jacobian_with_last_layer_weight(self.hid, x_w_grad, w)
    
    return jac.clone().cpu().data.numpy()

  def compute_jacobian_with_last_layer_weight(self, y, x, w):
    norm_loss = 0
    mini_batch_size = x.shape[0]
    input_dim = x.shape[1]

    dim = y.shape[1]
    
    pre_jacobian = torch.zeros(dim, mini_batch_size, input_dim)
    jacobian = torch.zeros(mini_batch_size, input_dim, input_dim)
    grad_one_hot = torch.zeros(mini_batch_size, dim)
    
    for i in range(dim):
      grad_one_hot.zero_()
      grad_one_hot[:,i] = 1
      pre_jacobian[i] = torch.autograd.grad(y, x, grad_one_hot, create_graph=True)[0]
      
    jacobian_without_last_layer = torch.transpose(pre_jacobian, dim0 = 0, dim1 = 1)
    for j in range(mini_batch_size):
      jacobian[j] = torch.Tensor(w).T @ jacobian_without_last_layer[j] / np.sqrt(self.hidden_dim)
    
    return jacobian

  def real_jacobian(self, x):
    assert(self.nb_layer == 2)
    mini_batch_size = x.shape[0]
    jacobian = torch.zeros(mini_batch_size, self.input_dim, self.input_dim)
    for i in range(mini_batch_size):
      act_derivative = torch.sigmoid(x[i,:] @ self.w_in / np.sqrt(self.input_dim)) * (1 -  torch.sigmoid(x[i,:] @ self.w_in / np.sqrt(self.input_dim))).squeeze(0) 
      jacobian[i,:] = self.w_out.T @ (self.w_in * act_derivative).T / np.sqrt(self.hidden_dim) / np.sqrt(self.input_dim)
    
    return jacobian
  
  def real_jacobian_with_given_weights(self, x, w_in, w_out):
    assert(self.nb_layer == 2)
    w_in_tensor = torch.Tensor(w_in)
    w_out_tensor = torch.Tensor(w_out)

    mini_batch_size = x.shape[0]
    jacobian = torch.zeros(mini_batch_size, self.input_dim, self.input_dim)
    for i in range(mini_batch_size):
      act_derivative = torch.sigmoid(x[i,:] @ w_in_tensor / np.sqrt(self.input_dim)) * (1 -  torch.sigmoid(x[i,:] @ w_in_tensor / np.sqrt(self.input_dim))).squeeze(0) 
      jacobian[i,:] = w_out_tensor.T @ (w_in_tensor * act_derivative).T / np.sqrt(self.hidden_dim) / np.sqrt(self.input_dim)

    return jacobian

  def return_weights_acts(self):
    w_in = self.w_in.clone().cpu().data.numpy()
    w_out = self.w_out.clone().cpu().data.numpy()
    act = self.hid.clone().cpu().data.numpy()

    return w_in, w_out, act

# function to calulcate kernel matrix
def kernel_mats(net, data, device, use_cuda = True):
  nb_ptr = len(data)
  if use_cuda:
    net = net.cuda()

  # get all the gradients
  grad_list = []
  for x in data:
    if use_cuda:
      x = x.cuda()
    loss, _ = net(x)

    grad_one_hot = torch.zeros(x.shape[0], x.shape[1], device=device)
    grad_one_hot.zero_()
    grad_one_hot[:,0] = 1

    grad_list.append(torch.autograd.grad(loss, net.parameters(), grad_one_hot, retain_graph = True, allow_unused=True))

  # train kernel
  K_trainvtrain = torch.zeros((nb_ptr, nb_ptr), device=device)
  for i in range(nb_ptr):
    grad_i = grad_list[i]
    for j in range(i+1):
      grad_j = grad_list[j]
      K_trainvtrain[i, j] = sum([torch.sum(torch.mul(grad_i[u], grad_j[u])) for u in range(len(grad_j))])
      K_trainvtrain[j, i] = K_trainvtrain[i, j]

  retMat = K_trainvtrain.cpu().detach().numpy()
  net.zero_grad()
  return retMat

class Test():
  def __init__(self, input_dim, hidden_dim, act):
    self.jacobian_compare = False
    self.hidden_feature_compare = False
    self.final_layer_weight_compare = False
    self.weight_compare = False
    self.landscape_compare = False
    self.plot_kernel = False
    self.input_dim = input_dim
    self.hidden_dim = hidden_dim
    self.host = torch.device("cpu")
    self.device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    self.attactors = None
    self.model = None
    self.act = act
    self.training_th = 1e-7
    self.ae_th = 1e-2

  def test(self, nb_layer, x_list, T, learning_rate = 1):
    host = self.host
    nb_fixed_point = len(x_list)
    x_batch_tensor = torch.cat(x_list, axis=0).to(self.device)
    self.attactors = x_batch_tensor

    model = Multivariate_Jacobian_Network(self.input_dim, self.hidden_dim, nb_layer, self.act, self.host, self.device).to(self.device)
    self.model = model

    criterion = torch.nn.MSELoss(reduction='sum')
    optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)
    
    init_jac = np.zeros(nb_fixed_point)
    init_jac_eigvals = np.zeros(nb_fixed_point)
    model.zero_grad()
    y_pred, jac = model.forward_with_jacobian(x_batch_tensor)
    self.w_in_0, self.w_out_0, self.act_0 = model.return_weights_acts()
    
    np_jac = jac.clone().to(host).data.numpy()
    for i in range(nb_fixed_point):
      init_jac[i] = np.linalg.norm(np_jac[i], ord=2)
      largest_eigvals = np.abs(np.linalg.eigvals(np_jac[i])).max()
      init_jac_eigvals[i] = largest_eigvals
    model.zero_grad()
    all_init_jac = np_jac

    if self.jacobian_compare:
      print("initial")
      print(np_jac)
      print(np.linalg.svd(np_jac)[1])
      print(np.linalg.eig(np_jac)[0])
      print(np.linalg.svd(np_jac)[0])
      print(np.linalg.svd(np_jac)[2])
      print(np.linalg.eig(np_jac)[1])
    
    if self.landscape_compare:
        x_test = np.random.normal(size=(10, x_batch_tensor.shape[1])) * 1
        y_test_save = []
        for x in x_test:
          x = np.expand_dims(x,axis=0)
          x_tensor = torch.Tensor(np.expand_dims(x,axis=0))

          y_pred, _ = model(x_tensor)
          y_test_save.append(y_pred.to(host).data.numpy()[0,0])

    if self.plot_kernel:
      center = x_list[0]
      new_x_list = [center]
      new_y_list = [0]
      for i in range(30):
        # new_x_list.append((center).clone() + 0.1 * (i + 1))
        new_x_list.append((center).clone() + 0.1 * (i + 1) * (center).clone() / torch.norm(center))
        new_y_list.append(i+1)
        # new_x_list.append((center).clone() - 0.1 * (i + 1))
        new_x_list.append((center).clone() - 0.1 * (i + 1) * (center).clone()/ torch.norm(center))
        new_y_list.append(-(i+1))
        test_kernel = kernel_mats(model, new_x_list, self.device)
      plt.scatter(new_y_list, test_kernel[0]/test_kernel[0][0])
      plt.show()
      print(test_kernel[0]/test_kernel[0][0])
      print(test_kernel[0])

    self.before_training_kernel = kernel_mats(model, x_list, self.device)
    
    for t in (range(T)):
          
      all_loss = 0 
      optimizer.zero_grad()
      y_pred, x_grad = model(x_batch_tensor)

      if t == 0:
        if self.hidden_feature_compare:
          init_hid = model.hid.clone().to(host).data.numpy() / np.sqrt(self.hidden_dim)
          print(init_hid @ init_hid.T)

      rec_loss = criterion(y_pred.view(-1), x_batch_tensor.view(-1)) / nb_fixed_point
      loss = rec_loss
      
      loss.backward()
      optimizer.step()
      x_grad.grad.zero_()

      all_loss += rec_loss.item()

      if t == 0:
        init_loss = all_loss
        
      if all_loss < self.training_th:
        break
      
    
    final_hid = model.hid.clone().to(host).data.numpy() / np.sqrt(self.hidden_dim)

    final_jac = np.zeros(nb_fixed_point)
    final_jac_eigvals = np.zeros(nb_fixed_point)
    model.zero_grad()
    y_pred, jac = model.forward_with_jacobian(x_batch_tensor)
    self.w_in_t, self.w_out_t, self.act_t = model.return_weights_acts()
    
    np_jac = jac.clone().to(host).data.numpy()
    for i in range(nb_fixed_point):
      final_jac[i] = np.linalg.norm(np_jac[i], ord=2)
      largest_eigvals = np.abs(np.linalg.eigvals(np_jac[i])).max()
      final_jac_eigvals[i] = largest_eigvals
    model.zero_grad()

    all_final_jac = np_jac

    if self.jacobian_compare:
      print("after")
      print(np_jac)
      print(np.linalg.svd(np_jac)[1])
      print(np.linalg.eig(np_jac)[0])
      print(np.linalg.svd(np_jac)[0])
      print(np.linalg.svd(np_jac)[2])
      print(np.linalg.eig(np_jac)[1])

    if self.landscape_compare:
        y_test = []
        for land_i, x in enumerate(x_test):
          x = np.expand_dims(x,axis=0)
          x_tensor = torch.Tensor(np.expand_dims(x,axis=0))
          y_pred,  _ = model(x_tensor)
          y_test.append(y_pred.data.numpy()[0,0])
          print(y_test[land_i] - y_test_save[land_i])

    if self.hidden_feature_compare:
      print(final_hid @ final_hid.T)
      print("hidden feature change: " + str(np.linalg.norm(final_hid - init_hid)))

      if self.final_layer_weight_compare:

        real_weight = self.w_out_t
        # last layer prediction
        x_batch_non_tensor = x_batch_tensor.clone().data.numpy()
        latent_feature_kernel = (final_hid  @ final_hid.T )
        # predicted_weight = (x_batch_non_tensor.T @ np.linalg.inv(latent_feature_kernel + np.ones_like(latent_feature_kernel) * 1) @ final_hid ).T
        predicted_weight = (x_batch_non_tensor.T @ np.linalg.inv(latent_feature_kernel + 0 * np.eye(latent_feature_kernel.shape[0]) ) @ final_hid ).T
        data_mat = x_batch_non_tensor @ x_batch_non_tensor.T

        # predicted_weight = np.linalg.pinv(final_hid.T @ final_hid) @ final_hid.T @ x_batch_non_tensor

        # print(x_batch_non_tensor)
        # print(final_hid @ predicted_weight)
        # print(final_hid @ self.w_out_t)

        # first layer prediction
        input_feature_kernel = (x_batch_non_tensor/ np.sqrt(self.input_dim)  @ x_batch_non_tensor.T/ np.sqrt(self.input_dim) )
        predicted_weight_first_layer = (final_hid.T @ np.linalg.inv(input_feature_kernel) @ x_batch_non_tensor ).T * np.sqrt(self.hidden_dim) / np.sqrt(self.input_dim)
        
        # print(predicted_weight_first_layer)
        # print(self.w_in_0)
        # print(self.w_in_t)
        # print(np.linalg.norm(self.w_in_0 - self.w_in_t))

        real_jacobian = model.forward_with_jacobian_with_weight(x_list[0], real_weight)
        print("real jacobian norm: " + str(np.linalg.norm(real_jacobian[0], ord=2)))
        predicted_jacobian = model.forward_with_jacobian_with_weight(x_list[0], predicted_weight)
        print("predicted jacobian norm: " + str(np.linalg.norm(predicted_jacobian[0], ord=2)))

        real_jacobian_wiht_initial_fisrt_layer = model.real_jacobian_with_given_weights(x_list[0], self.w_in_0, real_weight)
        print("real jacobian norm with initial first layer: " + str(np.linalg.norm(real_jacobian_wiht_initial_fisrt_layer[0], ord=2)))

        real_jacobian_with_init_final_layer_final_first_layer = model.real_jacobian_with_given_weights(x_list[0], self.w_in_t, self.w_out_0)
        print("real jacobian norm with final first layer and initial last layer: " + str(np.linalg.norm(real_jacobian_with_init_final_layer_final_first_layer[0], ord=2)))

        predicted_jacobian_wiht_initial_fisrt_layer = model.real_jacobian_with_given_weights(x_list[0], self.w_in_0, predicted_weight)
        print("predicted jacobian norm with initial first layer: " + str(np.linalg.norm(predicted_jacobian_wiht_initial_fisrt_layer[0], ord=2)))

        predicted_jacobian_wiht_final_fisrt_layer = model.real_jacobian_with_given_weights(x_list[0], self.w_in_t, predicted_weight)
        print("predicted jacobian norm with final first layer: " + str(np.linalg.norm(predicted_jacobian_wiht_final_fisrt_layer[0], ord=2)))

        predicted_jacobian_with_inital_weight = model.forward_with_jacobian_with_weight(x_list[0], self.w_out_0)
        print("predicted jacobian norm with initial weight: " + str(np.linalg.norm(predicted_jacobian_with_inital_weight[0], ord=2)))

        first_layer_jacobian = model.real_jacobian_with_given_weights(x_list[0], predicted_weight_first_layer, self.w_out_0)
        print("first_layer_prediction_jacobian: " + str(np.linalg.norm(first_layer_jacobian[0], ord=2)))

      
    if self.weight_compare:
      print("output weight norm change: " + str(np.linalg.norm(self.w_out_t - self.w_out_0) /np.sqrt(self.hidden_dim) ))
      # print("weight prediction norm change: " + str(np.linalg.norm(self.w_out_t - predicted_weight) /np.sqrt(self.hidden_dim) ))
      print(np.linalg.norm(self.w_out_t))
      # print(np.linalg.norm(predicted_weight_first_layer))
      # print((self.w_out_0))
      # print(self.w_out_t)
      
    after_training_kernel = kernel_mats(model, x_list, self.device)
    diff_kernel = np.linalg.norm(after_training_kernel - self.before_training_kernel)
    return init_jac, final_jac, init_loss, all_loss, diff_kernel, t, all_init_jac, all_final_jac, init_jac_eigvals, final_jac_eigvals
  
  def test_jacobian_change(self):
    print("test jacobian change hidden dim " + str(self.hidden_dim) )
    w_in_0 = self.w_in_0
    w_out_0 = self.w_out_0
    dev_0 = (self.act_0 * (1 - self.act_0))[0,:]

    w_in_t = self.w_in_t
    w_out_t = self.w_out_t
    dev_t = (self.act_t * (1 - self.act_t))[0,:]

    # w_in_t = self.w_in_0 + 1 / np.sqrt(self.hidden_dim)
    # w_out_t = self.w_out_0 + 1 / np.sqrt(self.hidden_dim)
    # dev_t = dev_0 + 1 / np.sqrt(self.hidden_dim)

    delta_w_in = w_in_t - w_in_0
    delta_w_out = w_out_t - w_out_0
    delta_dev = dev_t - dev_0

    # print(delta_w_in.mean(), 1 / np.sqrt(self.hidden_dim))
    # print(delta_w_out.mean(), 1 / np.sqrt(self.hidden_dim))
    # print(delta_dev.mean(), 1 / np.sqrt(self.hidden_dim))

    init_jacobian = w_out_0.T @ np.diag(dev_0) @ w_in_0.T / np.sqrt(self.hidden_dim) / np.sqrt(self.input_dim)
    final_jacobian = w_out_t.T @ np.diag(dev_t) @ w_in_t.T / np.sqrt(self.hidden_dim) / np.sqrt(self.input_dim)

    delta_w_in_jacobian = w_out_0.T @ np.diag(dev_0) @ delta_w_in.T / np.sqrt(self.hidden_dim) / np.sqrt(self.input_dim)
    delta_w_out_jacobian = delta_w_out.T @ np.diag(dev_0) @ w_in_t.T / np.sqrt(self.hidden_dim) / np.sqrt(self.input_dim)
    delta_dev_jacobian = w_out_0.T @ np.diag(delta_dev) @ w_in_t.T / np.sqrt(self.hidden_dim) / np.sqrt(self.input_dim)

    print("all the operator norm")
    print(np.linalg.norm(delta_w_in_jacobian, ord=2))
    print(np.linalg.norm(delta_w_out_jacobian, ord=2))
    print(np.linalg.norm(delta_dev_jacobian, ord=2))
    M = 1000
    init_z_norms = np.zeros(M)
    final_z_norms = np.zeros(M)
    delta_w_in_z_norms = np.zeros(M)
    delta_w_out_z_norms = np.zeros(M)
    delta_dev_z_norms = np.zeros(M)

    for i in range(M):
      z = np.random.uniform(-np.sqrt(self.input_dim), np.sqrt(self.input_dim), size = (self.input_dim, 1))
      z /= np.linalg.norm(z)

      init_z = init_jacobian @ z
      init_z_norms[i] = np.linalg.norm(init_z)
      final_z = final_jacobian @ z
      final_z_norms = np.linalg.norm(final_z)

      delta_w_in_z = delta_w_in_jacobian @ z
      delta_w_in_z_norms[i] = np.linalg.norm(delta_w_in_z)
      delta_w_out_z = delta_w_out_jacobian @ z
      delta_w_out_z_norms[i] = np.linalg.norm(delta_w_out_z)
      delta_dev_z = delta_dev_jacobian @ z
      delta_dev_z_norms[i] = np.linalg.norm(delta_dev_z)
      
    print(init_z_norms.mean(), final_z_norms.mean())

    print(delta_w_in_z_norms.mean(), delta_w_out_z_norms.mean(), delta_dev_z_norms.mean())
  
  def test_kernel(self):
    print(self.before_training_kernel)
    print(np.linalg.eig(self.before_training_kernel))

  def memorize_test(self, radis = 1, max_iter = 50):
    sucess = 0
    for x_id, x in enumerate(self.attactors):
      x_pretubed = x + torch.Tensor(np.random.uniform(-1*radis, radis, size = (1, self.input_dim))).to(self.device)

      for _ in range(max_iter):
        x_pretubed, _, = self.model(x_pretubed)
        diff = x.cpu().data.numpy() - x_pretubed.cpu().data.numpy()
        if np.linalg.norm(diff) < self.ae_th:
          sucess += 1
          break
    return sucess 
      
  def finding_other_fixed_point(self, constant):
      x = np.random.uniform(-constant, constant, size = (1, self.input_dim))
      
      x_pretubed = torch.Tensor(x).to(self.device)
      print("start point:")
      print(x_pretubed.cpu().data.numpy())

      for _ in range(30):
        x_pretubed, _, = self.model(x_pretubed)

      print("converged point:")
      print(x_pretubed.cpu().data.numpy())
      
      print("training points")
      for x_id, x in enumerate(self.attactors):
        print(x.cpu().data.numpy())

if __name__ == '__main__':

  parser = argparse.ArgumentParser()

  parser.add_argument('--input_dim', type=int, default= 100, help='input dimension')
  parser.add_argument('--nb_fixed_point', type=int, default= 2, help='number of fixed points')

  parser.add_argument('--nb_layer', type=int, default= 2, help='number of layers')
  parser.add_argument('--hidden_dim', type=int, default= 1000, help='hidden layers')

  parser.add_argument('--act', type=str, default='sigmoid')

  parser.add_argument('--dir', type=str, default= "./test_add_on")
  
  args = parser.parse_args()

  import os
  if not os.path.exists(args.dir):
    os.makedirs(args.dir)

  T = 100000
  M = 100

  for constant in ([1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]):
    for input_dim in ([args.input_dim]):
      for nb_fixed_point in ([args.nb_fixed_point]):
        all_x_list = []
        for i in (range(M)):
          x_list = []
          x_numpy_list = []
          for _ in range(nb_fixed_point):
            a = np.random.normal(0, np.sqrt(input_dim), size = (1, input_dim))
            a_normalized = a/np.linalg.norm(a) * constant
            x_list.append(torch.Tensor(a_normalized))

          all_x_list.append(x_list)

        for nb_layer in [args.nb_layer]:
          for hidden_dim in ([args.hidden_dim]):
            for lr in ([1]):
              first = np.zeros((M, nb_fixed_point))
              last = np.zeros((M, nb_fixed_point))
              init_losses = np.zeros(M)
              losses = np.zeros(M)
              kernel_diff = np.zeros(M)
              converged_T = np.zeros(M)
              mem_radius_all = np.linspace(1, 100, 100)
              converged_mem_success = np.zeros((M, mem_radius_all.shape[0]))

              first_eig = np.zeros((M, nb_fixed_point))
              last_eig = np.zeros((M, nb_fixed_point))
              all_first = np.zeros((M, nb_fixed_point, input_dim, input_dim))
              all_final = np.zeros((M, nb_fixed_point, input_dim, input_dim))
              
              for i in tqdm(range(M)):
                x_list = all_x_list[i]
                test = Test(input_dim, hidden_dim, args.act)
                first[i, :], last[i, :], init_losses[i], losses[i], kernel_diff[i], converged_T[i], all_first[i,:,:,:], all_final[i,:,:,:], first_eig[i, :], last_eig[i, :]  = test.test(nb_layer, x_list, T, lr)
                # test.test_jacobian_change()
                # test.test_kernel()
                
                for k, mem_radius in enumerate(mem_radius_all):
                  converged_mem_success[i, k] = test.memorize_test(radis=mem_radius) / nb_fixed_point
                # test.finding_other_fixed_point(constant)

              print(input_dim, constant, nb_fixed_point, nb_layer, hidden_dim, converged_T.mean(), init_losses.mean(), losses.mean(), kernel_diff.mean(), first.mean(), last.mean(), (last - first).mean(), first.std(), last.std(), (last - first).std())
              
              filename = args.act + '_eig_input_dim' + str(input_dim) + '_constant' +str(constant) + '_np' + str(nb_fixed_point) + '_nl' + str(nb_layer) + '_h' + str(hidden_dim) + '.npz'
              np.savez(args.dir + '/' +filename, first_eig=first_eig, last_eig=last_eig, all_first=all_first, all_final=all_final, first=first, last=last, init_losses=init_losses, losses = losses, kernel_diff = kernel_diff, converged_T = converged_T, converged_mem_success = converged_mem_success)