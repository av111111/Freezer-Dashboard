import json
import os
from generate_room_html import generate_room_html
from generate_freezer_page import generate_freezer_page
from extract_freezer_info import extract_freezer_info
from generate_home_page import generate_home_page

def generate_all_html(freezer_status, freezer_database, unique_rooms):
    freezer_data = {}

    # Ensure directories exist
    os.makedirs('Rooms', exist_ok=True)
    os.makedirs('Freezer', exist_ok=True)
    os.makedirs('HomePage', exist_ok=True)

    for room in unique_rooms:
        # Generate and save room HTML pages
        html_content = generate_room_html(room, freezer_status, freezer_database, unique_rooms)
        output_path = f'Rooms/room_{room}.html'
        with open(output_path, 'w') as file:
            file.write(html_content)

        # Generate and save individual freezer pages
        room_freezers = freezer_status[freezer_status['Room Number'] == room]['Freezer name'].unique()
        for freezer in room_freezers:
            freezer_html = generate_freezer_page(freezer, freezer_status, freezer_database)
            freezer_output_path = f'Freezer/freezer_{freezer}.html'
            with open(freezer_output_path, 'w') as file:
                file.write(freezer_html)

            # Collect data for search functionality
            details, shelf_info = extract_freezer_info(freezer, freezer_status, freezer_database)
            freezer_data[freezer] = {
                'room': room,
                'condition': details['Freezer condition'],
                'status': details['Freezer status'],
                'libraries': shelf_info['library'].dropna().unique().tolist()
            }

    # Generate search.js file for search functionality
    search_js = """
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
    """

    with open('HomePage/search.js', 'w') as file:
        file.write(search_js)

    # Save freezer data as JSON for search functionality
    with open('freezer_data.json', 'w') as file:
        json.dump(freezer_data, file)

    # Generate the home page
    generate_home_page(freezer_status, freezer_database, unique_rooms)

if __name__ == "__main__":
    from load_data import load_data

    # Load data
    freezer_status, freezer_database = load_data()
    unique_rooms = freezer_status['Room Number'].unique()

    # Generate all HTML pages including room pages with shelf occupancy details
    generate_all_html(freezer_status, freezer_database, unique_rooms)

    print("HTML pages generated for each room and individual freezers.")
    print("Home page generated.")
    print("Room pages with shelf occupancy details generated.")
    print("\nFirst few rows of Freezer Status:")
    print(freezer_status.head())
    print("\nFirst few rows of Freezer Database:")
    print(freezer_database.head())
