var myBarChart;
const predefinedColors = [
    '#FFCD56', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
    '#FF6384', '#C45850', '#A2CC3A', '#EB3D57', '#FF8A65', '#66BB6A'
    
];

const userColorMap = {}; // Ein Objekt zum Speichern der Farben für jeden Benutzernamen
let currentColorIndex = 0;

function getColorForUser(username) {
    if (!userColorMap[username]) {
        userColorMap[username] = predefinedColors[currentColorIndex];
        currentColorIndex = (currentColorIndex + 1) % predefinedColors.length;
    }
    return userColorMap[username];
}

function updateCharts() {
    const tableRows = document.querySelectorAll('#ccvDataBody tr');
    const groupedData = {};

    tableRows.forEach(row => {
        const cells = row.querySelectorAll('td.text-center');
        const timestamp = cells[0].textContent;
        const codeLine = parseFloat(cells[1].textContent);
        const username = cells[2].textContent;

        if (!groupedData[username]) {
            groupedData[username] = {
                timestamps: [],
                codeLines: []
            };
        }

        groupedData[username].timestamps.push(timestamp);
        groupedData[username].codeLines.push(codeLine);
    });


    const allUniqueTimestamps = [...new Set([...tableRows].map(row => row.querySelector('td.text-center').textContent))]
        .map(timestamp => {
            const [time, date] = timestamp.split(' ');
            const [hour, minute] = time.split(':');
            const [day, month, year] = date.split('.').map(num => parseInt(num, 10));
            return new Date(year, month - 1, day, hour, minute); // Monat ist 0-basiert in JavaScript
        })
        .sort((a, b) => a - b) // sortiert die Date-Objekte
        .map(date => {
            const day = date.getDate().toString().padStart(2, '0');
            const month = (date.getMonth() + 1).toString().padStart(2, '0'); // +1, da Monate 0-basiert sind
            const year = date.getFullYear();
            const hour = date.getHours().toString().padStart(2, '0');
            const minute = date.getMinutes().toString().padStart(2, '0');
            return `${hour}:${minute} ${day}.${month}.${year}`; // konvertiert zurück zum ursprünglichen Format
        });


    const datasets = [];


    for (let username in groupedData) {
        let data = [];

        allUniqueTimestamps.forEach((time) => {
            let index = groupedData[username].timestamps.indexOf(time);
            data.push(index !== -1 ? groupedData[username].codeLines[index] : undefined);
        });


        let color = getColorForUser(username);
        datasets.push({
            label: `Username: ${username}`,
            data: data,
            fill: false,
            lineTension: 0,
            backgroundColor: color,
            borderColor: color,
            borderWidth: 2,
            spanGaps: true,
        });
        console.log(datasets);
    }

    new Chart("myChart", {
        type: "line",
        data: {
            labels: allUniqueTimestamps,
            datasets: datasets
        },

    });

    const userCodeLines = {};

    tableRows.forEach(row => {
        const cells = row.querySelectorAll('td.text-center');
        const codeLine = parseFloat(cells[1].textContent);
        const username = cells[2].textContent;

        if (!userCodeLines[username]) {
            userCodeLines[username] = 0;
        }
        userCodeLines[username] += codeLine;
    });

    const usernames = Object.keys(userCodeLines);
    const codeLineTotals = Object.values(userCodeLines);

    const backgroundColors = usernames.map(getColorForUser);


    new Chart("myPieChart", {
        type: 'pie',
        data: {
            labels: usernames.map(name => `${name}`),
            datasets: [{
                data: codeLineTotals,
                backgroundColor: backgroundColors
            }]
        },
        options: {
            responsive: true,
            legend: {
                position: 'top',
            },
            animation: {
                animateScale: true,
                animateRotate: true
            }
        }
    });
}

updateCharts();
updateBarChart();

/*
document.getElementById('fetch_project_data').addEventListener('click', function () {
    var projectId = document.getElementById('projectSelector').value;
    window.location.href = '/?project_id=' + projectId;
    updateBarChart();
});
*/

