from load_data import load_data
from generate_all_html import generate_all_html

if __name__ == "__main__":
    freezer_status, freezer_database = load_data()
    unique_rooms = freezer_status['Room Number'].unique()
    
    generate_all_html(freezer_status, freezer_database, unique_rooms)
    
    print("HTML pages generated for each room and individual freezers.")
    print("Home page generated.")
    print("\nFirst few rows of Freezer Status:")
    print(freezer_status.head())
    print("\nFirst few rows of Freezer Database:")
    print(freezer_database.head())