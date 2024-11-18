from sklearn.neighbors import KNeighborsRegressor
import pyproj
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import LeaveOneOut, cross_val_score
import numpy as np
import math
from pykrige.ok import OrdinaryKriging
from pykrige.rk import Krige
import itertools
import sys 
import os


class Interpolator:
    def __init__(self, data, verbose=False):
        self.P = pyproj.Proj(proj='utm', zone=23, south=True, ellps='WGS84') # Projeção para a zona de SP
        self.scaler = MinMaxScaler()
        self.X, self.y = self.__preprocess_data__(data)

        self.verbose = verbose

    def __preprocess_data__(self, data):

        X = data.keys()
        y = [data[k] for k in X if not math.isnan(data[k])]
        X = [self.P(c[1], c[0]) for c in X  if not math.isnan(data[c])] # input é long, lat
        X = self.scaler.fit_transform(X)
        return X,y
    
    def predict(self, X):
        """
        X -> Lista de pares (lat, lon)
        retorna uma lista com valores interpolados
        """
        _X = [self.P(x[1], x[0]) for x in X]
        _X = self.scaler.transform(_X)
        return self.interpolator.predict(_X)


class KrigingInterpolator(Interpolator):
    def __init__(self, data, param_dict, verbose=False):
        """
        data -> dict com pares "coord" : "medida"
        """
        super().__init__(data, verbose=verbose)
        self.param_dict = param_dict
        params = self.__find_params__()

        self.interpolator = Krige(**params)
        self.interpolator.fit(self.X,self.y)

    def __find_params__(self):

        best_score = -np.inf
        best_params = {}

        combinations = [dict(zip(self.param_dict.keys(), valores)) for valores in itertools.product(*self.param_dict.values())]

        for c in combinations:
            cv = LeaveOneOut()
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
        return best_params


class KNNInterpolator(Interpolator):
    def __init__(self, data, param_dict='auto', verbose=False):
        """
        data -> dict com pares "coord" : "medida"
        """
        super().__init__(data, verbose=verbose)
        self.k = self.__find_k__() if param_dict == 'auto' else param_dict['k']

        if verbose and param_dict != 'auto':
            cv = LeaveOneOut()
            model = KNeighborsRegressor(n_neighbors=self.k, weights = 'distance')
            scores = cross_val_score(model, self.X, self.y, scoring='neg_root_mean_squared_error', cv=cv, n_jobs=-1)
            score = np.mean(scores)
            print(f"RMSE: {-1 * score}")

        self.interpolator = KNeighborsRegressor(n_neighbors = self.k, weights = 'distance')
        self.interpolator.fit(self.X,self.y)
        

    
    def __find_k__(self):

        best_score = -np.inf
        best_k = -1

        for k in range(1,len(self.y)):
            cv = LeaveOneOut()
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
        return best_k
    

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

    interpolator = KNNInterpolator(data, verbose=True, param_dict={"k": 1})
    print(interpolator.predict(X))
    print(100*"#")
    interpolator = KNNInterpolator(data, verbose=True, param_dict={"k": 5})
    print(interpolator.predict(X))
    print(100*"#")
    interpolator = KNNInterpolator(data, verbose=True, param_dict='auto')
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
