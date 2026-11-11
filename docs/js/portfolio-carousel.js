document.addEventListener("DOMContentLoaded", () => {
    
    /* ==========================================
       1. PROJECT CATEGORY TABS
       ========================================== */
    const tabs = document.querySelectorAll(".category-tab");
    const containers = document.querySelectorAll(".projects-container");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            // Remove active class from all tabs and containers
            tabs.forEach(t => t.classList.remove("active"));
            containers.forEach(c => c.classList.remove("active"));

            // Add active class to the clicked tab
            tab.classList.add("active");

            // Show the matching container
            const targetCategory = tab.getAttribute("data-category");
            const targetContainer = document.querySelector(
                `.projects-container[data-category="${targetCategory}"]`
            );

            if (targetContainer) {
                targetContainer.classList.add("active");
            }
        });
    });

    /* ==========================================
       2. STICKY NAV SCROLL SPY
       ========================================== */
    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll("nav a");
    let isScrolling = false;

    const updateActiveLink = () => {
        let current = "";
        
        // Find the current section
        sections.forEach((section) => {
            const sectionTop = section.offsetTop;
            // 150px offset accounts for the sticky navbar height
            if (window.scrollY >= sectionTop - 150) {
                current = section.getAttribute("id");
            }
        });

        // Update the navigation links
        navLinks.forEach((link) => {
            link.classList.remove("active");
            
            // If the link matches the current section, make it active
            // Or if we are at the very top, make "Home" active
            if (link.getAttribute("href") === `#${current}` || 
               (window.scrollY === 0 && (link.getAttribute("href") === "#" || link.getAttribute("href") === "#home"))) {
                link.classList.add("active");
            }
        });
        
        isScrolling = false;
    };

    window.addEventListener("scroll", () => {
        // Use requestAnimationFrame for better scrolling performance
        if (!isScrolling) {
            window.requestAnimationFrame(updateActiveLink);
            isScrolling = true;
        }
    });
    
    // Run once on load to set the initial active state
    updateActiveLink();
});