# Freezer Dashboard

This project generates a dashboard for monitoring freezer status and contents across multiple rooms. The data is automatically updated every 5 minutes.

## Setup

1. Clone this repository:
   ```
   git clone https://github.com/av111111/Freezer-Dashboard.git
   cd Freezer-Dashboard
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the update script:
   ```
   python update_and_push.py
   ```

This will start the automatic update process, which will refresh the data and push changes to GitHub every 5 minutes.

## Viewing the Dashboard

To view the dashboard, simply open any of the `room_X.html` files in your web browser. You can navigate between rooms using the links at the top of each page.

## Data Sources

The dashboard uses data from two Google Sheets:
- Freezer Status: [Link to your freezer status sheet]
- Freezer Database: [Link to your freezer database sheet]

## Contributing

If you'd like to contribute to this project, please fork the repository and submit a pull request with your changes.