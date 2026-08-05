document.addEventListener("DOMContentLoaded", () => {
  // Helper function to update the wrapper height to match the current slide
  function updateWrapperHeight(block, slideIndex) {
    const wrapper = block.querySelector(".carousel-wrapper");
    const slides = block.querySelectorAll(".carousel-slide");
    
    if (wrapper && slides[slideIndex]) {
      const activeSlideHeight = slides[slideIndex].offsetHeight;
      wrapper.style.height = `${activeSlideHeight}px`;
    }
  }

  // --- Category Tabs Switching ---
  const categoryTabs = document.querySelectorAll(".category-tab");
  const carouselBlocks = document.querySelectorAll(".carousel-block");

  categoryTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const selectedCategory = tab.getAttribute("data-category");

      categoryTabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");

      carouselBlocks.forEach((block) => {
        if (block.getAttribute("data-category") === selectedCategory) {
          block.classList.add("active");
          
          // Re-recalculate height when tab becomes visible
          const activeIndex = block.dataset.currentIndex ? parseInt(block.dataset.currentIndex) : 0;
          updateWrapperHeight(block, activeIndex);
        } else {
          block.classList.remove("active");
        }
      });
    });
  });

  // --- Carousel Slide Mechanism ---
  carouselBlocks.forEach((block) => {
    const track = block.querySelector(".carousel-track");
    const slides = block.querySelectorAll(".carousel-slide");
    const prevBtn = block.querySelector('.carousel-btn[data-dir="-1"]');
    const nextBtn = block.querySelector('.carousel-btn[data-dir="1"]');
    const dots = block.querySelectorAll(".carousel-dot");
    const counter = block.querySelector(".carousel-counter");

    if (!slides.length) return;

    let currentIndex = 0;
    const totalSlides = slides.length;

    function updateCarousel(index) {
      currentIndex = index;
      block.dataset.currentIndex = currentIndex; // Store index for tab switches
      
      track.style.transform = `translateX(-${currentIndex * 100}%)`;

      dots.forEach((dot, idx) => {
        dot.classList.toggle("active", idx === currentIndex);
      });

      if (counter) {
        counter.textContent = `${currentIndex + 1} / ${totalSlides}`;
      }

      // Update height whenever the slide updates
      updateWrapperHeight(block, currentIndex);
    }

    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        const newIndex = (currentIndex - 1 + totalSlides) % totalSlides;
        updateCarousel(newIndex);
      });
    }

    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        const newIndex = (currentIndex + 1) % totalSlides;
        updateCarousel(newIndex);
      });
    }

    dots.forEach((dot, idx) => {
      dot.addEventListener("click", () => {
        updateCarousel(idx);
      });
    });

    // Initialize height on initial page load
    updateCarousel(0);
  });
});