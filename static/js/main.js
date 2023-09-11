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
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert(data.message);
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
}
;

    


