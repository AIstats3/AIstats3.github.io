document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('lineup-form');
    const tableDiv = document.getElementById('lineup-table');
    const dropdownToggle = document.getElementById('dropdownToggle');
    const gameDropdown = document.getElementById('gameDropdown');
    const selectAll = document.getElementById('selectAll');

    // Toggle dropdown
    dropdownToggle.addEventListener('click', () => {
        gameDropdown.parentElement.classList.toggle('show');
    });

    // Select all games
    selectAll.addEventListener('change', () => {
        const checkboxes = gameDropdown.querySelectorAll('input[name="game"]');
        checkboxes.forEach(cb => cb.checked = selectAll.checked);
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const selectedFiles = Array.from(document.querySelectorAll('input[name="game"]:checked'))
                                   .map(cb => cb.value);

        const response = await fetch('/lineup-stats', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ files: selectedFiles })
        });

        const data = await response.json();
        renderTable(data);
    });

    function renderTable(data) {
        if (data.length === 0) {
            tableDiv.innerHTML = '<p>No data available.</p>';
            return;
        }

        const keys = Object.keys(data[0]);
        let html = '<table><thead><tr>';
        keys.forEach(k => html += `<th>${k}</th>`);
        html += '</tr></thead><tbody>';

        data.forEach(row => {
            html += '<tr>';
            keys.forEach(k => html += `<td>${Array.isArray(row[k]) ? row[k].join(', ') : row[k]}</td>`);
            html += '</tr>';
        });

        html += '</tbody></table>';
        tableDiv.innerHTML = html;
    }
});
