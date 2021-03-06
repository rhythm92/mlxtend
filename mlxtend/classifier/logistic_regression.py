# Sebastian Raschka 2015
# mlxtend Machine Learning Library Extensions


import numpy as np

class LogisticRegression(object):
    """Logistic regression classifier.

    Parameters
    ------------
    eta : float
      Learning rate (between 0.0 and 1.0)

    epochs : int
      Passes over the training dataset.

    learning : str (default: sgd)
      Learning rule, sgd (stochastic gradient descent)
      or gd (gradient descent).

    lambda_ : float
      Regularization parameter for L2 regularization.
      No regularization if lambda_=0.0.

    Attributes
    -----------
    w_ : 1d-array
      Weights after fitting.

    cost_ : list
      List of floats with sum of squared error cost (sgd or gd) for every
      epoch.

    """
    def __init__(self, eta=0.01, epochs=50, lambda_=0.0, learning='sgd'):
        self.eta = eta
        self.epochs = epochs
        self.lambda_ = lambda_

        if not learning in ('sgd', 'gd'):
            raise ValueError('learning must be sgd or gd')
        self.learning = learning


    def fit(self, X, y, init_weights=None):
        """ Fit training data.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.

        y : array-like, shape = [n_samples]
            Target values.

        init_weights : array-like, shape = [n_features + 1]
            Initial weights for the classifier. If None, weights
            are initialized to 0.

        Returns
        -------
        self : object

        """
        if not len(X.shape) == 2:
            raise ValueError('X must be a 2D array. Try X[:,np.newaxis]')

        if (np.unique(y) != np.array([0, 1])).all():
            raise ValueError('Supports only binary class labels 0 and 1')

        if not isinstance(init_weights, np.ndarray):
        # Initialize weights to 0
            self.w_ = np.zeros(1 + X.shape[1])
        else:
            self.w_ = init_weights

        self.cost_ = []

        for i in range(self.epochs):

            if self.learning == 'gd':
                y_val = self.activate(X)
                errors = (y - y_val)
                regularize = self.lambda_ * self.w_[1:]
                self.w_[1:] += self.eta * X.T.dot(errors)
                self.w_[1:] += regularize
                self.w_[0] += self.eta * errors.sum()

            elif self.learning == 'sgd':
                cost = 0.0
                for xi, yi in zip(X, y):
                    yi_val = self.activate(xi)
                    error = (yi - yi_val)
                    regularize = self.lambda_ * self.w_[1:]
                    self.w_[1:] += self.eta * xi.dot(error)
                    self.w_[1:] += regularize
                    self.w_[0] += self.eta * error

            self.cost_.append(self._logit_cost(y, self.activate(X)))
        return self

    def predict(self, X):
        """
        Predict class labels for X.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.

        Returns
        ----------
        class : int
          Predicted class label.

        """
        return np.where(self.activate(X) >= 0.5, 1, 0)

    def activate(self, X):
        """
        Predict class labels for X.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.

        Returns
        ----------
        int
          Class probability.

        """
        z = X.dot(self.w_[1:]) + self.w_[0]
        return self._sigmoid(z)

    def _logit_cost(self, y, y_val):
        logit = -y.dot(np.log(y_val)) - ((1 - y).dot(np.log(1 - y_val)))
        regularize = (self.lambda_ / 2) * self.w_[1:].dot(self.w_[1:])
        return logit + regularize

    def _sigmoid(self, z):
         return 1.0 / (1.0 + np.exp(-z))
