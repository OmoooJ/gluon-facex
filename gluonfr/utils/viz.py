# MIT License
#
# Copyright (c) 2018 Haoxintong
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
""""""
import seaborn as sns
import matplotlib.pyplot as plt


def plot_roc(tpr, fpr, x_name="FPR", y_name="TPR"):
    sns.set(style="darkgrid")
    plt.figure(figsize=(8, 8))
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.title("ROC")

    sns.lineplot(x=x_name, y=y_name, data={x_name: fpr, y_name: tpr})
    plt.show()


def plot_accuracy(accs, threholds):
    sns.set(style="darkgrid")
    plt.figure(figsize=(8, 8))
    plt.xlabel("threshold")
    plt.ylabel("accuracy")
    plt.title("Accuracy")

    sns.lineplot(x="threshold", y="accuracy", data={"accuracy": accs, "threshold": threholds})
    plt.show()
