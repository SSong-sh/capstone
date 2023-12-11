// static/js/main.js
function sendData() {
    const inputVariable = document.getElementById('input_variable').value;
    fetch('/clear_sky', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
        'capacity': capacity,
        'latitude': latitude,
        'longitude': longitude, 
    }),
    })
    
    .then(response => response.json())
    .then(graphData => {
        console.log(graphData);
        drawGraph(graphData); // Call the function to draw the graph
    })
    .catch((error) => {
        console.error('Error:', error);
    })

    .then(data => {
        // 서버로부터 받은 응답 처리
        const resultElement = document.getElementById('result');
        resultElement.innerHTML = ''; // 결과 영역 초기화

        // Create table
        let table = document.createElement('table');
        let headerRow = document.createElement('tr');
        let dataRow = document.createElement('tr');

        // Add headers and data
        data.result.forEach((item, index) => {
            let th = document.createElement('th');
            th.textContent = `${index}시`;  // assuming each item represents an hour
            headerRow.appendChild(th);

            let td = document.createElement('td');
            td.textContent = Object.values(item)[0];  // assuming each item is a single-value object
            dataRow.appendChild(td);
        });

        table.appendChild(headerRow);
        table.appendChild(dataRow);

        resultElement.appendChild(table);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}



function submitData() {
    // Collect user input
    let name = document.getElementById('user').value;
    let contact = document.getElementById('user-number1').value + "-" +
              document.getElementById('user-number2').value + "-" +
              document.getElementById('user-number3').value;
    let email = document.getElementById('user-email').value + "@" + document.getElementById('user-email2').value;
    let usingElements = document.querySelectorAll(".usage-input");
    let solarElements = document.querySelectorAll(".solar-input");
    let query = document.getElementById('ask').value;

    let usingValues = Array.from(usingElements).map(input => input.value);
    let solarValues = Array.from(solarElements).map(input => input.value);

    // Construct the data object
    let userData = {
        'name': name,
        'contact': contact,
        'email': email,
        'using': usingValues,
        'solar': solarValues,
        'query': query
    };

    console.log(userData);

    // Send POST request to the server
    fetch('/contact_mail', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    })
    
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .catch(error => {
        console.error('There has been a problem with your fetch operation:', error);
    });
}
;

    
document.addEventListener('DOMContentLoaded', function() {
    // Adding an event listener to the inquiry button
    var inquiryButton = document.getElementById('inquiry-button'); // Assuming the ID of the inquiry button is 'inquiry-button'
    if (inquiryButton && !inquiryButton.classList.contains('event-bound')) {
        inquiryButton.addEventListener('click', function(event) {
            event.preventDefault(); // Preventing the default form submission behavior
            submitPowerData(); // Calling the function when the inquiry button is clicked
        });
        inquiryButton.classList.add('event-bound'); // Add a flag to indicate the event is bound
    }
});



function submitPowerData() {
    let usingElements = document.querySelectorAll(".usage-input");
    let solarElements = document.querySelectorAll(".solar-input");
    let usingValues = Array.from(usingElements).map(input => input.value);
    let solarValues = Array.from(solarElements).map(input => input.value);
    console.log(usingValues);
    console.log(solarValues);

    fetch('/calculate_price', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'power_generated': solarValues,
            'power_used': usingValues
        }),
    })
    .then(response => response.json())
    .then(graphData => {
        // console.log(graphData);
        drawGraph(graphData); 
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

let mychart = null;
function drawGraph(graphData) {
    let usingElements = document.querySelectorAll(".usage-input");
    let solarElements = document.querySelectorAll(".solar-input");
    let usingValues = Array.from(usingElements).map(input => input.value);
    let solarValues = Array.from(solarElements).map(input => input.value);
    let purchase = usingValues.map((value, index) => value - graphData.best_position_variance[index]);
    
    const ctx = document.getElementById('graph-container').getContext('2d');
    console.log('power generated')
    console.log(graphData.power_generated);
    if (mychart) {
        mychart.destroy();
        console.log('destroyed');
    }
    mychart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: graphData.hour,
            datasets: [{
                label: '실제 전력 사용량',
                data: usingValues,
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 2,
                type: 'line',
                yAxisID: 'y-axis-1',
            }, {
                label: '태양광 발전량',
                data: graphData.before_solar,
                type: 'line',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 2,
                fill: false,
                yAxisID: 'y-axis-1',
            },
            {
                label: '최적 발전 사용량',
                data: graphData.best_position_variance,
                borderWidth: 1,
                fill: false,
                yAxisID: 'y-axis-1',
                backgroundColor:'rgba(255, 159, 64, 0.5)'
            },
            {
                label: '구매 전력 사용량',
                data : purchase,
                borderColor: 'rgba(255, 206, 86, 1)',
                borderWidth: 1,
                fill: false,
                yAxisID: 'y-axis-1',

            }]
        },
        options: {
            scales: {
                'y-axis-1': {
                    type: 'linear',
                    display: true,
                    position: 'left',
                },
            },
        },
    });
}

