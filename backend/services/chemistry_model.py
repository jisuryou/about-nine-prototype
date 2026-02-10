import numpy as np
import pickle
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "turn",
    "flow",
    "romantic",
    "lsm",
    "preference",
    "pitch"
]


class ChemistryModel:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = Ridge(alpha=1.0)

    def fit(self, df):
        X = df[FEATURES].values
        y = df["label"].values

        Xs = self.scaler.fit_transform(X)
        self.model.fit(Xs, y)

    def predict(self, feats: dict):
        x = np.array([[feats[f] for f in FEATURES]])
        xs = self.scaler.transform(x)
        return float(self.model.predict(xs)[0])

    def save(self, path):
        pickle.dump((self.scaler, self.model), open(path, "wb"))

    def load(self, path):
        self.scaler, self.model = pickle.load(open(path, "rb"))
