
function search() {
    var input, filter, freezers, i, txtValue;
    input = document.getElementById('searchInput');
    filter = input.value.toUpperCase();
    freezers = document.getElementsByClassName('freezer');

    for (i = 0; i < freezers.length; i++) {
        freezer = freezers[i];
        txtValue = freezer.textContent || freezer.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            freezer.style.display = '';
        } else {
            freezer.style.display = 'none';
        }
    }

    if (Array.from(freezers).every(f => f.style.display === 'none')) {
        searchOtherPages(filter);
    }
}

function searchOtherPages(filter) {
    fetch('../freezer_data.json')
        .then(response => response.json())
        .then(data => {
            var results = [];
            for (var freezer in data) {
                if (freezer.toUpperCase().indexOf(filter) > -1 ||
                    data[freezer].room.toString().toUpperCase().indexOf(filter) > -1 ||
                    data[freezer].condition.toUpperCase().indexOf(filter) > -1 ||
                    data[freezer].status.toUpperCase().indexOf(filter) > -1 ||
                    data[freezer].libraries.some(lib => lib.toUpperCase().indexOf(filter) > -1)) {
                    results.push({freezer: freezer, room: data[freezer].room});
                }
            }
            displaySearchResults(results);
        });
}

function displaySearchResults(results) {
    var freezersDiv = document.querySelector('.freezers');
    freezersDiv.innerHTML = '<h2>Search Results:</h2>';
    if (results.length === 0) {
        freezersDiv.innerHTML += '<p>No results found.</p>';
    } else {
        var resultsList = '<ul>';
        results.forEach(function(result) {
            resultsList += `<li><a href="../Freezer/freezer_${result.freezer}.html">${result.freezer}</a> (Room ${result.room})</li>`;
        });
        resultsList += '</ul>';
        freezersDiv.innerHTML += resultsList;
    }
}
    