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


document.getElementById('fetch_project_data').addEventListener('click', function () {
    var projectId = document.getElementById('projectSelector').value;
    window.location.href = '/?project_id=' + projectId;
    updateBarChart();
});

// Verhindert das Absenden des Formulars wenn kein Projekt ausgewählt ist
//wirkt nur auf das erste formular muss noch angepasst werden auf eine spezifische id!!!
document.querySelector("form").addEventListener("submit", function (event) {
    let selectedProject = document.getElementById("projectSelector").value;
    if (selectedProject === "all") {
        alert("Bitte wählen Sie ein Projekt aus!");
        event.preventDefault();
    }
});

document.getElementById("ltcForm").addEventListener("submit", function (event) {
    let selectedProject = document.getElementById("ltcprojectSelector").value;
    let commitDatetime = document.getElementById("commitDatetime").value;
    let deploymentDatetime = document.getElementById("deploymentDatetime").value;

    // Überprüfen, ob das Projekt "all" ist
    if (selectedProject === "all") {
        alert("Bitte wählen Sie ein Projekt aus!");
        event.preventDefault();
        return;  // Beendet die Funktion hier, um weitere Überprüfungen zu vermeiden
    }

    // Überprüfen, ob die Input-Felder leer sind
    if (!commitDatetime || !deploymentDatetime) {
        alert("Bitte füllen Sie alle Datum- und Uhrzeitfelder aus!");
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