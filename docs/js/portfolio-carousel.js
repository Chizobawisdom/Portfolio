document.addEventListener("DOMContentLoaded", () => {
  // ─── CATEGORY TAB SWITCHING ───
  const categoryTabs = document.querySelectorAll(".category-tab");
  const carouselBlocks = document.querySelectorAll(".carousel-block");

  categoryTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const selectedCategory = tab.getAttribute("data-category");

      // Update active tab button
      categoryTabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");

      // Show matching category block, hide others
      carouselBlocks.forEach((block) => {
        if (block.getAttribute("data-category") === selectedCategory) {
          block.classList.add("active");
        } else {
          block.classList.remove("active");
        }
      });
    });
  });

  // ─── CAROUSEL SLIDER LOGIC ───
  carouselBlocks.forEach((block) => {
    const track = block.querySelector(".carousel-track");
    const slides = block.querySelectorAll(".carousel-slide");
    const prevBtn = block.querySelector('.carousel-btn[data-dir="-1"]');
    const nextBtn = block.querySelector('.carousel-btn[data-dir="1"]');
    const dots = block.querySelectorAll(".carousel-dot");
    const counter = block.querySelector(".carousel-counter");

    // Skip initializing carousels with single or zero slides
    if (!slides.length || slides.length <= 1) return;

    let currentIndex = 0;
    const totalSlides = slides.length;

    function updateCarousel(index) {
      currentIndex = index;

      // Translate track to slide position
      track.style.transform = `translateX(-${currentIndex * 100}%)`;
      track.style.transition = "transform 0.3s ease-in-out";

      // Update active dot indicator
      dots.forEach((dot, idx) => {
        dot.classList.toggle("active", idx === currentIndex);
      });

      // Update text counter (e.g., "1 / 4")
      if (counter) {
        counter.textContent = `${currentIndex + 1} / ${totalSlides}`;
      }
    }

    // Previous Button Click
    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        const newIndex = (currentIndex - 1 + totalSlides) % totalSlides;
        updateCarousel(newIndex);
      });
    }

    // Next Button Click
    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        const newIndex = (currentIndex + 1) % totalSlides;
        updateCarousel(newIndex);
      });
    }

    // Dot Navigation Clicks
    dots.forEach((dot, idx) => {
      dot.addEventListener("click", () => {
        updateCarousel(idx);
      });
    });
  });
});