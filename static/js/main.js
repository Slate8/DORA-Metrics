var myBarChart;
const predefinedColors = [
    '#216b73', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
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

var lineCharts = [];

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

    const lineChartElements = document.getElementsByClassName('lineChart');
    for (let i = 0; i < lineChartElements.length; i++) {
        if (lineCharts[i]) {
            // Aktualisiere vorhandene Chart-Instanz
            lineCharts[i].data.labels = allUniqueTimestamps;
            lineCharts[i].data.datasets = datasets;
            lineCharts[i].update();
        } else {
            // Erstelle eine neue Chart-Instanz
            lineCharts[i] = new Chart(lineChartElements[i].getContext('2d'), {
                type: "line",
                data: {
                    labels: allUniqueTimestamps,
                    datasets: datasets
                }
            });
        }
    }


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
//Alte Abruffunktion zum befüllen der Charts und Tabellen
/*updateCharts();
updateBarChart();
*/


document.getElementById('fetch_project_data').addEventListener('click', function () {
    var projectId = document.getElementById('projectSelector').value;
    // Starten   einen Fetch für jede Datenquelle
    Promise.all([
        fetch('/get_cd_metric_data?project_id=' + projectId).then(response => response.json()),
        fetch('/get_ltc_data?project_id=' + projectId).then(response => response.json()),
        fetch('/get_mttr_data?project_id=' + projectId).then(response => response.json()),
        fetch('/get_cfr_data?project_id=' + projectId).then(response => response.json()),
        fetch('/get_df_data?project_id=' + projectId).then(response => response.json()),
        // ... fügen   hier weitere fetch Aufrufe für andere Datenquellen hinzu
    ])
        .then(alldata => {
            // alldata[0] enthält die Antwort von '/get_cd_metric_data'
            // alldata[1] enthält die Antwort von '/get_ltc_data'
            // ... und so weiter für weitere Antworten

            // Aktualisieren   hier die Tabellen mit den Daten von alldata
            updateCCVTable(alldata[0]); // Eine  Funktion, um die CCV-Tabelle zu aktualisieren
            updateLTCTable(alldata[1]); // Eine  Funktion, um die LTC-Tabelle zu aktualisieren
            const ltcData = alldata[1]; 
            updateLTCChart(alldata[1]);
            updateLTCDashboard(ltcData);

            updateMTTRTable(alldata[2].data);
            updateMTTRValue(alldata[2].mttr);
            updateMTTRDisplay(alldata[2].data);
            updateCFRDisplay(alldata[3]); //  neue Funktion, um die CFR anzuzeigen
            const cfr = alldata[3].cfr;
            updateCFRChart(cfr);
            updateCFRDashboard(cfr);
            updateDFChart(alldata[4]);
            const df = alldata[4].df;
            updateDFDashboard(df);
            document.getElementById('dfValue').textContent = alldata[4].df;
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
                         <td class="text-center">${metric.projekt}</td>
                         <td class="text-center">
                         <a href="/edit_ccv/${metric.id}">
                             <i class="fas fa-cog"></i>
                         </a>
                     </td>`
                         ;
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
function updateMTTRValue(mttr) {
    var mttrDisplay = document.getElementById('mttrDisplay');
    mttrDisplay.innerText = mttr; // Nur der Wert von MTTR wird hier aktualisiert
    
}

// Array, um die Chart-Instanzen zu speichern
let mttrCharts = [];

function updateMTTRDisplay(mttrData) {
    const chartElements = document.getElementsByClassName('mttrChart');
    
    const projectNames = [...new Set(mttrData.map(incident => incident.project))];
    const labels = [...new Set(mttrData.map(incident => incident.starttime))];

    // Initialisiere die Datenstruktur für jedes Projekt mit Nullen
    const projectData = projectNames.reduce((acc, projectName) => {
        acc[projectName] = labels.map(() => null); // Starte mit null für jede Zeitmarke
        return acc;
    }, {});

    // Fülle die tatsächlichen Daten für jedes Projekt
    mttrData.forEach(incident => {
        const projectName = incident.project;
        const labelIndex = labels.indexOf(incident.starttime);
        const start = parseDate(incident.starttime);
        const end = parseDate(incident.endtime);
        const duration = (end - start) / 1000 / 3600; // Dauer in Stunden
        projectData[projectName][labelIndex] = parseFloat(duration.toFixed(2));
    });

    // Erstelle ein Dataset für jedes Projekt
    const datasets = projectNames.map((projectName, index) => {
        const color = predefinedColors[index % predefinedColors.length];
        return {
            label: projectName,
            data: projectData[projectName],
            backgroundColor: '#fea900',
            borderColor: '#fea900',
            borderWidth: 1
        };
    });

    // Iteriere über alle Chart-Elemente und erstelle oder aktualisiere das Diagramm
    for (let i = 0; i < chartElements.length; i++) {
        const ctx = chartElements[i].getContext('2d');

        if (mttrCharts[i]) {
            // Aktualisiere das vorhandene Diagramm
            mttrCharts[i].data.labels = labels;
            mttrCharts[i].data.datasets = datasets;
            mttrCharts[i].update();
        } else {
            // Erstelle ein neues Diagramm
            mttrCharts[i] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: datasets
                },
                options: {
                    responsive: false,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Dauer (Stunden)'
                            }
                        }
                    },
                    plugins: {
                        title: {
                            display: true,
                            text: `MTTR`
                        }
                    }
                }
            });
        }
    }
}

// Funktion zum Erstellen des CFR Balkendiagramms
function updateCFRDashboard(cfr) {
    const chartElements = document.getElementsByClassName('cfrChart');

    for (let i = 0; i < chartElements.length; i++) {
        const ctx = chartElements[i].getContext('2d');

        // Überprüfen, ob bereits eine Chart-Instanz für dieses Canvas-Element existiert
        if (window['cfrChart' + i]) {
            // Aktualisiere das vorhandene Diagramm
            window['cfrChart' + i].data.datasets[0].data = [cfr];
            window['cfrChart' + i].update();
        } else {
            // Erstelle ein neues Diagramm
            window['cfrChart' + i] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Change Failure Rate'],
                    datasets: [{
                        label: 'CFR (%)',
                        data: [cfr],
                        backgroundColor: '#800080',
                        borderColor: '#800080',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 30  // Skala bis 30% festgelegt
                        }
                    }
                }
            });
        }
    }
}

function updateDFDashboard(dfValue) {
    const chartElements = document.getElementsByClassName('dfChart');

    for (let i = 0; i < chartElements.length; i++) {
        const ctx = chartElements[i].getContext('2d');

        // Überprüfen, ob bereits eine Chart-Instanz für dieses Canvas-Element existiert
        if (window['dfChart' + i]) {
            // Aktualisiere das vorhandene Diagramm
            window['dfChart' + i].data.datasets[0].data = [dfValue];
            window['dfChart' + i].update();
        } else {
            // Erstelle ein neues Diagramm
            window['dfChart' + i] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Deployment Frequency'],
                    datasets: [{
                        label: 'DF (Deployments pro Monat)',
                        data: [dfValue],
                        backgroundColor: '#87cde9',
                        borderColor: '#87cde9',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100  // Angenommener maximaler Wert für DF
                        }
                    }
                }
            });
        }
    }
}

function updateLTCDashboard(ltcData) {
    const ltcChartElements = document.getElementsByClassName('ltcChart');

    for (let i = 0; i < ltcChartElements.length; i++) {
        const ctx = ltcChartElements[i].getContext('2d');

        // Extrahiere Daten für das Diagramm
        const labels = ltcData.map(data => data.commit); // Verwende 'commit' für die X-Achse
        const ltcValues = ltcData.map(data => parseFloat(data.ltc_value)); // Stelle sicher, dass es eine Zahl ist

        // Überprüfe, ob bereits eine Chart-Instanz für dieses Canvas-Element existiert
        if (window['ltcChart' + i]) {
            // Aktualisiere das vorhandene Diagramm
            window['ltcChart' + i].data.labels = labels;
            window['ltcChart' + i].data.datasets[0].data = ltcValues;
            window['ltcChart' + i].update();
        } else {
            // Erstelle ein neues Diagramm als Balkendiagramm
            window['ltcChart' + i] = new Chart(ctx, {
                type: 'line', // Ändere den Typ zu 'bar'
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Lead Time for Changes (Stunden)',
                        data: ltcValues,
                        fill: false,
                        borderColor: '#65a95f',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'LTC (Stunden)'
                            }
                        }
                    }
                }
            });
        }
    }
}





// Verwendet beim Laden der Seite und auch wenn neue Daten abgerufen werden
document.getElementById('fetch_project_data').addEventListener('click', function () {
    const projectId = document.getElementById('projectSelector').value;
    fetch('/get_mttr_data?project_id=' + projectId)
        .then(response => response.json())
        .then(data => {
            updateMTTRDisplay(data.data); // Übergebe die Daten direkt an die Funktion
        })
        .catch(error => {
            console.error('Fehler beim Abrufen der MTTR-Daten:', error);
        });
});





function updateCFRDisplay(cfrData) {
    document.getElementById('failed').innerText = cfrData.failed;
    document.getElementById('total').innerText = cfrData.total;
    document.getElementById('cfrDisplay').innerText = cfrData.cfr.toFixed(2) + '%'; // Formatieren auf 2 Dezimalstellen
}

// Funktion zum Erstellen des CFR Balkendiagramms
function updateCFRChart(cfr) {
    const ctx = document.getElementById('cfrBarChart').getContext('2d');
    const cfrChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Change Failure Rate'],
            datasets: [{
                label: 'CFR (%)',
                data: [cfr],
                backgroundColor: '#800080',
                borderColor: '#800080',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    max: 30  // Skala bis 30% festgelegt
                }
            }
        }
    });
}



function updateDFChart(dfData) {
    

    if (window.myBarChart) {
        window.myBarChart.data.labels = dfData.months;
        window.myBarChart.data.datasets.forEach((dataset) => {
            dataset.data = dfData.deployments;

        });
        window.myBarChart.update();
    } else {
        
        var ctx = document.getElementById('myBarChart').getContext('2d');
      
        window.myBarChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dfData.months,
                datasets: [{
                    label: 'Deployments pro Monat',
                    data: dfData.deployments,
                    backgroundColor: '#87cde9',
                    borderColor: '#87cde9',
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
                },
                animation: {
                    duration: 1000, // Dauer in Millisekunden
                    easing: 'easeOutBounce'
                }
            }
        });
    }
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

function updateLTCChart(ltcData) {
    const ltcChartElement = document.getElementById('ltcBarChart');
    if (!ltcChartElement) return;

    const ctx = ltcChartElement.getContext('2d');

    // Extrahiere Daten für das Diagramm
    const labels = ltcData.map(data => data.commit); // oder data.deployment, abhängig von der Struktur deiner Daten
    const ltcValues = ltcData.map(data => parseFloat(data.ltc_value)); // Stelle sicher, dass es eine Zahl ist

    if (window.ltcChart) {
        // Aktualisiere das vorhandene Diagramm
        window.ltcChart.data.labels = labels;
        window.ltcChart.data.datasets[0].data = ltcValues;
        window.ltcChart.update();
    } else {
        // Erstelle ein neues Diagramm als Balkendiagramm
        window.ltcChart = new Chart(ctx, {
            type: 'line', // Ändere den Typ zu 'bar'
            data: {
                labels: labels,
                datasets: [{
                    label: 'Lead Time for Changes (Stunden)',
                    data: ltcValues,
                    fill: false,
                    borderColor: '#65a95f',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'LTC (Stunden)'
                        }
                    }
                }
            }
        });
    }
}




function updateBarChart() {
    // Daten aus den data-* Attributen lesen
    const chartDataElement = document.getElementById('chartData');
    const months = JSON.parse(chartDataElement.getAttribute('data-months'));
    const monthlyDeploymentsRaw = JSON.parse(chartDataElement.getAttribute('data-deployments'));
    const monthlyDeployments = monthlyDeploymentsRaw.map(value => (value === null || value === 0) ? 0 : value);

    // Ensure predefinedColors is defined and accessible here
    const predefinedColors = ['#FF6384', '#36A2EB', '#FFCE56'];

    // Generate the background and border color arrays for each bar
    const backgroundColors = monthlyDeployments.map((_, index) => predefinedColors[index % predefinedColors.length]);
    const borderColors = backgroundColors;

    // Destroy the existing chart if it exists
    if (window.myBarChart) {
        window.myBarChart.destroy();
    }

    var ctx = document.getElementById('myBarChart').getContext('2d');
    window.myBarChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: months,
            datasets: [{
                label: 'Deployments pro Monat',
                data: monthlyDeployments,
                backgroundColor: '#216b73',
                borderColor: '#216b73',
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
            },
            animation: {
                duration: 1000, // Dauer in Millisekunden
                easing: 'easeOutBounce'
            }
        }
    });
}







document.addEventListener('DOMContentLoaded', function () {
    var newProjectForm = document.getElementById('newProjectForm');

    newProjectForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Verhindert das normale Senden des Formulars

        var formData = new FormData(this);

        fetch('/create_project', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayMessage(data.message, 'success'); // Erfolgsmeldung
                    $('#createProjectModal').modal('hide'); // Schließt das Modal

                } else {
                    displayMessage(data.message, 'error'); // Fehlermeldung
                }
            })
            .catch(error => {
                console.error('Fehler beim Senden des Formulars:', error);
                displayMessage('Ein Fehler ist aufgetreten', 'error');
            });
    });
});

function displayMessage(message, type) {
    var messageBox = document.createElement('div');
    messageBox.textContent = message;
    messageBox.className = type === 'success' ? 'alert alert-success' : 'alert alert-danger';
    messageBox.style.position = 'fixed';
    messageBox.style.bottom = '20px';
    messageBox.style.right = '20px';
    messageBox.style.zIndex = '1000';

    document.body.appendChild(messageBox);

    // Meldung nach ein paar Sekunden ausblenden
    setTimeout(function () {
        messageBox.remove();
    }, 3000);
}

function parseDate(dateStr) {
    // Zerlegen des Strings in seine Bestandteile
    const [time, date] = dateStr.split(' ');
    const [hours, minutes] = time.split(':').map(part => parseInt(part, 10));
    const [day, month, year] = date.split('.').map(part => parseInt(part, 10));

    // Erstellen eines neuen Date-Objekts
    

    return new Date(year, month - 1, day, hours, minutes);
}

document.addEventListener('DOMContentLoaded', function () {
    fetch('/get_mttr_data')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('mttrChart').getContext('2d');
            const projectNames = [...new Set(data.data.map(incident => incident.project))];
            const labels = [...new Set(data.data.map(incident => incident.starttime))];

            // Initialisieren der Datenstruktur für jedes Projekt mit Nullen
            const projectData = projectNames.reduce((acc, projectName) => {
                acc[projectName] = labels.map(() => null); // Starten mit null für jede Zeitmarke
                return acc;
            }, {});

            // Füllen der tatsächlichen Daten für jedes Projekt
            data.data.forEach(incident => {
                const projectName = incident.project;
                const labelIndex = labels.indexOf(incident.starttime);
                const start = parseDate(incident.starttime);
                const end = parseDate(incident.endtime);
                const duration = (end - start) / 1000 / 3600;
                projectData[projectName][labelIndex] = parseFloat(duration.toFixed(2));
            });

            // Erstellen eines Datasets für jedes Projekt
            const datasets = projectNames.map((projectName, index) => {
                const color = predefinedColors[index % predefinedColors.length];
                return {
                    label: projectName,
                    data: projectData[projectName],
                    // Farben dynamisch zuweisen, je nach Anzahl der Projekte
                    backgroundColor: color, 
                    borderColor: color, 
                    borderWidth: 1
                };
            });

            // Erstellen des Diagramms
            const mttrChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels, 
                    datasets: datasets
                },
                options: {
                    responsive: false,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Dauer (Stunden)'
                            }
                        }
                    },
                    plugins: {

                        title: {
                            display: true,
                            text: `MTTR: ${data.mttr}`
                        }
                    }
                }
            });
        });
});


document.addEventListener('DOMContentLoaded', function () {
    fetch('/get_mttr_data')
        .then(response => response.json())
        .then(data => {
            // Aggregieren der MTTR-Daten für jedes Projekt
            const mttrByProject = {};
            data.data.forEach(incident => {
                const projectName = incident.project;
                const start = new Date(parseDate(incident.starttime));
                const end = new Date(parseDate(incident.endtime));

                const duration = (end - start) / 1000 / 60; // Dauer in Minuten
                if (mttrByProject[projectName]) {
                    mttrByProject[projectName] += duration;
                } else {
                    mttrByProject[projectName] = duration;
                }
            });

            // Definiere ein Array von Farben
            const colors = predefinedColors;
            const backgroundColors = Object.keys(mttrByProject).map((_, index) => colors[index % colors.length]);

            // Erstellen der Datenstruktur für das Chart.js-Diagramm
            const mttrData = {
                labels: Object.keys(mttrByProject),
                datasets: [{
                    label: 'MTTR in Minuten',
                    data: Object.values(mttrByProject),
                    backgroundColor: backgroundColors, // Verwende das Farb-Array für Hintergrundfarben
                    borderColor: backgroundColors, // Verwende das Farb-Array für Randfarben
                    borderWidth: 1
                }]
            };

            // Erstellen des Doughnut-Charts
            const ctx = document.getElementById('mttrRingChart').getContext('2d');
            const mttrRingChart = new Chart(ctx, {
                type: 'doughnut',
                data: mttrData,
                options: {
                    responsive: false,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: 'MTTR für Projekte (in Minuten)'
                        }
                    }
                }
            });
        })
        .catch(error => console.error('Fehler beim Abrufen der MTTR-Daten', error));
});

document.addEventListener('DOMContentLoaded', function () {
var projectId = document.getElementById('projectSelector').value;
// Starten   einen Fetch für jede Datenquelle
Promise.all([
    fetch('/get_cd_metric_data?project_id=' + projectId).then(response => response.json()),
    fetch('/get_ltc_data?project_id=' + projectId).then(response => response.json()),
    fetch('/get_mttr_data?project_id=' + projectId).then(response => response.json()),
    fetch('/get_cfr_data?project_id=' + projectId).then(response => response.json()),
    fetch('/get_df_data?project_id=' + projectId).then(response => response.json()),
    // ... fügen   hier weitere fetch Aufrufe für andere Datenquellen hinzu
])
    .then(alldata => {
        // alldata[0] enthält die Antwort von '/get_cd_metric_data'
        // alldata[1] enthält die Antwort von '/get_ltc_data'
        // ... und so weiter für weitere Antworten

        // Aktualisieren   hier die Tabellen mit den Daten von alldata
        updateCCVTable(alldata[0]); // Eine  Funktion, um die CCV-Tabelle zu aktualisieren
        updateLTCTable(alldata[1]); // Eine  Funktion, um die LTC-Tabelle zu aktualisieren
        const ltcData = alldata[1]; 
            updateLTCChart(alldata[1]);
            updateLTCDashboard(ltcData);
        updateMTTRTable(alldata[2].data);
        updateMTTRValue(alldata[2].mttr);
        updateMTTRDisplay(alldata[2].data);
        updateCFRDisplay(alldata[3]); // Ihre neue Funktion, um die CFR anzuzeigen
        const cfr = alldata[3].cfr;
        updateCFRChart(cfr);
        updateCFRDashboard(cfr);
        updateDFChart(alldata[4]);
        const df = alldata[4].df;
        updateDFDashboard(df);
        document.getElementById('dfValue').textContent = alldata[4].df;
        // ... weitere Funktionen, um andere Tabellen zu aktualisieren

        // Nach dem Aktualisieren der Tabellen rufen   updateCharts erneut auf
        updateCharts();
    })
    .catch(error => console.error('Fehler beim Abrufen der Daten:', error));
});