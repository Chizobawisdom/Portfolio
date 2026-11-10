"""
Bag of Visual Words classifier replicating the best configuration from
"Image Classification with Classic and Deep Learning Techniques" (arXiv:2105.04895).

Usage:
  python bovw_pipeline.py --data_root path/to/dataset
"""
import argparse
import os
from pathlib import Path

import cv2
import numpy as np
from joblib import Parallel, delayed
from sklearn.cluster import MiniBatchKMeans
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# ----------------------------- Hyperparameters ------------------------------
IMG_SIZE = 256        # paper images are 256x256; all images are resized to this
STEP = 8              # dense grid spacing in pixels (smaller = more keypoints = better in paper)
KP_SIZE = 16          # SIFT keypoint (patch) size in pixels
CODEBOOK_SIZE = 512   # best trade-off in paper (Fig. 7)
PYRAMID_LEVEL = 1     # horizontal pyramid: level 0 -> 1 hist, level 1 -> 1 + 3 hists
PCA_COMPONENTS = 64   # paper uses 64 (Fig. 8)
TEST_SIZE = 0.3       # paper: 70/30 split
CV_FOLDS = 8          # paper: 8-fold stratified CV
SEED = 42
MAX_DESC_FOR_KMEANS = 500_000  # subsample descriptors for codebook fitting (speed)
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


# ------------------------------- Data loading -------------------------------
def load_dataset(data_root):
    """Return list of image paths and list of integer labels, plus class names."""
    root = Path(data_root)
    class_names = sorted(d.name for d in root.iterdir() if d.is_dir())
    paths, labels = [], []
    for idx, cname in enumerate(class_names):
        for p in sorted((root / cname).iterdir()):
            if p.suffix.lower() in IMG_EXTS:
                paths.append(str(p))
                labels.append(idx)
    return paths, np.array(labels), class_names


# --------------------------- Dense SIFT extraction ---------------------------
def dense_keypoints(size=IMG_SIZE, step=STEP, kp_size=KP_SIZE):
    half = kp_size // 2
    return [
        cv2.KeyPoint(float(x), float(y), kp_size)
        for y in range(half, size - half + 1, step)
        for x in range(half, size - half + 1, step)
    ]


def extract_dense_sift(path):
    """Return (descriptors [N,128], y-coordinates [N]) for one image."""
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise IOError(f"Could not read image: {path}")
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    sift = cv2.SIFT_create()
    kps = dense_keypoints()
    kps, desc = sift.compute(img, kps)
    ys = np.array([kp.pt[1] for kp in kps], dtype=np.float32)
    return desc.astype(np.float32), ys


def extract_all(paths, n_jobs=-1):
    results = Parallel(n_jobs=n_jobs)(delayed(extract_dense_sift)(p) for p in paths)
    descs = [r[0] for r in results]
    ys = [r[1] for r in results]
    return descs, ys


# ------------------------------- Codebook -----------------------------------
def build_codebook(train_descs, k=CODEBOOK_SIZE, max_desc=MAX_DESC_FOR_KMEANS):
    all_desc = np.vstack(train_descs)
    if len(all_desc) > max_desc:
        rng = np.random.RandomState(SEED)
        all_desc = all_desc[rng.choice(len(all_desc), max_desc, replace=False)]
    kmeans = MiniBatchKMeans(
        n_clusters=k, batch_size=10_000, n_init=3, random_state=SEED, verbose=0
    )
    kmeans.fit(all_desc)
    return kmeans


# --------------------- Spatial pyramid histograms (horizontal) ---------------
def pyramid_regions(level, size=IMG_SIZE):
    """List of (y_start, y_end) regions. Level 0: whole image; level 1: + 3 strips."""
    regions = [(0, size)]
    if level >= 1:
        edges = np.linspace(0, size, 4)
        regions += [(edges[i], edges[i + 1]) for i in range(3)]
    if level >= 2:
        edges = np.linspace(0, size, 7)
        regions += [(edges[i], edges[i + 1]) for i in range(6)]
    return regions


def l2_normalize(h):
    n = np.linalg.norm(h)
    return h / n if n > 0 else h


def encode_image(desc, ys, kmeans, level=PYRAMID_LEVEL):
    words = kmeans.predict(desc)
    feats = []
    for y0, y1 in pyramid_regions(level):
        mask = (ys >= y0) & (ys < y1) if y1 < IMG_SIZE else (ys >= y0)
        hist = np.bincount(words[mask], minlength=kmeans.n_clusters).astype(np.float32)
        feats.append(l2_normalize(hist))  # every region contributes equally (paper, Sec. IV-D)
    return np.concatenate(feats)


def encode_all(descs, ys, kmeans, level=PYRAMID_LEVEL):
    return np.vstack([encode_image(d, y, kmeans, level) for d, y in zip(descs, ys)])


# ----------------------------------- Main -----------------------------------
def main(data_root):
    root = Path(data_root)
    if (root / "train").is_dir() and (root / "test").is_dir():
        # Dataset already split: use the provided train/test folders as they are
        tr_paths, y_tr, class_names = load_dataset(root / "train")
        te_paths, y_te, te_class_names = load_dataset(root / "test")
        assert class_names == te_class_names, "train/ and test/ have different class folders"
        print(f"Train: {len(tr_paths)} images | Test: {len(te_paths)} images")
        print(f"Classes: {class_names}")
        print("Train class counts:", dict(zip(class_names, np.bincount(y_tr))))
    else:
        # Single folder with class subfolders: create a stratified 70/30 split
        paths, labels, class_names = load_dataset(data_root)
        print(f"Found {len(paths)} images in {len(class_names)} classes: {class_names}")
        print("Class counts:", dict(zip(class_names, np.bincount(labels))))
        tr_paths, te_paths, y_tr, y_te = train_test_split(
            paths, labels, test_size=TEST_SIZE, stratify=labels, random_state=SEED
        )

    print("Extracting dense SIFT (train)...")
    tr_desc, tr_ys = extract_all(tr_paths)
    print("Extracting dense SIFT (test)...")
    te_desc, te_ys = extract_all(te_paths)

    print(f"Fitting codebook (k={CODEBOOK_SIZE}) on training descriptors only...")
    kmeans = build_codebook(tr_desc)

    print("Encoding images with spatial pyramid histograms...")
    X_tr = encode_all(tr_desc, tr_ys, kmeans)
    X_te = encode_all(te_desc, te_ys, kmeans)
    print("Feature dimension before PCA:", X_tr.shape[1])

    n_comp = min(PCA_COMPONENTS, X_tr.shape[0], X_tr.shape[1])
    clf = make_pipeline(
        StandardScaler(),
        PCA(n_components=n_comp, random_state=SEED),
        SVC(kernel="rbf", C=1.0, gamma="scale"),
    )

    print(f"Running {CV_FOLDS}-fold stratified CV on the training set...")
    skf = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=SEED)
    scores = cross_val_score(clf, X_tr, y_tr, cv=skf, n_jobs=-1)
    print(f"CV accuracy: {scores.mean():.3f} +/- {scores.std():.3f}")

    print("Fitting on full training set and evaluating on the test set...")
    clf.fit(X_tr, y_tr)
    y_pred = clf.predict(X_te)
    print(f"Test accuracy: {accuracy_score(y_te, y_pred):.3f}")
    print(classification_report(y_te, y_pred, target_names=class_names))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_root", required=True, help="Folder with one subfolder per class")
    args = ap.parse_args()
    main(args.data_root)