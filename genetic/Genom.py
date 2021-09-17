import numpy as np

class Genome():
    def __init__(self):
        pass

    def relu(self, x):
        if x>=0:
            return x
        elif x<0:
            return 0
        pass

    def sigmoid(self, x):
        return 1/(1+np.exp(-x))
        pass

    def softmax(self, x):
        pass

    def leaky_relu(self, x):
        if x>=0:
            return x
        elif x<0:
            return 0.01 * x
        pass

    pass



if __name__ == '__main__':
    test = (1, 0)
    print(test[0])