from extract_freezer_info import extract_freezer_info

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
        h1 {{ text-align: center; display: flex; align-items: center; justify-content: center; }}
        .freezer-info {{ max-width: 1200px; margin: 0 auto; text-align: left; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .logo-container {{ display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }}
        .logo-container img {{ margin-right: 10px; width: 100px; cursor: pointer; }}
        .home-logo {{ width: 25px; height: 25px; margin-right: 10px; }}
        .dashboard-title {{ display: flex; align-items: center; justify-content: center; }}
        .condition {{ color: {'red' if details['Freezer condition'].lower() == 'dirty' else 'green'}; }}
        .status {{ display: inline-block; padding: 2px 6px; border-radius: 4px; color: white; }}
        .status.offer-out {{ background-color: #FFB6C1; color: black; }}
        .status.dispose {{ background-color: #f47979; }}
        .status.keep {{ background-color: lightblue; }}
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
        <img src="../Sanger_Logo.png" alt="Sanger Logo">
        <img src="../bio_r_logo.png" alt="BIO/R Logo">
    </div>
    <h1 class="dashboard-title">
        <a href="../HomePage/index.html"><img src="../home.jpg" alt="Home Logo" class="home-logo"></a>
        Freezer Information - {freezer_number}
    </h1>
    <div class="freezer-info">
        <h2>Details</h2>
        <p>Room Number: <a href="../Rooms/room_{details['Room Number']}.html">{details['Room Number']}</a></p>
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
