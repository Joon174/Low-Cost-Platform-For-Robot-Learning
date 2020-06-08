## @package agent.py
#  @brief Script containing the parent class Agent which bridges the PyTorch package and Matplotlib for testing the model

import os
import json
import torch
import matplotlib.pyplot as plt

## Debugger
#  If the test rewards need to be plot out, the debugger can called in the Agent class for visualization. Visualization
#  is done using the matplotlib python package.
class Debugger:
    ## Constructor
    # @param xlabel Labels the x-axis with xlabel.
    # @param ylabel Labels the y-axis with ylabel.
    def __init__(self, xlabel="Time Step", ylabel="Angle Of System"):
        self.matplot = plt
        self.matplot.xlabel(xlabel)
        self.matplot.ylabel(ylabel)

    ## plotValues
    #  @brief Plots the reward and target of the model for the current episode. Defaults as a scatter plot.
    #  @param x_value Plots the input value on the x-axis
    #  @param y_value Plots the input value on the y-axis
    def plotValues(self, x_value, y_value):
        self.matplot.scatter(x_value, y_value[0], color=['red'])
        self.matplot.scatter(x_value, y_value[1], color=['blue'])
        self.matplot.pause(0.01)

    ## showPlot
    #  @brief Opens a window to illustrate the plot generated from the Debugger class.
    def showPlot(self):
        self.matplot.show()

## Agent
#  The Parent class which can be used to create instances of Agents using inheritance. The class checks for CUDA cores to use
#  for GPU computation and read JSON files for the hyperparameters of the model. The class contains frequently used parameters
#  in Reinforcecment Learning such as: rewards, loss, epoch number, time step and frame index. A Debugger is instantiated in the
#  class for debugging should the user feel the need to.
class Agent:
    ## Constructor
    #  Upon constructing the class, the Agent class will search for CUDA cores on the computer to determine if GPU compitation
    #  is possbile.
    def __init__(self):
        self.device = self._testCUDAAvailable()
        self.debugger = Debugger()

        # Common Training Parameters
        self.frame_idx = 0
        self.time_step = 0
        self.training = True
        self.rewards = 0
        self.test_rewards = []
        self.ep_num = 0
        self.loss = 0
    
    ## getParameters
    #  Method used to read a JSON file to configure the Agent's architecture with the selected hyperparameters in the JSON file.
    #  The method will return with an error and terminate the program if no JSON configuration file is found.
    #  @param config_file The path to the JSON configuration file in the local directory.
    def _getParameters(self, config_file):
        try: 
            with open(config_file, 'r') as json_data_file:
                return json.load(json_data_file)
        except AttributeError:
            print("Unable to locate local JSON Configuration File")
            exit(0)

    ## testCUDAAvailable
    #  Method used to verify if the local machine contains CUDA cores to use with the Pytorch package for GPU computation
    #  If no CUDA cores are found, the scirpt will terminate and output an error.
    def _testCUDAAvailable(self):
        use_cuda = torch.cuda.is_available()
        try:
            device = torch.device("cuda" if use_cuda else "cpu")
            print("Current Training is attached to device: {}\r".format(device))
            return device
        except AttributeError:
            print("Pytorch cannot find any cpu or cuda chips available for training.\n This class uses cuda cores to create the model. To use cpu, \
                set arguement 'use_cuda' to false.")
            exit(0)

    ## test_env
    #  Method for Testing the model against the single instance of the environment. This will allow the model to be verified
    #  if trained properly. User can validate the performance of the model by calling this function and pass the environment
    #  and model through it.
    def test_env(self, env, vis=False, plot=False):
        state = env.reset()
        done = False
        total_reward = 0
        time_step = 0
        while not done:
            if vis: env.render()
            state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            dist, _ = self.model(state)
            next_state, reward, done, info = env.step(dist.sample().cpu().numpy()[0])
            state = next_state
            if plot:
                self.debugger.plotValues(time_step, [info['Model Leg Pos (radians)'], info['Target Leg Pos (radians)']])
            total_reward += reward
            time_step += 1
        self.debugger.showPlot()
        print("Test Reward: {0}".format(total_reward))
        return total_reward

    ## saveWeights
    #  Method for saving weights of the model into the local directory. For unit testing, this function will save the entire
    #  model architecture in addition to the weights.
    #  @param directory Folder the model will be saved to
    #  @param file_name Name of the file which the model will be saved. 
    def saveWeights(self, directory, file_name, model):
        if file_name is None:
            file_name = "proof_of_concept_model.pt"
        if directory is None:
            directory = "modelWeights" 
        model_path = os.path.join(os.getcwd(), directory, file_name).replace("\\", "/")
        torch.save(model.state_dict(), model_path)
    
    def saveModel(self, directory, file_name, model):
        if file_name is None:
            file_name = "proof_of_concept_model.pt"
        if directory is None:
            directory = "modelWeights" 
        model_path = os.path.join(os.getcwd(), directory, file_name).replace("\\", "/")
        torch.save(model, model_path)
    
    def loadWeights(self, directory, file_name):
        if file_name is None:
            file_name = "proof_of_concept_model.pt"
        if directory is None:
            directory = "modelWeights" 
        model_path = os.path.join(os.getcwd(), directory, file_name).replace("\\", "/")
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        
    def loadModel(self, directory, file_name):
        if file_name is None:
            file_name = "proof_of_concept_model.pt"
        if directory is None:
            directory = "modelWeights" 
        model_path = os.path.join(os.getcwd(), directory, file_name).replace("\\", "/")
        self.model = torch.load(model_path)

    def plotResults(self, results):
        plt.figure(figsize=(12,8))
        plt.plot(results, label='Rewards')
        plt.xlabel('Frames')
        plt.ylabel('Rewards')
        plt.show()