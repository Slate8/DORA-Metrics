function updateCharts() {
    const tableRows = document.querySelectorAll('tbody tr');
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



    function getRandomColor() {
        let letters = '0123456789ABCDEF';
        let color = '#';
        for (let i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    const datasets = [];


    for (let username in groupedData) {
        let data = [];

        allUniqueTimestamps.forEach((time) => {
            let index = groupedData[username].timestamps.indexOf(time);
            data.push(index !== -1 ? groupedData[username].codeLines[index] : undefined);
        });


        let color = getRandomColor();
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

    const backgroundColors = usernames.map(() => getRandomColor());

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
/*
const projectDropdown = document.getElementById('projectSelector');
projectDropdown.addEventListener('change', () => {
    const selectedProjectId = projectSelector.value;
    if (selectedProjectId === "all") {
        window.location.href = '/?project_id=all';
    } else {
        window.location.href = '/?project_id=' + selectedProjectId;
    }
});

*/
document.getElementById('fetchCCV').addEventListener('click', function() {
    var projectId = document.getElementById('projectSelector').value;
    window.location.href = '/?project_id=' + projectId;
});

// Verhindert das Absenden des Formulars wenn kein Projekt ausgewählt ist
document.querySelector("form").addEventListener("submit", function(event){
    let selectedProject = document.getElementById("projectSelector").value;
    if (selectedProject === "all") {
        alert("Bitte wählen Sie ein Projekt aus!");
        event.preventDefault(); 
    }
});

document.getElementById('fetchMTTR').addEventListener('click', function() {
    var projectId = document.getElementById('projectDropdown').value;
    window.location.href = '/?project_id=' + projectId;
});
