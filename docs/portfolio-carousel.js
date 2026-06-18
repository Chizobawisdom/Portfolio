/**
 * portfolio-carousel.js
 * Drives all category-tab + carousel-block + carousel-track groups on the page.
 */
(function () {
  'use strict';

  /* ── helper: initialise one carousel block ── */
  function initCarousel(block) {
    const track  = block.querySelector('.carousel-track');
    const slides = Array.from(block.querySelectorAll('.carousel-slide'));
    const prev   = block.querySelector('.carousel-btn[data-dir="-1"]');
    const next   = block.querySelector('.carousel-btn[data-dir="1"]');
    const dots   = Array.from(block.querySelectorAll('.carousel-dot'));
    const counter= block.querySelector('.carousel-counter');
    const total  = slides.length;
    let   current = 0;

    function go(index) {
      current = Math.max(0, Math.min(index, total - 1));
      track.style.transform = `translateX(-${current * 100}%)`;
      dots.forEach((d, i) => d.classList.toggle('active', i === current));
      if (counter) counter.textContent = `${current + 1} / ${total}`;
      if (prev) prev.disabled = current === 0;
      if (next) next.disabled = current === total - 1;
    }

    if (prev) prev.addEventListener('click', () => go(current - 1));
    if (next) next.addEventListener('click', () => go(current + 1));
    dots.forEach((d, i) => d.addEventListener('click', () => go(i)));

    /* swipe / drag support */
    let startX = null;
    track.addEventListener('touchstart', e => { startX = e.touches[0].clientX; }, { passive: true });
    track.addEventListener('touchend',   e => {
      if (startX === null) return;
      const dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 40) go(current + (dx < 0 ? 1 : -1));
      startX = null;
    });

    go(0); // initialise to first slide
  }

  /* ── wire category tabs to carousel blocks ── */
  function initSection(section) {
    const tabs   = Array.from(section.querySelectorAll('.category-tab'));
    const blocks = Array.from(section.querySelectorAll('.carousel-block'));

    function showBlock(id) {
      tabs.forEach(t   => t.classList.toggle('active', t.dataset.category === id));
      blocks.forEach(b => b.classList.toggle('active', b.dataset.category === id));
    }

    tabs.forEach(tab => {
      tab.addEventListener('click', () => showBlock(tab.dataset.category));
    });

    /* show first category on load */
    if (tabs.length) showBlock(tabs[0].dataset.category);

    /* initialise every carousel inside this section */
    blocks.forEach(initCarousel);
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.carousel-section').forEach(initSection);
  });
})();
