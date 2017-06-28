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

# This interface represents a basic DataFilter. It only supports one operation
# and gets used inside of the data adapter, when the data is loaded.


class DataFilter:

    # This method should take the trajectory and return the filtered version of
    # it. It applies the internal filter method to each trajectory and removes
    # the empty ones.
    #
    # trajectories - This is a list of trajectories
    #
    def filter(self, trajectories):

        # filter trajectories.
        f_trajectories = [self.apply_filter(trajectory) for trajectory in trajectories]
        rf_trajectories = list(filter(lambda x: x.shape[0] != 0, f_trajectories))

        return rf_trajectories

    # This method should take one trajectory and return the filtered version of
    # it.
    #
    # trajectory - This is a trajectory
    #
    def apply_filter(self, trajectory):
        raise NotImplementedError("You have to supply a trajectory filter method.")
