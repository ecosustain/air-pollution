from sklearn.neighbors import KNeighborsRegressor
import pyproj
from sklearn.model_selection import  cross_val_score
import numpy as np
import math
from pykrige.ok import OrdinaryKriging
from pykrige.rk import Krige
import itertools
import sys 
import os

def convex_hull_indices(points):
    """
    points -> list of coordinates
    return -> list of indices of the points in the convex hull
    """
    indexed_points = list(enumerate(points))
    indexed_points.sort(key=lambda x: (x[1][0], x[1][1]))
    sorted_indices, sorted_points = zip(*indexed_points)
    
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    
    lower = []
    for i, p in zip(sorted_indices, sorted_points):
        while len(lower) >= 2 and cross(points[lower[-2]], points[lower[-1]], p) <= 0:
            lower.pop()
        lower.append(i)
    
    upper = []
    for i, p in zip(reversed(sorted_indices), reversed(sorted_points)):
        while len(upper) >= 2 and cross(points[upper[-2]], points[upper[-1]], p) <= 0:
            upper.pop()
        upper.append(i)
    
    return list(dict.fromkeys(lower + upper))

class ConvexLOOCV():
    """
    Cross validation data splitter. Fix all points in the boundary of the convex hull
    to the train set and apply leave one out cross validation in the remaining points.
    """

    def split(self, X, y=None, groups=None):
        hull_idx = convex_hull_indices(X)

        folds = []

        for i in range(len(X)):
            if i in hull_idx: continue

            train_index = [k for k in range(len(X)) if k != i]
            test_index = [i]
            folds.append((train_index, test_index))
        
        return folds
    
    def get_n_splits(self, X, y=None, groups=None):
        return len(self.split(X))
    
class Scaler():
    """
    Scale (x_0, x_1) coordinates to [0,1] values while preserving relative distance.
    """
    def fit_transform(self, X):
        self.x_0_max = np.max(X[:,0])
        self.x_0_min = np.min(X[:,0])
        self.x_1_max = np.max(X[:,1])
        self.x_1_min =  np.min(X[:,1])
        self.scale_factor = np.max([self.x_0_max - self.x_0_min, self.x_1_max - self.x_1_min])

        return self.transform(X)

    def transform(self, X):
        _X = np.copy(X)
        _X[:,0] = _X[:,0] - self.x_0_min
        _X[:,1] = _X[:,1] - self.x_1_min
        _X = _X / self.scale_factor

        return _X

class Interpolator():
    """
    Base interpolator class.
    """
    def __init__(self, data, verbose=False):
        self.P = pyproj.Proj(proj='utm', zone=23, south=True, ellps='WGS84') # Sâo Paulo projection zone
        self.scaler = Scaler()
        self.X, self.y = self._preprocess_data(data)

        self.verbose = verbose

    def _preprocess_data(self, data):
        """
        data -> dict  (lat,long) : value
        Convert (lat, long) to [0,1] coordinates preserving relative distance.
        returns 
        X -> coordinates
        y -> values 
        """
        X = data.keys()
        y = [data[k] for k in X if not math.isnan(data[k])]
        X = np.array([list(self.P(c[1], c[0])) for c in X  if not math.isnan(data[c])]) # Projection input is long, lat
        X = self.scaler.fit_transform(X)
        return X,y
    
    def predict(self, X):
        """
        X -> List of (lat, lon) pairs
        returns a list containing interpolated values 
        """
        _X = [self.P(x[1], x[0]) for x in X]
        _X = self.scaler.transform(_X)
        return self.interpolator.predict(_X)
    
class KrigingInterpolator(Interpolator):
    """
    Kriging interpolator class
    """
    def __init__(self, data, param_dict, verbose=False):
        """
        data -> dict  (lat,long) : value
        param_dict -> dict containing parameters for grid search. Possible parameters are given by 
        https://geostat-framework.readthedocs.io/projects/pykrige/en/stable/generated/pykrige.rk.Krige.html#pykrige.rk.Krige
        Example: 
        param_dict = {
            "method": ["ordinary", "universal"],
            "variogram_model": ["linear", "power", "gaussian", "spherical"],
            "nlags": [4, 6, 8],
            "weight": [True, False]
        }
        """
        super().__init__(data, verbose=verbose)
        self.param_dict = {key: value if isinstance(value, list) else [value] for key, value in param_dict.items()}
        params, self.best_score = self._find_params()

        self.interpolator = Krige(**params)
        self.interpolator.fit(self.X,self.y)

    def _find_params(self):
        """
        Apply grid search to find best parameter combination
        """
        best_score = -np.inf
        best_params = {}

        combinations = [dict(zip(self.param_dict.keys(), valores)) for valores in itertools.product(*self.param_dict.values())]

        for c in combinations:
            cv = ConvexLOOCV()
            model = Krige(**c, verbose=False)
            scores = cross_val_score(model, self.X, self.y, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1, verbose=0)
            score = np.mean(scores)

            if score > best_score:
                best_score = score
                best_params = c

            if self.verbose:
                print(f"RMSE: {-score}; params={c}")

        if self.verbose:
            print(f"Best RMSE: {-1 * best_score}; params={best_params}")
        return best_params, -best_score
        


