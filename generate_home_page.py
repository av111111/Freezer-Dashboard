from extract_freezer_info import extract_freezer_info

def generate_home_page(status_df, database_df, unique_rooms):
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BioResource Freezer Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; }
        h1 { text-align: center; display: flex; align-items: center; justify-content: center; }
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
        .logo-container { display: flex; align-items: center; justify-content: center; margin-bottom: 20px; }
        .logo-container img { margin-right: 10px; width: 100px; cursor: pointer; }
        .home-logo { width: 25px; height: 25px; margin-right: 10px; }
        .dashboard-title { display: flex; align-items: center; justify-content: center; }
    </style>
    <script>
        function toggleRoom(roomId, imgElement) {
            var roomElement = document.getElementById(roomId);
            if (roomElement.classList.contains('collapsed')) {
                roomElement.classList.remove('collapsed');
                imgElement.src = '../expand-less.jpg';
            } else {
                roomElement.classList.add('collapsed');
                imgElement.src = '../expand-more.jpg';
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
        <img src="../Sanger_Logo.png" alt="Sanger Logo">
        <img src="../bio_r_logo.png" alt="BIO/R Logo">
    </div>
    <h1 class="dashboard-title">
        <a href="index.html"><img src="../home.jpg" alt="Home Logo" class="home-logo"></a>
        BioResource Freezer Dashboard
    </h1>
    <div class="search-container">
        <input type="text" id="searchInput" onkeyup="searchHomepage()" placeholder="Search for freezers or rooms..">
    </div>
    <div class="rooms-container">
"""

    for room in unique_rooms:
        html_content += f"""
        <div class="room">
            <h2><a href="../Rooms/room_{room}.html">{room}</a> <img src="../expand-less.jpg" class="collapse-button" onclick="toggleRoom('room_{room}_content', this)"></h2>
            <div id="room_{room}_content" class="room-content">
                <div class="freezers">
        """
        freezers_in_room = status_df[status_df['Room Number'] == room]['Freezer name'].unique()
        for freezer in freezers_in_room:
            details, shelf_info = extract_freezer_info(freezer, status_df, database_df)
            total_shelves = shelf_info['shelf'].nunique()
            occupied_shelves = shelf_info[shelf_info['library'] != '']['shelf'].nunique()
            html_content += f"""
                    <div class="freezer">
                        <h3><a href="../Freezer/freezer_{details['Freezer number']}.html">{details['Freezer number']}</a></h3>
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
    
    with open('HomePage/index.html', 'w') as file:
        file.write(html_content)
