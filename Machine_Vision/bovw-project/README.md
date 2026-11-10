# BoVW Scene Classification (MIT Split)
This project implements a Bag of Visual Words (BoVW) pipeline for scene classification. It replicates the best configuration from the paper “Image Classification with Classic and Deep Learning Techniques” (arXiv:2105.04895). The pipeline uses dense SIFT descriptors, a spatial pyramid representation, and an SVM classifier to categorize images into eight scene classes

---

## Dataset
The project uses the MIT split dataset, which contains 8 scene categories:
 - coast
 - forest
 - highway
 - insidecity
 - mountain
 - opencountry
 - street
 - tallbuilding

### Pipeline Steps
 #### Dense SIFT Extraction
  - Images are resized to 256×256.
  - Keypoints are sampled on a regular grid (step = 8 px, keypoint size = 16 px)
  - Each keypoint yields a 128‑dimensional SIFT descriptor.
 #### Codebook Construction
  - Descriptors from the training set are collected (sub‑sampled to 500 000 if necessary).
  - MiniBatchKMeans is used to build a visual vocabulary of 512 words
 #### Spatial Pyramid Encoding
  - A horizontal pyramid (level 1) is applied: the whole image plus three horizontal strips.
  - Each region contributes a histogram of visual‑word occurrences; histograms are L2‑normalized and concatenated.
 #### Feature Post‑processing
  - The concatenated histogram is passed through StandardScaler and PCA (64 components)
 #### Classification
  - An SVM with an RBF kernel (C=1.0, gamma='scale') is trained on the reduced features
 #### Evaluation
  - 8‑fold stratified cross‑validation on the training set
  - Final model is fitted on the full training set and evaluated on the held‑out test set
  - Accuracy and a classification report are printed

### Requirements
 - Python 3.8+
 - OpenCV (opencv-python)
 - scikit-learn
 - NumPy
 - joblib
 - Matplotlib (optional, for visualisation)

Install the main dependencies usiing pip: 
pip install opencv-python scikit-learn numpy joblib matplotlib

## Results
The pipeline reports cross‑validation accuracy and test accuracy along with a per‑class classification report. For the exact numbers obtained in this project, refer to the output cells in notebook.ipynb or run the script on the MIT split dataset.

### References
 - Lorente, Ò., Riera, I., & Rana, A. (2021, May 11). Image Classification with Classic and Deep Learning Techniques. arXiv.org. https://arxiv.org/abs/2105.04895
 - MIT split dataset – scene classification benchmark.