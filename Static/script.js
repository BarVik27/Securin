document.addEventListener("DOMContentLoaded", function () {
    const resultsPerPage = document.getElementById("resultsPerPage");
    resultsPerPage.addEventListener("change", applyFilters);

    let currentPage = 1;
    let totalPages = 1;

    
    function applyFilters() {
        const cveId = document.getElementById("cveIdFilter").value;
        const cvss = document.getElementById("cvssFilter").value;
        const date = document.getElementById("dateFilter").value;
        const limit = resultsPerPage.value;

        fetchCVEData(currentPage, limit, cveId, cvss, date);
    }

    
    function fetchCVEData(page, limit, cveId = "", cvss = "", date = "") {
        const url = `/api/cves?page=${page}&limit=${limit}&cveId=${cveId}&cvss=${cvss}&date=${date}`;

        fetch(url)
            .then((response) => response.json())
            .then((data) => {
                let tbody = document.getElementById("cveTableBody");
                tbody.innerHTML = "";

                
                document.getElementById("totalRecords").innerText = data.total;
                totalPages = Math.ceil(data.total / limit);
                document.getElementById("pageInfo").innerText = `Page ${currentPage} of ${totalPages}`;

                
                data.results.forEach((cve) => {
                    let row = `<tr onclick="viewCVE('${cve.cve_id}')">
                        <td>${cve.cve_id}</td>
                        <td>${cve.description}</td>
                        <td>${cve.published_date}</td>
                        <td>${cve.severity}</td>
                    </tr>`;
                    tbody.innerHTML += row;
                });
            })
            .catch((error) => console.error("Error fetching CVEs:", error));
    }

    
    window.changePage = function (page) {
        if (page < 1 || page > totalPages) return;
        currentPage = page;
        applyFilters();
    };

    
    window.viewCVE = function (cveID) {
        window.location.href = `/cves/cve-${cveID}`;
    };

   
    applyFilters();
});