class KNNInterpolator(Interpolator):
    """
    KNN interpolator class.
    """
    def __init__(self, data, k='auto', verbose=False):
        """
        data -> dict  (lat,long) : value
        k -> KNN number of neighbors parameter. Integer for a fixed value or "auto" 
        to select using cross validation
        """

        k = k['k'] if isinstance(k, dict) else k # Allow to receive k as a dict

        super().__init__(data, verbose=verbose) 
        if k == 'auto':
            self.k, self.best_score = self._find_k() 
        else:
            self.k = k
            cv = ConvexLOOCV()
            model = KNeighborsRegressor(n_neighbors=self.k, weights = 'distance')
            scores = cross_val_score(model, self.X, self.y, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1)
            score = np.mean(scores)

            if verbose:
                print(f"RMSE: {-1 * score}")

            self.best_score = -score

        self.interpolator = KNeighborsRegressor(n_neighbors = self.k, weights = 'distance')
        self.interpolator.fit(self.X,self.y)
        

    
    def _find_k(self):
        """
        Apply grid search to find best k parameter.
        """

        best_score = -np.inf
        best_k = -1

        for k in range(1,len(self.y)):
            cv = ConvexLOOCV()
            model = KNeighborsRegressor(n_neighbors=k, weights = 'distance')
            scores = cross_val_score(model, self.X, self.y, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1)
            score = np.mean(scores)

            if score > best_score:
                best_score = score
                best_k = k

            if self.verbose:
                print(f"RMSE: {-score}; k={k}")

        if self.verbose:
            print(f"Best RMSE: {-1 * best_score}; k={best_k}")
        return best_k, -best_score
    
def main():

    X = [[-23.566208579985688, -46.612390087515855],
        [-23.666256213135124, -46.77757667402106],
        [-23.530099662416678, -46.835509169711806],
        [-23.546495191898174, -46.64204969669802],
        [-23.55380623492676, -46.672903802761034],
        [-23.5655461015706, -46.734405289267485],
        [-23.61469263215215, -46.66189287112119],
        [-23.688266405558103, -46.61374371994841],
        [-23.77640719581183, -46.69684001809603],
        [-23.46249691918744, -46.495885904613715],
        [-23.455120602001223, -46.518515858355144],
        [-23.43986912260211, -46.41009814694313],
        [-23.587079204386246, -46.65770300691746],
        [-23.68229846316575, -46.67569777657078],
        [-23.501581234659536, -46.42070443344805],
        [-23.580811719980417, -46.46837926837583],
        [-23.5155126601368, -46.7265656315981],
        [-23.518365400993915, -46.7429296297482],
        [-23.66905543128161, -46.46491684508577],
        [-23.517709187954523, -46.187040918104756],
        [-23.54869617093327, -46.601310350663816],
        [-23.479885648174786, -46.6923604540432],
        [-23.526653491555958, -46.79235938862972],
        [-23.5441946511828, -46.62713713344649],
        [-23.41485503633198, -46.756473948793506],
        [-23.478940200252275, -46.753771508201794],
        [-23.561052296864116, -46.70126515488353],
        [-23.6414089676038, -46.491965233443196],
        [-23.64508918825277, -46.53672911810052],
        [-23.65596671480102, -46.53161859073262],
        [-23.699143597602014, -46.547291631591705],
        [-23.670961607046227, -46.58499485367963],
        [-23.498688875345394, -46.445376446941154],
        [-23.5151867380584, -46.62933870420927],
        [-23.654751624518237, -46.710280982564925],
        [-23.61840136721358, -46.556341859314045],
        [-23.60911197805361, -46.75589374693721]]
    
    y = [math.nan, 100.0, 78.0, math.nan, math.nan, 106.0,
        math.nan, 82.0, 52.0, math.nan, 116.0, math.nan, 111.0,
        100.0, 116.0, 88.0, math.nan, math.nan, math.nan, math.nan,
        math.nan, 112.0, math.nan, 82.0, 129.0, 119.0, math.nan,
        56.0, math.nan, math.nan, 52.0, math.nan, math.nan, 100.0,
        math.nan, 109.0, math.nan]
    
    data = {tuple(a):b for a,b in zip(X,y)}

    interpolator = KNNInterpolator(data, verbose=True, k=1)
    print(interpolator.best_score)
    print(interpolator.predict(X))
    print(100*"#")
    interpolator = KNNInterpolator(data, verbose=True, k=5)
    print(interpolator.predict(X))
    print(100*"#")
    interpolator = KNNInterpolator(data, verbose=True, k='auto')
    print(interpolator.predict(X))
    print(100*"#")

    param_dict = {
    "method": ["ordinary", "universal"],
    "variogram_model": ["linear", "power", "gaussian", "spherical"],
    "nlags": [4, 6, 8],
    "weight": [True, False]
    }

    interpolator = KrigingInterpolator(data,param_dict, verbose=True)
    print(interpolator.predict(X))

    return


if __name__ == "__main__":
    main()