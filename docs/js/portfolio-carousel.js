document.addEventListener("DOMContentLoaded", () => {
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
      track.style.transform = `translateX(-${currentIndex * 100}%)`;

      dots.forEach((dot, idx) => {
        dot.classList.toggle("active", idx === currentIndex);
      });

      if (counter) {
        counter.textContent = `${currentIndex + 1} / ${totalSlides}`;
      }
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
  });
});