/*
document.getElementById('fetch_project_data').addEventListener('click', function () {
    var projectId = document.getElementById('projectSelector').value;
    fetch('/get_cd_metric_data?project_id=' + projectId) // Pfad muss Ihrem Backend-Endpoint entsprechen
        .then(response => response.json())
        .then(data => {
            // Aktualisieren   die Tabelle mit neuen Daten
            var tbody = document.getElementById('ccvDataBody');
            tbody.innerHTML = ''; // Löschen   den vorhandenen Tabelleninhalt
            // Erstellen   neue Tabellenzeilen mit den abgerufenen Daten
            data.forEach(metric => {
                var row = tbody.insertRow();
                row.innerHTML = `<td class="text-center">${metric.timestamp}</td>
                                 <td class="text-center">${metric.code_change_volume}</td>
                                 <td class="text-center">${metric.user}</td>
                                 <td class="text-center">${metric.projekt}</td>`;
            });

            // Nach dem Aktualisieren der Tabelle müssen   updateCharts erneut aufrufen
            updateCharts();
   
        })
        .catch(error => console.error('Fehler beim Abrufen der Daten:', error));
});
*/

document.getElementById('fetch_project_data').addEventListener('click', function () {
    var projectId = document.getElementById('projectSelector').value;
    // Starten   einen Fetch für jede Datenquelle
    Promise.all([
        fetch('/get_cd_metric_data?project_id=' + projectId).then(response => response.json()),
        fetch('/get_ltc_data?project_id=' + projectId).then(response => response.json()),
        fetch('/get_mttr_data?project_id=' + projectId).then(response => response.json()),
        fetch('/get_cfr_data?project_id=' + projectId).then(response => response.json()),
        // ... fügen   hier weitere fetch Aufrufe für andere Datenquellen hinzu
    ])
    .then(alldata => {
        // alldata[0] enthält die Antwort von '/get_cd_metric_data'
        // alldata[1] enthält die Antwort von '/get_ltc_data'
        // ... und so weiter für weitere Antworten

        // Aktualisieren   hier die Tabellen mit den Daten von alldata
        updateCCVTable(alldata[0]); // Eine hypothetische Funktion, um die CCV-Tabelle zu aktualisieren
        updateLTCTable(alldata[1]); // Eine hypothetische Funktion, um die LTC-Tabelle zu aktualisieren
        updateMTTRTable(alldata[2].data);
        updateMTTRDisplay(alldata[2].mttr);
        updateCFRDisplay(alldata[3]); // Ihre neue Funktion, um die CFR anzuzeigen
        // ... weitere Funktionen, um andere Tabellen zu aktualisieren

        // Nach dem Aktualisieren der Tabellen rufen   updateCharts erneut auf
        updateCharts();
    })
    .catch(error => console.error('Fehler beim Abrufen der Daten:', error));
});

