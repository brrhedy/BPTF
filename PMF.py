#!usr/bin/env python
#coding:utf-8

from readConfig import ReadConfig
import numpy as np


class PMF:
    def __init__(self, trainMatrix, testMatrix, cf):
        self.trainMatrix = trainMatrix
        self.testMatrix = testMatrix
        self.cf = cf
        self.numUsers = 0
        self.numItems = 0
        self.predictions = dict()

    def initModel(self):
        self.numUsers, self.numItems = self.trainMatrix.shape
        self.MAX_Iterations = int(self.cf.getParameter('PMF', 'MAX_Iterations'))
        self.numFactors = int(self.cf.getParameter('PMF', 'numFactors'))
        self.lRate = float(self.cf.getParameter('PMF', 'rate'))
        self.regU = float(self.cf.getParameter('PMF', 'regU'))
        self.regI = float(self.cf.getParameter('PMF', 'regI'))

        self.P = np.random.normal(0, 1, size=(self.numUsers, self.numFactors))
        self.Q = np.random.normal(0, 1, size=(self.numItems, self.numFactors))

    def buildModel(self):

        oldLoss = np.inf
        for iteration in range(self.MAX_Iterations):
            loss = 0.0

            for u in range(self.numUsers):
                for i in range(self.numItems):
                    rate = self.trainMatrix[u, i]
                    if rate == 0:
                        continue
                    pr_ui = self.predict(u, i)
                    eui = rate - pr_ui
                    loss += eui**2

                    self.P[u, :] += self.lRate * (eui * self.Q[i, :] - self.regU * self.P[u, :])
                    self.Q[i, :] += self.lRate * (eui * self.P[u, :] - self.regI * self.Q[i, :])

                    loss += self.regU * np.sum(self.P[u, :] * self.P[u, :]) + self.regI * np.sum(self.Q[i, :] * self.Q[i, :])

            if np.abs(oldLoss - loss) < 0.001:
                break
            else:
                oldLoss = loss

        for u in range(self.numUsers):
            for i in range(self.numItems):
                rate = self.testMatrix[u, i]
                if rate == 0:
                    continue
                self.prediction[(u, i)] = self.predict(u, i)


    def predict(self, u, i):
        return np.sum(self.P[u, :] * self.Q[i, :])

    def evaluate(self, evalString):
        metrics = {'rmse': self.rmse, 'mse': self.mse, 'mae': self.mae}
        result = metrics[evalString]()
        return result

    def rmse(self):
        loss = 0
        num = 0
        for u, i in self.predictions:
            error = self.testMatrix[u, i] - self.prediction[(u, i)]
            loss += error * error
            num += 1
        return np.sqrt(loss/num)

    def mse(self):
        loss = 0
        num = 0
        for u, i in self.predictions:
            error = self.testMatrix[u, i] - self.prediction[(u, i)]
            loss += error * error
            num += 1
        return loss / num

    def mae(self):
        loss = 0
        num = 0
        for u, i in self.prediction:
            error = np.abs(self.testMatrix[u, i] - self.predictions[(u, i)])
            loss += error
            num += 1
        return loss / num


    def execute(self):
        self.initModel()
        self.buildModel()
        self.evaluate()



if __name__ == '__main__':
    print '__main__'