
This project demonstrates the use of histogram specification (also called histogram matching) to enhance the contrast of a dark image by matching its intensity distribution to that of a high‑contrast reference image.

This is a common image-processing technique used in:
- image enhancement  
- medical imaging  
- computer vision preprocessing  
- photography correction  
- standardising datasets for ML pipelines  

---

What This Project Does

- Loads two colour images:  
  (1) a dark, low‑contrast image  
  (2) a bright, high‑contrast reference image  
- Converts images from BGR → RGB (OpenCV default → normal format)
- Applies histogram matching using  
  `skimage.exposure.match_histograms`
- Produces three outputs:
  - Original dark image  
  - Reference image  
  - Histogram‑matched enhanced image  
- Plots:
  - Side‑by‑side visual comparison  
  - Intensity histograms for 'R, G, and B channels'  
  - Cumulative distribution functions (CDFs)  

This project demonstrates an applied understanding of contrast manipulation, colour channel distribution, image statistics, and visualisation.

