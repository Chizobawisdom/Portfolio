document.addEventListener("DOMContentLoaded", () => {
    // Select all category tab buttons and all project containers
    const tabs = document.querySelectorAll(".category-tab");
    const containers = document.querySelectorAll(".projects-container");

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            // 1. Remove the 'active' class from all tabs and containers
            tabs.forEach(t => t.classList.remove("active"));
            containers.forEach(c => c.classList.remove("active"));

            // 2. Add 'active' class to the clicked tab
            tab.classList.add("active");

            // 3. Find the matching container using the data-category attribute
            const targetCategory = tab.getAttribute("data-category");
            const targetContainer = document.querySelector(
                `.projects-container[data-category="${targetCategory}"]`
            );

            // 4. Show the matching container
            if (targetContainer) {
                targetContainer.classList.add("active");
            }
        });
    });
});