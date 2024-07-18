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
