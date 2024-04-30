function fetchData() {
    $.ajax({
        url: '/fetch/',
        type: 'GET', // GET방식으로 요청
        success: function(response) {
            displayTable(response['pcs_data'], 'pcs-table', 'W', 'Hz', 'V', 'A');
            displayTable(response['bat_data'], 'bat-table', '%', '%', 'V', 'A');
        },
        error: function() {
            $('#data-display').html('<p>데이터 불러오는 중 문제 발생</p>');
        }
    });
}

function displayTable(data, tableId, ...units) {
    let tableHtml = `<table>`;
    Object.keys(data).forEach((key, index) => {
        const formattedValue = parseFloat(data[key]).toFixed(3);
        const unit = determineUnit(key, units);
        tableHtml += `<tr class="border-2"><th class="text-center text-blue-900 px-6 py-4 bg-gray-200 border-2 border-neutral-300">${key}</th><td class="text-center  border-2 border-neutral-300 px-8 py-4">${formattedValue} ${unit}</td></tr>`;
    });
    tableHtml += `</table>`;
    $('#' + tableId).html(tableHtml);
}

function determineUnit(key, units) {
    if (key === 'active_power') return units[0];
    if (key.includes('SO')) return units[0];
    if (key === "frequency") return units[1];
    if (key.includes('vol')) return units[2];
    if (key.includes('cur')) return units[3];
    return '';
}

function showClock() {
    var currentDate = new Date();
    var divClock = document.getElementById('divclock');
    
    var dateMsg = "";
    var clockMsg = "";

    dateMsg += currentDate.getFullYear() + "년 ";
    dateMsg += currentDate.getMonth() + 1 + "월 ";
    dateMsg += currentDate.getDate() + "일 "; 
    
    clockMsg += currentDate.getHours() + ":";

    if (currentDate.getMinutes() < 10) clockMsg += "0" + currentDate.getMinutes() +  ":";
    else clockMsg += currentDate.getMinutes() + ":";


    if (currentDate.getSeconds() < 10) clockMsg += "0" + currentDate.getSeconds();
    else clockMsg += currentDate.getSeconds();

    divClock.innerHTML = dateMsg + '<br>' +clockMsg ;
    // divClock.innerText = clockMsg;
    
    setTimeout(showClock, 1000)
}

$(document).ready(function() {
    fetchData();
    setInterval(fetchData, 1000);
});