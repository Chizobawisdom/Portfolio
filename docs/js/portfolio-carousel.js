document.addEventListener("DOMContentLoaded", () => {
    const tabs = document.querySelectorAll(".category-tab");
    const containers = document.querySelectorAll(".projects-container");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            // 1. Remove active class from all tabs and containers
            tabs.forEach(t => t.classList.remove("active"));
            containers.forEach(c => c.classList.remove("active"));

            // 2. Add active class to clicked tab
            tab.classList.add("active");

            // 3. Find the matching container and make it active
            const targetCategory = tab.getAttribute("data-category");
            const targetContainer = document.querySelector(`.projects-container[data-category="${targetCategory}"]`);
            
            if (targetContainer) {
                targetContainer.classList.add("active");
            }
        });
    });
});