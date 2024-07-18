from extract_freezer_info import extract_freezer_info

def generate_room_html(room_number, status_df, database_df, unique_rooms):
    filtered_freezer_status = status_df[status_df['Room Number'] == room_number]

    freezers = filtered_freezer_status['Freezer name'].unique()
    freezer_data = []

    for freezer in freezers:
        details, shelf_info = extract_freezer_info(freezer, status_df, database_df)
        freezer_data.append((details, shelf_info))

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Room {room_number}</title>
    <style>
        body {{ font-family: Arial, sans-serif; }}
        h1 {{ text-align: center; display: flex; align-items: center; justify-content: center; }}
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
        .logo-container {{ display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }}
        .logo-container img {{ margin-right: 10px; width: 100px; cursor: pointer; }}
        .home-logo {{ width: 25px; height: 25px; margin-right: 10px; }}
        .dashboard-title {{ display: flex; align-items: center; justify-content: center; }}
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
    <div class="logo-container">
        <img src="../Sanger_Logo.png" alt="Sanger Logo">
        <img src="../bio_r_logo.png" alt="BIO/R Logo">
    </div>
    <h1 class="dashboard-title">
        <a href="../HomePage/index.html"><img src="../home.jpg" alt="Home Logo" class="home-logo"></a>
        Freezer Information - Room {room_number}
    </h1>
    <div class="search-container">
        <input type="text" id="searchInput" onkeyup="search()" placeholder="Search for library, freezer number, or room..">
    </div>
    <div class="nav-container">
"""

    for room in unique_rooms:
        if room == room_number:
            html_content += f'<a href="room_{room}.html" class="current-room">{room}</a> | '
        else:
            html_content += f'<a href="room_{room}.html">{room}</a> | '

    html_content = html_content.rstrip(" | ")

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
            <h2><a href="../Freezer/freezer_{details['Freezer number']}.html">{details['Freezer number']}</a></h2>
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
