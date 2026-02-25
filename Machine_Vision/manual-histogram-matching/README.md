
This project demonstrates manual histogram specification (histogram matching) for image enhancement.  
Instead of using high-level library functions, I implement the core math:

1. Compute histogram → PDF → CDF for the input and reference images  
2. Build a pixel mapping based on nearest CDF values  
3. Apply the mapping to transform the input image  
4. Visualise the original, reference, and matched images with their histograms

> This is a companion to my project using `skimage.exposure.match_histograms`; here I show the under-the-hood math.

---

What This Project Shows
- How histogram matching works mathematically:
  - Histogram (`np.bincount`)
  - PDF (normalise counts)
  - CDF (cumulative sum)
  - Mapping via minimal CDF difference (`argmin`)
- Contrast enhancement by statistically aligning tone distributions
- Clear visualisation of before/after intensity distributions


