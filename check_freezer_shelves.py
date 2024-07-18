import pandas as pd
from extract_freezer_info import extract_freezer_info

def check_freezer_shelves(freezer_status, freezer_database, output_file):
    freezers = freezer_status['Freezer name'].unique()
    report = []

    for freezer in freezers:
        details, shelf_info = extract_freezer_info(freezer, freezer_status, freezer_database)
        
        total_shelves = shelf_info['shelf'].nunique()
        occupied_shelves = 0
        
        for shelf in shelf_info['shelf'].unique():
            shelf_data = shelf_info[shelf_info['shelf'] == shelf]
            library_count = shelf_data['library'].dropna().count()
            
            if library_count == 0:
                report.append({
                    'Freezer': freezer,
                    'Shelf': shelf,
                    'Status': 'Empty'
                })
            else:
                report.append({
                    'Freezer': freezer,
                    'Shelf': shelf,
                    'Status': 'Occupied'
                })
                occupied_shelves += 1
        
        occupancy_rate = occupied_shelves / total_shelves if total_shelves != 0 else 0
        report.append({
            'Freezer': freezer,
            'Shelf': 'Total',
            'Status': f'Occupancy Rate: {occupancy_rate:.2%}'
        })
    
    report_df = pd.DataFrame(report)
    report_df.to_csv(output_file, index=False)
    print(f"Report generated and saved to {output_file}")

if __name__ == "__main__":
    # Example usage
    from load_data import load_data
    freezer_status, freezer_database = load_data()
    
    check_freezer_shelves(freezer_status, freezer_database, 'freezer_shelf_report.csv')
