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
       2. STICKY NAV SCROLL SPY & BACK TO TOP BUTTON
       ========================================== */
    const sections = document.querySelectorAll("section[id]");
    const navLinks = document.querySelectorAll("nav a");
    const mybutton = document.getElementById("myBtn"); // Back to top button
    let isScrolling = false;

    const handleScroll = () => {
        // --- A. Handle Navbar Highlighting ---
        let current = "";
        sections.forEach((section) => {
            const sectionTop = section.offsetTop;
            if (window.scrollY >= sectionTop - 150) {
                current = section.getAttribute("id");
            }
        });

        navLinks.forEach((link) => {
            link.classList.remove("active");
            if (link.getAttribute("href") === `#${current}` || 
               (window.scrollY === 0 && (link.getAttribute("href") === "#" || link.getAttribute("href") === "#home"))) {
                link.classList.add("active");
            }
        });

        // --- B. Handle Back to Top Button Visibility ---
        if (mybutton) {
            const scrollTop = document.body.scrollTop || document.documentElement.scrollTop;
            if (scrollTop > 20) {
                mybutton.style.display = "block";
            } else {
                mybutton.style.display = "none";
            }
        }
        
        isScrolling = false;
    };

    // Listen for scroll events
    window.addEventListener("scroll", () => {
        if (!isScrolling) {
            window.requestAnimationFrame(handleScroll);
            isScrolling = true;
        }
    });
    
    // Run once on load to set the initial states
    handleScroll();

    /* ==========================================
       3. BACK TO TOP CLICK FUNCTION
       ========================================== */
    // We attach this to the window object so the HTML 'onclick="topFunction()"' can find it
    window.topFunction = () => {
        // Using smooth behavior for a nicer scroll
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    };
});