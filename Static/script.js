document.addEventListener("DOMContentLoaded", function() {
    const resultsPerPage = document.getElementById("resultsPerPage");
    resultsPerPage.addEventListener("change", fetchCVEData);

    function fetchCVEData() {
        let limit = resultsPerPage.value;
        fetch(`/api/cves?limit=${limit}`)
            .then(response => response.json())
            .then(data => {
                let tbody = document.getElementById("cveTableBody");
                tbody.innerHTML = "";
                document.getElementById("totalRecords").innerText = data.total;

                data.results.forEach(cve => {
                    let row = `<tr onclick="viewCVE('${cve.cve_id}')">
                        <td>${cve.cve_id}</td>
                        <td>${cve.description}</td>
                        <td>${cve.published_date}</td>
                        <td>${cve.severity}</td>
                    </tr>`;
                    tbody.innerHTML += row;
                });
            })
            .catch(error => console.error("Error fetching CVEs:", error));
    }

    window.viewCVE = function(cveID) {
        window.location.href = `/cves/cve-${cveID}`;
    };

    fetchCVEData(); // Load data initially
});
