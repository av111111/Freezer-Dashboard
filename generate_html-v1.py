import pandas as pd
import os
import json

# Load the data from Google Sheets
freezer_status_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTBqu3473l0OMMlicoERthxkIYTneF9fh9jy958Q0zAb5NwVCeSDsIYUsxpnBzgl4rDoMJ7P7E1W2lM/pubhtml?gid=0&single=true"
freezer_database_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSgeAPBmFPRxaRHnoHLG7Xt5wT_gr5A0gkgfgjiT1mLFBPgQsXFa2k9wriUvZtkl1_DB7fcrTnV0DUj/pubhtml?gid=0&single=true"

# Read the data from Google Sheets
freezer_status = pd.read_html(freezer_status_url)[0]
freezer_database = pd.read_html(freezer_database_url)[0]

# Set the first row as column names and remove it from the data
freezer_status.columns = freezer_status.iloc[0]
freezer_status = freezer_status.drop(freezer_status.index[0])

freezer_database.columns = freezer_database.iloc[0]
freezer_database = freezer_database.drop(freezer_database.index[0])

# Reset the index for both dataframes
freezer_status = freezer_status.reset_index(drop=True)
freezer_database = freezer_database.reset_index(drop=True)

# Function to generate the home page with collapsible rooms
def generate_home_page(status_df, unique_rooms):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BioResource Freezer Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; }
        h1 { text-align: center; }
        .rooms-container { display: flex; flex-wrap: wrap; justify-content: center; }
        .room { border: 1px solid #ccc; border-radius: 8px; padding: 10px; margin: 10px; width: 300px; transition: all 0.3s; }
        .room.collapsed { padding: 5px; border-width: 1px; }
        .room h2 { margin: 0; font-size: 1.5em; display: flex; justify-content: space-between; align-items: center; }
        .freezers { display: flex; flex-direction: column; }
        .freezer { border: 1px solid #ccc; border-radius: 8px; padding: 10px; margin: 10px; width: 200px; height: 100px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); overflow: hidden; }
        .freezer h3 { margin: 0; font-size: 1.2em; }
        .dirty { color: red; }
        .clean { color: green; }
        .status { display: inline-block; padding: 2px 6px; border-radius: 4px; color: white; }
        .status.offer-out { background-color: #FFB6C1; color: black; } /* Light Pink */
        .status.dispose { background-color: #f47979; }
        .status.keep { background-color: lightblue; }
        .capacity { display: flex; align-items: center; }
        .search-container { text-align: center; margin-bottom: 20px; }
        .search-container input { padding: 5px; width: 300px; }
        .collapse-button { cursor: pointer; }
        .collapsed { display: none; }
        .logo-container { text-align: center; margin-bottom: 20px; }
        .logo-container img { margin: 0 10px; width: 100px; }
    </style>
    <script>
        function toggleRoom(roomId, imgElement) {
            var roomElement = document.getElementById(roomId);
            if (roomElement.classList.contains('collapsed')) {
                roomElement.classList.remove('collapsed');
                imgElement.src = 'expand-less.jpg';
            } else {
                roomElement.classList.add('collapsed');
                imgElement.src = 'expand-more.jpg';
            }
        }

        function searchHomepage() {
            var input, filter, rooms, freezers, i, txtValue, roomVisible;
            input = document.getElementById('searchInput');
            filter = input.value.toUpperCase();
            rooms = document.getElementsByClassName('room');
            freezers = document.getElementsByClassName('freezer');

            for (i = 0; i < rooms.length; i++) {
                roomVisible = false;
                freezers = rooms[i].getElementsByClassName('freezer');
                for (j = 0; j < freezers.length; j++) {
                    txtValue = freezers[j].textContent || freezers[j].innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        freezers[j].style.display = '';
                        roomVisible = true;
                    } else {
                        freezers[j].style.display = 'none';
                    }
                }
                rooms[i].style.display = roomVisible ? '' : 'none';
            }
        }
    </script>
</head>
<body>
    <div class="logo-container">
        <img src="Sanger_Logo.png" alt="Sanger Logo">
        <img src="bio_r_logo.png" alt="BIO/R Logo">
    </div>
    <h1>BioResource Freezer Dashboard</h1>
    <div class="search-container">
        <input type="text" id="searchInput" onkeyup="searchHomepage()" placeholder="Search for freezers or rooms..">
    </div>
    <div class="rooms-container">
"""

    for room in unique_rooms:
        html_content += f"""
        <div class="room">
            <h2><a href="room_{room}.html">{room}</a> <img src="expand-less.jpg" class="collapse-button" onclick="toggleRoom('room_{room}_content', this)"></h2>
            <div id="room_{room}_content" class="room-content">
                <div class="freezers">
        """
        freezers_in_room = status_df[status_df['Room Number'] == room]['Freezer name'].unique()
        for freezer in freezers_in_room:
            details, shelf_info = extract_freezer_info(freezer, status_df, freezer_database)
            total_shelves = shelf_info['shelf'].nunique()
            occupied_shelves = shelf_info[shelf_info['library'] != '']['shelf'].nunique()
            html_content += f"""
                    <div class="freezer">
                        <h3><a href="freezer_{details['Freezer number']}.html">{details['Freezer number']}</a></h3>
                        <p><span class="{details['Freezer condition'].lower()}">{details['Freezer condition']}</span> | <span class="status {details['Freezer status'].lower()}">{details['Freezer status']}</span></p>
                        <p>Capacity: {occupied_shelves} / {total_shelves}</p>
                    </div>
            """
        html_content += """
                </div>
            </div>
        </div>
        """
    
    html_content += """
    </div>
</body>
</html>
    """
    
    with open('index.html', 'w') as file:
        file.write(html_content)
        
# Function to extract freezer information
def extract_freezer_info(freezer_number, status_df, database_df):
    # Filter the status_df for the given freezer number
    freezer_info = status_df[status_df['Freezer name'] == freezer_number].iloc[0]
    
    # Extract relevant details
    freezer_details = {
        'Freezer number': freezer_info['Freezer name'],
        'Freezer condition': freezer_info['Clean or dirty'],
        'Freezer status': freezer_info['ULT for BR or Offer out'],
        'Age': freezer_info['Age (years)'],
        'Energy use': freezer_info['Energy Consumption (kwh per day)'],
        'Room Number': freezer_info['Room Number']
    }
    
    # Filter the database_df for the given freezer number and extract all information
    shelf_info = database_df[database_df['freezer'] == freezer_number]
    
    return freezer_details, shelf_info

# Get unique room numbers
unique_rooms = freezer_status['Room Number'].unique()

# Function to generate HTML content for a single freezer
def generate_room_html(room_number, status_df, database_df):
    # Filter the status dataframe for the given room number
    filtered_freezer_status = status_df[status_df['Room Number'] == room_number]

    # Extract information for all freezers in the room
    freezers = filtered_freezer_status['Freezer name'].unique()
    freezer_data = []

    for freezer in freezers:
        details, shelf_info = extract_freezer_info(freezer, status_df, database_df)
        freezer_data.append((details, shelf_info))

    # Generate HTML for all freezers
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Room {room_number}</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        h1 {{ text-align: center; }}
        .nav-container {{ text-align: center; margin-bottom: 20px; }}
        .nav-container a {{ margin: 0 10px; text-decoration: none; color: #007BFF; }}
        .nav-container a:hover {{ text-decoration: underline; }}
        .nav-container .current-room {{ font-weight: bold; color: #FF5733; border: 1px solid #FF5733; padding: 2px 6px; border-radius: 4px; }}
        .freezers {{ display: flex; flex-wrap: wrap; justify-content: center; }}
        .freezer {{ border: 1px solid #ccc; border-radius: 8px; padding: 10px; margin: 10px; width: 300px; height: 400px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); overflow: hidden; }}
        .freezer h2 {{ margin: 0; font-size: 1.2em; }}
        .dirty {{ color: red; }}
        .clean {{ color: green; }}
        .status {{ display: inline-block; padding: 2px 6px; border-radius: 4px; color: white; }}
        .status.offer-out {{ background-color: #FFB6C1; color: black; }} /* Light Pink */
        .status.dispose {{ background-color: #f47979; }}
        .status.keep {{ background-color: lightblue; }}
        .scrollable {{ overflow-y: auto; height: 250px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 5px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .search-container {{ text-align: center; margin-bottom: 20px; }}
        .search-container input {{ padding: 5px; width: 300px; }}
        .logo-right {{ position: absolute; top: 10px; right: 10px; width: 100px; }}
        .logo-left {{ position: absolute; top: 10px; left: 10px; width: 100px; }}
        .capacity {{ display: flex; align-items: center; }}
        .shelf {{
            width: 60px;
            height: 20px;
            margin: 0px;
            border: 1px solid #ccc;
            box-sizing: border-box;
            text-align: center;
            line-height: 20px;
            cursor: pointer;
            font-size: 10px;
            display: inline-block;
        }}
        .occupied {{ background-color: orange; }}
        .free {{ background-color: green; }}
    </style>
    <script>
        function filterTable(freezerNumber, shelf) {{
            var table, tr, td, i, txtValue;
            table = document.getElementById("contentsTable_" + freezerNumber);
            tr = table.getElementsByTagName("tr");

            for (i = 1; i < tr.length; i++) {{
                tr[i].style.display = "none";
                td = tr[i].getElementsByTagName("td");
                if (td[0]) {{
                    txtValue = td[0].textContent || td[0].innerText;
                    if (txtValue.indexOf(shelf) > -1) {{
                        tr[i].style.display = "";
                    }}
                }}
            }}
        }}
    </script>
</head>
<body>
    <img src="Sanger_Logo.png" alt="Sanger Logo" class="logo-left">
    <img src="bio_r_logo.png" alt="BIO/R Logo" class="logo-right">
    <h1>Freezer Information - Room {room_number}</h1>
    <div class="search-container">
        <input type="text" id="searchInput" onkeyup="search()" placeholder="Search for library, freezer number, or room..">
    </div>
    <div class="nav-container">
"""

    # Add links to other room pages, highlighting the current room
    for room in unique_rooms:
        if room == room_number:
            html_content += f'<a href="room_{room}.html" class="current-room">{room}</a> | '
        else:
            html_content += f'<a href="room_{room}.html">{room}</a> | '

    html_content = html_content.rstrip(" | ")  # Remove the trailing "|"

    html_content += """
    </div>
    <div class="freezers">
"""

    for details, shelf_info in freezer_data:
        total_shelves = shelf_info['shelf'].nunique()
        occupied_shelves = shelf_info[shelf_info['library'] != '']['shelf'].nunique()
        free_shelves = total_shelves - occupied_shelves

        all_shelves = range(1, total_shelves + 1)
        capacity_html = ""
        for shelf in all_shelves:
            if shelf in shelf_info[shelf_info['library'] != '']['shelf'].unique():
                capacity_html += f'<div class="shelf occupied" onclick="filterTable(\'{details["Freezer number"]}\', \'{shelf}\')">{shelf}</div>'
            else:
                capacity_html += f'<div class="shelf free" onclick="filterTable(\'{details["Freezer number"]}\', \'{shelf}\')">{shelf}</div>'

        html_content += f"""
        <div class="freezer" data-room="{details['Room Number']}">
            <h2><a href="freezer_{details['Freezer number']}.html">{details['Freezer number']}</a></h2>
            <p><span class="{details['Freezer condition'].lower()}">{details['Freezer condition']}</span> | <span class="status {details['Freezer status'].lower()}">{details['Freezer status']}</span></p>
            <p>{details['Age']} years old | {details['Energy use']} kwh/Day</p>
            <p>Capacity: {occupied_shelves} / {total_shelves}</p>
            <div class="capacity">{capacity_html}</div>
            <div class="scrollable">
                <table id="contentsTable_{details['Freezer number']}">
                    <tr>
                        <th>Shelf</th>
                        <th>Library</th>
                        <th>Count</th>
                    </tr>
        """

        library_counts = shelf_info.groupby(['shelf', 'library']).size().reset_index(name='Count')
        for _, row in library_counts.iterrows():
            html_content += f"""
                    <tr>
                        <td>{row['shelf']}</td>
                        <td>{row['library']}</td>
                        <td>{row['Count']}</td>
                    </tr>
            """

        html_content += """
                </table>
            </div>
        </div>
        """

    html_content += """
    </div>
</body>
</html>
"""

    return html_content

    # Filter the status dataframe for the given room number
    filtered_freezer_status = status_df[status_df['Room Number'] == room_number]

    # Extract information for all freezers in the room
    freezers = filtered_freezer_status['Freezer name'].unique()
    freezer_data = []

    for freezer in freezers:
        details, shelf_info = extract_freezer_info(freezer, status_df, database_df)
        freezer_data.append((details, shelf_info))

    # Generate HTML for all freezers
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Room {room_number}</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        h1 {{ text-align: center; }}
        .nav-container {{ text-align: center; margin-bottom: 20px; }}
        .nav-container a {{ margin: 0 10px; text-decoration: none; color: #007BFF; }}
        .nav-container a:hover {{ text-decoration: underline; }}
        .nav-container .current-room {{ font-weight: bold; color: #FF5733; border: 1px solid #FF5733; padding: 2px 6px; border-radius: 4px; }}
        .freezers {{ display: flex; flex-wrap: wrap; justify-content: center; }}
        .freezer {{ border: 1px solid #ccc; border-radius: 8px; padding: 10px; margin: 10px; width: 300px; height: 400px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); overflow: hidden; }}
        .freezer h2 {{ margin: 0; font-size: 1.2em; }}
        .dirty {{ color: red; }}
        .clean {{ color: green; }}
        .status {{ display: inline-block; padding: 2px 6px; border-radius: 4px; color: white; }}
        .status.offer-out {{ background-color: #FFB6C1; color: black; }} /* Light Pink */
        .status.dispose {{ background-color: #f47979; }}
        .status.keep {{ background-color: lightblue; }}
        .scrollable {{ overflow-y: auto; height: 250px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 5px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .search-container {{ text-align: center; margin-bottom: 20px; }}
        .search-container input {{ padding: 5px; width: 300px; }}
        .logo-right {{ position: absolute; top: 10px; right: 10px; width: 100px; }}
        .logo-left {{ position: absolute; top: 10px; left: 10px; width: 100px; }}
        .capacity {{ display: flex; align-items: center; }}
        .shelf {{
            width: 60px;
            height: 20px;
            margin: 0px;
            border: 1px solid #ccc;
            box-sizing: border-box;
            text-align: center;
            line-height: 20px;
            cursor: pointer;
            font-size: 10px;
            display: inline-block;
        }}
        .occupied {{ background-color: orange; }}
        .free {{ background-color: green; }}
    </style>
    <script>
        function filterTable(freezerNumber, shelf) {{
            var table, tr, td, i, txtValue;
            table = document.getElementById("contentsTable_" + freezerNumber);
            tr = table.getElementsByTagName("tr");

            for (i = 1; i < tr.length; i++) {{
                tr[i].style.display = "none";
                td = tr[i].getElementsByTagName("td");
                if (td[0]) {{
                    txtValue = td[0].textContent || td[0].innerText;
                    if (txtValue.indexOf(shelf) > -1) {{
                        tr[i].style.display = "";
                    }}
                }}
            }}
        }}
    </script>
</head>
<body>
    <img src="Sanger_Logo.png" alt="Sanger Logo" class="logo-left">
    <img src="bio_r_logo.png" alt="BIO/R Logo" class="logo-right">
    <h1>Freezer Information - Room {room_number}</h1>
    <div class="search-container">
        <input type="text" id="searchInput" onkeyup="search()" placeholder="Search for library, freezer number, or room..">
    </div>
    <div class="nav-container">
"""

    # Add links to other room pages, highlighting the current room
    for room in unique_rooms:
        if room == room_number:
            html_content += f'<a href="room_{room}.html" class="current-room">{room}</a> | '
        else:
            html_content += f'<a href="room_{room}.html">{room}</a> | '

    html_content = html_content.rstrip(" | ")  # Remove the trailing "|"

    html_content += """
    </div>
    <div class="freezers">
"""

    for details, shelf_info in freezer_data:
        total_shelves = shelf_info['shelf'].nunique()
        occupied_shelves = shelf_info[shelf_info['library'] != '']['shelf'].nunique()
        free_shelves = total_shelves - occupied_shelves

        all_shelves = range(1, total_shelves + 1)
        capacity_html = ""
        for shelf in all_shelves:
            if shelf in shelf_info[shelf_info['library'] != '']['shelf'].unique():
                capacity_html += f'<div class="shelf occupied" onclick="filterTable(\'{details["Freezer number"]}\', \'{shelf}\')">{shelf}</div>'
            else:
                capacity_html += f'<div class="shelf free" onclick="filterTable(\'{details["Freezer number"]}\', \'{shelf}\')">{shelf}</div>'

        html_content += f"""
        <div class="freezer" data-room="{details['Room Number']}">
            <h2><a href="freezer_{details['Freezer number']}.html">{details['Freezer number']}</a></h2>
            <p><span class="{details['Freezer condition'].lower()}">{details['Freezer condition']}</span> | <span class="status {details['Freezer status'].lower()}">{details['Freezer status']}</span></p>
            <p>{details['Age']} years old | {details['Energy use']} kwh/Day</p>
            <p>Capacity: {occupied_shelves} / {total_shelves}</p>
            <div class="capacity">{capacity_html}</div>
            <div class="scrollable">
                <table id="contentsTable_{details['Freezer number']}">
                    <tr>
                        <th>Shelf</th>
                        <th>Library</th>
                        <th>Count</th>
                    </tr>
        """

        library_counts = shelf_info.groupby(['shelf', 'library']).size().reset_index(name='Count')
        for _, row in library_counts.iterrows():
            html_content += f"""
                    <tr>
                        <td>{row['shelf']}</td>
                        <td>{row['library']}</td>
                        <td>{row['Count']}</td>
                    </tr>
            """

        html_content += """
                </table>
            </div>
        </div>
        """

    html_content += """
    </div>
</body>
</html>
"""

    return html_content

# Generate HTML for individual freezer pages
def generate_freezer_page(freezer_number, status_df, database_df):
    details, shelf_info = extract_freezer_info(freezer_number, status_df, database_df)

    # Replace NaN values with blanks
    shelf_info = shelf_info.fillna('')

    # Calculate capacity
    total_shelves = shelf_info['shelf'].nunique()
    occupied_shelves = shelf_info[shelf_info['library'] != '']['shelf'].nunique()
    free_shelves = total_shelves - occupied_shelves

    # Create capacity visualization
    shelf_numbers = shelf_info['shelf'].unique()
    capacity_html = ""
    for shelf in shelf_numbers:
        if shelf_info[shelf_info['shelf'] == shelf]['library'].iloc[0] != '':
            capacity_html += f'<div class="shelf occupied" onclick="filterShelf(\'{shelf}\')">{shelf}</div>'
        else:
            capacity_html += f'<div class="shelf free" onclick="filterShelf(\'{shelf}\')">{shelf}</div>'

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Freezer Information - {freezer_number}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        h1 {{ text-align: center; }}
        .freezer-info {{ max-width: 1200px; margin: 0 auto; text-align: left; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .logo-right {{ width: 100px; }}
        .logo-left {{ width: 100px; }}
        .condition {{ color: {'red' if details['Freezer condition'].lower() == 'dirty' else 'green'}; }}
        .status {{ display: inline-block; padding: 2px 6px; border-radius: 4px; color: white; }}
        .status.offer-out {{ background-color: #FFB6C1; color: black; }}
        .status.dispose {{ background-color: #f47979; }}
        .status.keep {{ background-color: lightblue; }}
        .logo-container {{ display: flex; justify-content: space-between; }}
        .capacity {{ display: flex; align-items: center; }}
        .shelf {{
            width: 60px;
            height: 20px;
            margin: 0px;
            border: 1px solid #ccc;
            box-sizing: border-box;
            text-align: center;
            line-height: 20px;
            cursor: pointer;
        }}
        .occupied {{ background-color: orange; }}
        .free {{ background-color: green; }}
        .clear-selection {{
            margin-top: 10px;
            padding: 5px 10px;
            background-color: #007BFF;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 4px;
        }}
    </style>
    <script>
        function filterTable() {{
            var input, filter, table, tr, td, i, j, txtValue;
            input = document.getElementById("filterInput").getElementsByTagName("input");
            filter = [];
            for (i = 0; i < input.length; i++) {{
                filter.push(input[i].value.toUpperCase());
            }}
            table = document.getElementById("contentsTable");
            tr = table.getElementsByTagName("tr");

            for (i = 2; i < tr.length; i++) {{
                tr[i].style.display = "none";
                td = tr[i].getElementsByTagName("td");
                for (j = 0; j < td.length; j++) {{
                    if (td[j]) {{
                        txtValue = td[j].textContent || td[j].innerText;
                        if (txtValue.toUpperCase().indexOf(filter[j]) > -1) {{
                            tr[i].style.display = "";
                        }} else {{
                            tr[i].style.display = "none";
                            break;
                        }}
                    }}
                }}
            }}
        }}

        function filterShelf(shelf) {{
            var table, tr, td, i, txtValue;
            table = document.getElementById("contentsTable");
            tr = table.getElementsByTagName("tr");

            for (i = 2; i < tr.length; i++) {{
                tr[i].style.display = "none";
                td = tr[i].getElementsByTagName("td");
                if (td[0]) {{
                    txtValue = td[0].textContent || td[0].innerText;
                    if (txtValue.indexOf(shelf) > -1) {{
                        tr[i].style.display = "";
                    }}
                }}
            }}
        }}

        function clearFilter() {{
            var table, tr, i;
            table = document.getElementById("contentsTable");
            tr = table.getElementsByTagName("tr");

            for (i = 2; i < tr.length; i++) {{
                tr[i].style.display = "";
            }}
        }}
    </script>
</head>
<body>
    <div class="logo-container">
        <img src="Sanger_Logo.png" alt="Sanger Logo" class="logo-left">
        <img src="bio_r_logo.png" alt="BIO/R Logo" class="logo-right">
    </div>
    <h1>Freezer Information - {freezer_number}</h1>
    <div class="freezer-info">
        <h2>Details</h2>
        <p>Room Number: <a href="room_{details['Room Number']}.html">{details['Room Number']}</a></p>
        <p>Condition: <span class="condition">{details['Freezer condition']}</span></p>
        <p>Status: <span class="status {details['Freezer status'].lower()}">{details['Freezer status']}</span></p>
        <p>Age: {details['Age']} years</p>
        <p>Energy Use: {details['Energy use']} kwh/Day</p>
        <p>Capacity: {occupied_shelves} / {total_shelves}</p>
        <div class="capacity">{capacity_html}</div>
        <button class="clear-selection" onclick="clearFilter()">Clear selection</button>
        <h2>Contents</h2>
        <table id="contentsTable">
            <tr>
                <th>Shelf</th>
                <th>Library</th>
                <th>Sub-library Name</th>
                <th>Alt. Library Name</th>
                <th>Description</th>
                <th>Well Format</th>
                <th>Copy Type</th>
                <th>Plate Number</th>
            </tr>
            <tr id="filterInput">
                <td><input type="text" onkeyup="filterTable()" placeholder="Filter Shelf"></td>
                <td><input type="text" onkeyup="filterTable()" placeholder="Filter Library"></td>
                <td><input type="text" onkeyup="filterTable()" placeholder="Filter Sub-library Name"></td>
                <td><input type="text" onkeyup="filterTable()" placeholder="Filter Alt. Library Name"></td>
                <td><input type="text" onkeyup="filterTable()" placeholder="Filter Description"></td>
                <td><input type="text" onkeyup="filterTable()" placeholder="Filter Well Format"></td>
                <td><input type="text" onkeyup="filterTable()" placeholder="Filter Copy Type"></td>
                <td><input type="text" onkeyup="filterTable()" placeholder="Filter Plate Number"></td>
            </tr>
    """
    
    for _, row in shelf_info.iterrows():
        html_content += f"""
        <tr>
            <td>{row['shelf']}</td>
            <td>{row['library']}</td>
            <td>{row['sub-library name']}</td>
            <td>{row['alt. library name']}</td>
            <td>{row['description']}</td>
            <td>{row['well_format']}</td>
            <td>{row['copy_type']}</td>
            <td>{row['plate_number']}</td>
        </tr>
        """
    
    html_content += """
        </table>
    </div>
</body>
</html>
    """
    
    return html_content

# Generate HTML for all rooms and save to files
def generate_all_html():
    freezer_data = {}
    for room in unique_rooms:
        html_content = generate_room_html(room, freezer_status, freezer_database)
        output_path = f'room_{room}.html'
        with open(output_path, 'w') as file:
            file.write(html_content)
        
        # Generate individual freezer pages
        room_freezers = freezer_status[freezer_status['Room Number'] == room]['Freezer name'].unique()
        for freezer in room_freezers:
            freezer_html = generate_freezer_page(freezer, freezer_status, freezer_database)
            freezer_output_path = f'freezer_{freezer}.html'
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
    
    # Generate search.js file
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

    // If no results on current page, search other pages
    if (Array.from(freezers).every(f => f.style.display === 'none')) {
        searchOtherPages(filter);
    }
}

function searchOtherPages(filter) {
    fetch('freezer_data.json')
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
            resultsList += `<li><a href="freezer_${result.freezer}.html">${result.freezer}</a> (Room ${result.room})</li>`;
        });
        resultsList += '</ul>';
        freezersDiv.innerHTML += resultsList;
    }
}
    """
    
    with open('search.js', 'w') as file:
        file.write(search_js)
    
    # Save freezer data as JSON for search functionality
    with open('freezer_data.json', 'w') as file:
        json.dump(freezer_data, file)

if __name__ == "__main__":
    generate_all_html()
    generate_home_page(freezer_status, unique_rooms)
    print("HTML pages generated for each room and individual freezers.")
    print("Home page generated.")

    # Print the first few rows of each dataframe to verify the changes
    print("\nFirst few rows of Freezer Status:")
    print(freezer_status.head())
    print("\nFirst few rows of Freezer Database:")
    print(freezer_database.head())