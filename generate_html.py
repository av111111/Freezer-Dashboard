import pandas as pd

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
        'Energy use': freezer_info['Energy Consumption (kwh per day)']
    }
    
    # Filter the database_df for the given freezer number and extract unique shelves
    shelf_info = database_df[database_df['freezer'] == freezer_number]
    unique_shelves = shelf_info['shelf'].unique()
    
    # For each unique shelf, find unique library values and their counts
    shelf_details = []
    empty_shelves = []
    for shelf in unique_shelves:
        libraries = shelf_info[shelf_info['shelf'] == shelf]['library'].value_counts()
        if libraries.empty:
            empty_shelves.append(shelf)
        shelf_details.append((shelf, libraries))
    
    freezer_details['Empty shelves'] = empty_shelves
    
    return freezer_details, shelf_details

# Get unique room numbers
unique_rooms = freezer_status['Room Number'].unique()

# Function to generate HTML content for a single freezer
def generate_freezer_html(details, shelves):
    condition_color = "dirty" if details['Freezer condition'].lower() == "dirty" else "clean"
    
    # Determine the status class for coloring
    status_class = "offer-out"
    if details['Freezer status'].lower() == "dispose":
        status_class = "dispose"
    elif details['Freezer status'].lower() == "keep":
        status_class = "keep"
    elif details['Freezer status'].lower() == "offer out":
        status_class = "offer-out"
    
    empty_shelves_html = ""
    if len(details['Empty shelves']) > 0:
        empty_shelves_html = f"""
        <p>Empty shelves: {len(details['Empty shelves'])}
            <select>
                {"".join(f"<option>{shelf}</option>" for shelf in details['Empty shelves'])}
            </select>
        </p>
        """
    else:
        empty_shelves_html = "<p>Empty shelves: 0</p>"
    
    html_template = f"""
    <div class="freezer">
        <h2>{details['Freezer number']}</h2>
        <p class="{condition_color}">{details['Freezer condition']}</p>
        <p class="status {status_class}">{details['Freezer status']}</p>
        <p>{details['Age']} years old | {details['Energy use']} kwh/Day</p>
        {empty_shelves_html}
        <div class="scrollable">
            <table>
                <tr>
                    <th>Shelf</th>
                    <th>Library</th>
                    <th>Count</th>
                </tr>
    """
    for shelf, libraries in shelves:
        for library, count in libraries.items():
            html_template += f"""
                <tr>
                    <td>{shelf}</td>
                    <td>{library}</td>
                    <td>{count}</td>
                </tr>
            """
    html_template += """
            </table>
        </div>
    </div>
    """
    return html_template

# Generate HTML for all freezers in a specific room
def generate_room_html(room_number, status_df, database_df):
    # Filter the status dataframe for the given room number
    filtered_freezer_status = status_df[status_df['Room Number'] == room_number]

    # Extract information for all freezers in the room
    freezers = filtered_freezer_status['Freezer name'].unique()
    freezer_data = []

    for freezer in freezers:
        details, shelves = extract_freezer_info(freezer, status_df, database_df)
        freezer_data.append((details, shelves))

    # Generate HTML for all freezers
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Freezer Information - Room {room_number}</title>
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
        .scrollable {{ overflow-y: auto; height: 150px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 5px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .search-container {{ text-align: center; margin-bottom: 20px; }}
        .search-container input {{ padding: 5px; width: 300px; }}
    </style>
    <script>
        function search() {{
            var input, filter, freezers, freezer, h2, p, table, tr, td, i, j, txtValue;
            input = document.getElementById('searchInput');
            filter = input.value.toUpperCase();
            freezers = document.getElementsByClassName('freezer');

            for (i = 0; i < freezers.length; i++) {{
                freezer = freezers[i];
                h2 = freezer.getElementsByTagName('h2')[0];
                p = freezer.getElementsByTagName('p');
                table = freezer.getElementsByTagName('table')[0];
                tr = table.getElementsByTagName('tr');

                freezer.style.display = 'none';

                if (h2) {{
                    txtValue = h2.textContent || h2.innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {{
                        freezer.style.display = '';
                        continue;
                    }}
                }}

                for (j = 0; j < p.length; j++) {{
                    if (p[j]) {{
                        txtValue = p[j].textContent || p[j].innerText;
                        if (txtValue.toUpperCase().indexOf(filter) > -1) {{
                            freezer.style.display = '';
                            break;
                        }}
                    }}
                }}

                for (j = 1; j < tr.length; j++) {{
                    td = tr[j].getElementsByTagName('td');
                    for (var k = 0; k < td.length; k++) {{
                        if (td[k]) {{
                            txtValue = td[k].textContent || td[k].innerText;
                            if (txtValue.toUpperCase().indexOf(filter) > -1) {{
                                freezer.style.display = '';
                                break;
                            }}
                        }}
                    }}
                }}
            }}
        }}
    </script>
</head>
<body>
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

    for details, shelves in freezer_data:
        html_content += generate_freezer_html(details, shelves)

    html_content += """
    </div>
</body>
</html>
"""

    return html_content

# Generate HTML for all rooms and save to files
def generate_all_room_html():
    for room in unique_rooms:
        html_content = generate_room_html(room, freezer_status, freezer_database)
        output_path = f'room_{room}.html'
        with open(output_path, 'w') as file:
            file.write(html_content)

if __name__ == "__main__":
    generate_all_room_html()
    print("HTML pages generated for each room.")

    # Print the first few rows of each dataframe to verify the changes
    print("\nFirst few rows of Freezer Status:")
    print(freezer_status.head())
    print("\nFirst few rows of Freezer Database:")
    print(freezer_database.head())