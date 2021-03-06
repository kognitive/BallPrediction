# MIT License
#
# Copyright (c) 2017 Markus Semmler, Stefan Fabian
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import numpy as np
import tensorflow as tf

from src.models.RecurrentNeuralNetwork import RecurrentNeuralNetwork


class GatedRecurrentUnit(RecurrentNeuralNetwork):
    """This model represents a GRU recurrent network. It can
    be configured in various ways. This concrete implementation
    features the GRU with forget gates."""

    def __init__(self, config):
        """Constructs a new GRU.

        Args:
            config: The configuration parameters
                unique_name: Define the unique name of this lstm
                num_input: The number of input units per step.
                num_output: The number of output units per step.
                num_hidden: The number of units in the hidden layer.
                num_cells: The number of cells per layer
                num_layers: Define number of time-step unfolds.
                batch_size: This represents the batch size used for training.
                minimizer: Select the appropriate minimizer
                seed: Represents the seed for this model
                momentum: The momentum if the minimizer is momentum
                lr_rate: The initial learning rate
                lr_decay_steps: The steps until a decay should happen
                lr_decay_rate: How much should the learning rate be reduced
        """

        # Perform the super call
        config['clip_norm'] = 0
        config['unique_name'] = "GRU_" + config['unique_name']
        super().__init__(config)

    def get_h(self):
        """Gets a reference to the step h."""
        size = self.config['num_hidden'] * self.config['num_cells']
        return [tf.zeros([size, 1], tf.float32)]

    def get_initial_h(self):
        """Gets a reference to the step h."""
        return self.h

    def get_step_h(self):
        """Retrieve the step h"""
        size = self.config['num_hidden'] * self.config['num_cells']
        return [tf.placeholder(tf.float32, [size, 1], name="step_h")]

    def get_current_h(self):
        """Deliver current h"""
        size = self.config['num_hidden'] * self.config['num_cells']
        return [np.zeros([size, 1])]

    def init_layer(self, name, hidden_mult):
        """This method initializes the weights for a layer with the
        given name.

        Args:
            name: The name of the layer.
        """

        with tf.variable_scope(name, reuse=None):

            # extract parameters
            H = self.config['num_hidden']
            C = self.config['num_cells']
            I = self.config['num_input']

            # The input to the layer unit
            tf.get_variable("W", [H, I], dtype=tf.float32, initializer=self.weights_initializer)
            tf.get_variable("R", [H, H * hidden_mult], dtype=tf.float32, initializer=self.weights_initializer)
            tf.get_variable("b", [H, 1], dtype=tf.float32, initializer=self.bias_initializer)

    def create_layer(self, name, activation, x, h):
        """This method creates one layer, it therefore needs a activation
        function, the name as well as the inputs to the layer.

        Args:
            name: The name of this layer
            activation: The activation to use.
            x: The input state
            h: The hidden state from the previous layer.

        Returns:
            The output for this layer
        """

        with tf.variable_scope(name, reuse=True):

            # The input to the layer unit
            W = tf.get_variable("W")
            R = tf.get_variable("R")
            b = tf.get_variable("b")

            # create the term
            term = W @ x + R @ h + b

            # create the variables only the first times
            return activation(term)

    def init_cell(self, name):
        """This method creates the parameters for a cell with
        the given name

        Args:
            name: The name for this cell, e.g. 1
        """
        with tf.variable_scope(name, reuse=None):

            # init the layers appropriately
            self.init_layer("recurrent_gate", self.config['num_cells'])
            self.init_layer("input_gate", self.config['num_cells'])
            self.init_layer("input_node", 1)

    def create_cell(self, name, x, h_state, num_cell):
        """This method creates a GRU cell. It basically uses the
        previously initialized weights.

        Args:
            x: The input to the layer.
            h: The hidden input to the layer.

        Returns:
            new_h: The new hidden vector
        """

        [h] = h_state

        with tf.variable_scope(name, reuse=True):

            ex_h = tf.slice(h, [self.config['num_hidden'] * num_cell, 0], [self.config['num_hidden'], 1])

            # create all gate layers
            recurrent_gate = self.create_layer("recurrent_gate", tf.sigmoid, x, h)
            mod_h = tf.multiply(recurrent_gate, ex_h)

            input_gate = self.create_layer("input_gate", tf.sigmoid, x, h)
            input_node = self.create_layer("input_node", tf.tanh, x, mod_h)

            # update input gate
            right_input_node = tf.multiply(input_gate, input_node)
            left_input_node = tf.multiply(tf.ones([]) - input_gate, ex_h)

            # calculate the new s
            new_h = tf.add(left_input_node, right_input_node)

        # pass back both states
        return [new_h]