// Beispiel Funktion, um die CCV Tabelle zu aktualisieren
function updateCCVTable(data) {
    var tbody = document.getElementById('ccvDataBody');
    tbody.innerHTML = ''; // Löschen   den vorhandenen Tabelleninhalt
    // Erstellen   neue Tabellenzeilen mit den abgerufenen Daten
    data.forEach(metric => {
        var row = tbody.insertRow();
        row.innerHTML = `<td class="text-center">${metric.timestamp}</td>
                         <td class="text-center">${metric.code_change_volume}</td>
                         <td class="text-center">${metric.user}</td>
                         <td class="text-center">${metric.projekt}</td>`;
    });
}
function updateLTCTable(data) {
    var tbody = document.getElementById('ltcDataBody');
    tbody.innerHTML = ''; // Löschen   den vorhandenen Tabelleninhalt
    // Erstellen   neue Tabellenzeilen mit den abgerufenen Daten
    data.forEach(metric => {
        var row = tbody.insertRow();
        row.innerHTML = `<td class="text-center">${metric.commit}</td>
                         <td class="text-center">${metric.deploy}</td>
                         <td class="text-center">${metric.ltc_value}</td>
                         <td class="text-center">${metric.deploy_successful}</td>
                         <td class="text-center">
                         <a href="/edit_ltc/${metric.id}">
                             <i class="fas fa-cog"></i>
                         </a>
                     </td>`;
    });
}
function updateMTTRTable(data) {
    var tbody = document.getElementById('mttrDataBody');
    tbody.innerHTML = ''; // Löscht den vorhandenen Tabelleninhalt
    // Erstellen   neue Tabellenzeilen mit den abgerufenen Daten
    data.forEach(metric => {
        var row = tbody.insertRow();
        row.innerHTML = `<td class="text-center">${metric.starttime}</td>
                         <td class="text-center">${metric.endtime}</td>
                         <td class="text-center">${metric.description}</td>
                         <td class="text-center">${metric.project}</td>`;
                         
    });
    
}
function updateMTTRDisplay(mttr) {
    var mttrDisplay = document.getElementById('mttrDisplay');
    mttrDisplay.innerText = mttr; // Nur der Wert von MTTR wird hier aktualisiert
}

function updateCFRDisplay(cfrData) {
    document.getElementById('failed').innerText = cfrData.failed;
    document.getElementById('total').innerText = cfrData.total;
    document.getElementById('cfrDisplay').innerText = cfrData.cfr.toFixed(2) + '%'; // Formatieren auf 2 Dezimalstellen
}
  
// Verhindert das Absenden des Formulars wenn kein Projekt ausgewählt ist
//wirkt nur auf das erste formular muss noch angepasst werden auf eine spezifische id!!!
document.getElementById("ccvForm").addEventListener("submit", function (event) {
    let ccvValue = document.getElementById("ccvInput").value;
    let selectedProject = document.getElementById("projectSelector").value;
    document.getElementById("hiddenProjectId").value = selectedProject;
    if (selectedProject === "all") {
        alert("Bitte wählen   ein Projekt aus!");
        event.preventDefault();
        return
    }
    if (!ccvValue) {
        alert("Bitte geben   Ihren CCV-Wert ein!");
        event.preventDefault();
        
    }
});
/*
document.getElementById("submit_ccv").addEventListener("submit", function(event) {
    const projectId = document.getElementById("projectSelector").value;
    document.getElementById("hiddenProjectId").value = projectId;
});
*/

document.getElementById("ltcForm").addEventListener("submit", function (event) {
    let selectedProject = document.getElementById("ltcprojectSelector").value;
    let commitDatetime = document.getElementById("commitDatetime").value;
    let deploymentDatetime = document.getElementById("deploymentDatetime").value;

    // Überprüfen, ob das Projekt "all" ist
    if (selectedProject === "all") {
        alert("Bitte wählen   ein Projekt aus!");
        event.preventDefault();
        return;  // Beendet die Funktion hier, um weitere Überprüfungen zu vermeiden
    }

    // Überprüfen, ob die Input-Felder leer sind
    if (!commitDatetime || !deploymentDatetime) {
        alert("Bitte füllen   alle Datum- und Uhrzeitfelder aus!");
        event.preventDefault();
    }
});

function updateBarChart() {

// Daten aus den data-* Attributen lesen
const chartDataElement = document.getElementById('chartData');
const months = JSON.parse(chartDataElement.getAttribute('data-months'));
const monthlyDeploymentsRaw = JSON.parse(chartDataElement.getAttribute('data-deployments'));
const monthlyDeployments = monthlyDeploymentsRaw.map(value => (value === null || value === 0) ? 0 : value);

if (myBarChart) {
    myBarChart.destroy();
}

var ctx = document.getElementById('myBarChart').getContext('2d');
myBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: months,
        datasets: [{
            label: 'Deployments pro Monat',
            data: monthlyDeployments,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                }
            }]
        },
        responsive: true,
        legend: {
            position: 'top',
        }
    }
});

}