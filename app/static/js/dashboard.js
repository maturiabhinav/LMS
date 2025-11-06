  const sidebar = document.getElementById("sidebar");
    const menuToggle = document.getElementById("menuToggle");
    const themeToggle = document.getElementById("themeToggle");
    const logoutBtn = document.getElementById("logoutBtn");
    const body = document.body;
    const content = document.querySelector(".content");

    // Sidebar collapse toggle
    menuToggle.addEventListener("click", () => {
      sidebar.classList.toggle("collapsed");
    });

    // Dark/Light mode toggle
    themeToggle.addEventListener("click", () => {
      body.classList.toggle("dark");
      const icon = themeToggle.querySelector("i");
      icon.classList.toggle("ri-sun-line");
      icon.classList.toggle("ri-moon-line");
    });

    // Logout button click
    logoutBtn.addEventListener("click", () => {
      alert("You have logged out successfully!");
      // window.location.href = "login.html";
    });

    // Sidebar menu click logic
    const descriptions = {
      "Dashboard": "Overview of key analytics and activity insights.",
      "Course Delivery": "Manage live and recorded course content.",
      "Clients": "View and manage all clients and their details.",
      "Marketing": "Handle campaigns, promotions, and leads.",
      "Sales": "Track orders, invoices, and revenue data.",
      "Analytics": "Visualize performance and engagement metrics.",
      "Reports": "Generate and export various performance reports.",
      "Settings": "Customize system preferences and configurations.",
      "Certificates": "Issue and manage achievement certificates.",
      "Exams/Tests": "Create, assign, and review assessments.",
      "Discussions": "Engage users through posts and comments."
    };

    document.querySelectorAll(".menu-item").forEach(item => {
      item.addEventListener("click", () => {
        document.querySelectorAll(".menu-item").forEach(i => i.classList.remove("active"));
        item.classList.add("active");
        const title = item.querySelector("span").textContent.trim();

        if (title === "Clients") {
          content.innerHTML = `
            <h2>Clients List</h2>
            <table style="width:100%; border-collapse: collapse; margin-top: 15px;">
              <thead style="background-color:#082553; color:white;">
                <tr>
                  <th style="padding:10px; text-align:left;">Client ID</th>
                  <th style="padding:10px; text-align:left;">Client Name</th>
                  <th style="padding:10px; text-align:left;">Email</th>
                  <th style="padding:10px; text-align:left;">Joining Date</th>
                </tr>
              </thead>
              <tbody id="clientTableBody"></tbody>
            </table>
          `;
        } else {
          const desc = descriptions[title] || "";
          content.innerHTML = `<h2>${title}</h2><p>${desc}</p>`;
        }
      });
    });