"""
Soft Voting/Majority Rule classifier

This module contains a Soft Voting/Majority Rule classifier for
classification clfs.


"""
from sklearn.base import BaseEstimator
from sklearn.base import ClassifierMixin
from sklearn.base import TransformerMixin
from sklearn.preprocessing import LabelEncoder
import numpy as np
import operator

class EnsembleClassifier(BaseEstimator, ClassifierMixin, TransformerMixin):
    """
    Soft Voting/Majority Rule classifier for classification clfs.
    Parameters
    ----------
    clfs : array-like, shape = [n_classifiers]
      A list of clfs for classification.
    voting : str, {'hard', 'soft'} (default='hard')
      If 'hard', uses predicted class labels for majority rule voting.
      Else if 'soft', predicts the class label based on the argmax of
      the sums of the predicted probalities.
    weights : array-like, shape = [n_classifiers], optional (default=`None`)
      Sequence of weights (`float` or `int`) to weight the occurances of
      predicted class labels (`hard` voting) or class probabilities
      before averaging (`soft` voting). Uses uniform weights if `None`.
    Attributes
    ----------
    classes_ : array-like, shape = [n_predictions]
    Examples
    --------
    >>> import numpy as np
    >>> from sklearn.linear_model import LogisticRegression
    >>> from sklearn.naive_bayes import GaussianNB
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> clf1 = LogisticRegression(random_state=1)
    >>> clf2 = RandomForestClassifier(random_state=1)
    >>> clf3 = GaussianNB()
    >>> X = np.array([[-1, -1], [-2, -1], [-3, -2], [1, 1], [2, 1], [3, 2]])
    >>> y = np.array([1, 1, 1, 2, 2, 2])
    >>> eclf1 = EnsembleClassifier(clfs=[clf1, clf2, clf3], voting='hard')
    >>> eclf1 = eclf1.fit(X, y)
    >>> print(eclf1.predict(X))
    [1 1 1 2 2 2]
    >>> eclf2 = EnsembleClassifier(clfs=[clf1, clf2, clf3], voting='soft')
    >>> eclf2 = eclf2.fit(X, y)
    >>> print(eclf2.predict(X))
    [1 1 1 2 2 2]
    >>> eclf3 = EnsembleClassifier(clfs=[clf1, clf2, clf3],
    ...                          voting='soft', weights=[2,1,1])
    >>> eclf3 = eclf3.fit(X, y)
    >>> print(eclf3.predict(X))
    [1 1 1 2 2 2]
    >>>
    """
    def __init__(self, clfs, voting='hard', weights=None):
        self.clfs = clfs
        self.voting = voting
        self.weights = weights

    def fit(self, X, y):
        """
        Fits the clfs.
        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.
        y : array-like, shape = [n_samples]
            Target values.
        Returns
        -------
        self : object
        """

        if isinstance(y, np.ndarray) and len(y.shape) > 1 and y.shape[1] > 1:
            raise NotImplementedError('Multilabel classification'
                                      ' not implemented, yet.')

        if self.voting not in ('soft', 'hard'):
            raise ValueError("Voting must be 'soft' or 'hard'; got (voting=%r)"
                             % voting)

        if self.weights and len(self.weights) != len(self.clfs):
            raise ValueError('Number of classifiers and weights must be equal'
                             '; got %d weights, %d clfs'
                             % (len(self.weights), len(self.clfs)))

        self.le_ = LabelEncoder()
        self.le_.fit(y)
        self.classes_ = self.le_.classes_

        for clf in self.clfs:
            clf.fit(X, self.le_.transform(y))

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
        maj : array-like, shape = [n_samples]
            Predicted class labels.

        """
        if self.voting == 'soft':

            maj = np.argmax(self.predict_proba(X), axis=1)

        else:  # 'hard' voting
            predictions = self._predict(X)

            maj = np.apply_along_axis(lambda x:
                                      np.argmax(np.bincount(x, weights=self.weights)),
                                      axis=1,
                                      arr=predictions)

        maj = self.le_.inverse_transform(maj)

        return maj

    def predict_proba(self, X):
        """
        Predict class probabilities for X.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.

        Returns
        ----------
        avg : array-like, shape = [n_samples, n_classes]
            Weighted average probability for each class per sample.

        """
        avg = np.average(self._predict_probas(X), axis=0, weights=self.weights)

        return avg

    def transform(self, X):
        """
        Return class labels or probabilities for X for each estimator.

        Parameters
        ----------
        X : {array-like, sparse matrix}, shape = [n_samples, n_features]
            Training vectors, where n_samples is the number of samples and
            n_features is the number of features.

        Returns
        -------
        If `voting='soft'`:
          array-like = [n_classifiers, n_samples, n_classes]
            Class probabilties calculated by each classifier.
        If `voting='hard'`:
          array-like = [n_classifiers, n_samples]
            Class labels predicted by each classifier.

        """
        if self.voting == 'soft':
            return self._predict_probas(X)
        else:
            return self._predict(X)

    def _predict(self, X):
        """ Collects results from clf.predict calls. """

        return np.asarray([clf.predict(X) for clf in self.clfs]).T

    def _predict_probas(self, X):
        """ Collects results from clf.predict calls. """

        return np.asarray([clf.predict_proba(X) for clf in self.clfs])

if __name__ == "__main__":
    import doctest
    doctest.testmod()