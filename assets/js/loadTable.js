document.addEventListener("DOMContentLoaded", function () {
  fetch('/assets/data/next_shot_stats.csv')
      .then(response => response.text())
      .then(data => {
          const rows = data.trim().split("\n").map(row => row.split(","));
          const table = document.getElementById("csvTable");
          const thead = table.querySelector("thead");
          const tbody = table.querySelector("tbody");

          // Populate table headers
          const headerRow = document.createElement("tr");
          rows[0].forEach(headerText => {
              const th = document.createElement("th");
              th.textContent = headerText.trim();
              headerRow.appendChild(th);
          });
          thead.appendChild(headerRow);

          // Populate table rows
          rows.slice(1).forEach(row => {
              const tr = document.createElement("tr");
              row.forEach(cellText => {
                  const td = document.createElement("td");
                  td.textContent = cellText.trim();
                  tr.appendChild(td);
              });
              tbody.appendChild(tr);
          });
      })
      .catch(error => console.error("Error loading CSV:", error));
});