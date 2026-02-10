import os
import numpy as np
import pickle
from pathlib import Path
from firebase_admin import storage

from backend.services.firestore import get_firestore
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
        self._loaded = False
        self._version = "baseline"

    def fit(self, df):
        if isinstance(df, list):
            X = []
            y = []
            for row in df:
                X.append([row.get(k, 0) for k in FEATURES])
                y.append(row.get("label", 0))
            X = np.array(X, dtype=float)
            y = np.array(y, dtype=float)
        else:
            X = df[FEATURES].values
            y = df["label"].values

        Xs = self.scaler.fit_transform(X)
        self.model.fit(Xs, y)

    def predict(self, feats: dict):
        values = []
        for key in FEATURES:
            if key in feats:
                values.append(feats[key])
                continue
            # allow newer feature keys from analysis_service
            if key == "turn":
                values.append(feats.get("turn_taking", 0))
            elif key == "flow":
                values.append(feats.get("flow_continuity", 0))
            elif key == "romantic":
                values.append(feats.get("romantic_intent", 0))
            elif key == "lsm":
                values.append(feats.get("language_style_ma", 0))
            elif key == "preference":
                values.append(feats.get("preference_sync", 0))
            elif key == "pitch":
                values.append(feats.get("voice_pitch", feats.get("voice pitch", 0)))
            else:
                values.append(0)

        x = np.array([values], dtype=float)

        if not self._loaded:
            # Fallback: average raw feature scores when model file is missing.
            return float(np.mean(x))

        xs = self.scaler.transform(x)
        return float(self.model.predict(xs)[0])

    def save(self, path):
        pickle.dump((self.scaler, self.model, self._version), open(path, "wb"))

    def load(self, path):
        try:
            local_path = path
            if isinstance(path, str) and path.startswith("gs://"):
                local_path = self._download_from_gcs(path)
            payload = pickle.load(open(local_path, "rb"))
            if isinstance(payload, tuple) and len(payload) == 3:
                self.scaler, self.model, self._version = payload
            else:
                self.scaler, self.model = payload
                self._version = "legacy"
            self._loaded = True
        except FileNotFoundError:
            print(f"⚠️ chemistry model not found at {path}; using fallback scoring")
            self._loaded = False
            self._version = "baseline"

    def set_version(self, version: str):
        self._version = version

    def version(self):
        return self._version

    def _download_from_gcs(self, gs_path: str) -> str:
        if not gs_path.startswith("gs://"):
            return gs_path

        # Ensure Firebase app is initialized (ADC on GCP or service account)
        get_firestore()

        parts = gs_path.replace("gs://", "", 1).split("/", 1)
        bucket_name = parts[0]
        blob_path = parts[1] if len(parts) > 1 else ""

        if not bucket_name or not blob_path:
            raise FileNotFoundError(f"Invalid GCS path: {gs_path}")

        bucket = storage.bucket(bucket_name)
        blob = bucket.blob(blob_path)

        local_dir = Path("/tmp/chemistry_models")
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = local_dir / os.path.basename(blob_path)

        blob.download_to_filename(str(local_path))
        return str(local_path)
