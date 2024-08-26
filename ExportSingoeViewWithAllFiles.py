import requests
import json
import csv
import os
import re
import pathlib

def export_all_files(apiKey, viewId, rootPath):
    view_data = export_grid_as_csv(apiKey, viewId)
    view_info = get_view_data(apiKey, viewId)
    filesPath = os.path.join(
        rootPath,
        re.sub(r'[^a-zA-Z0-9 ]', '', view_info['name']).strip(),
        "Files"
    )
    viewPath = os.path.dirname(filesPath)
    pathlib.Path(filesPath).mkdir(parents=True, exist_ok=True)

    # Save the CSV file
    with open(os.path.join(viewPath, re.sub(r'[^a-zA-Z0-9 ]', '', view_info['name']).strip() + '.csv'), 'w', encoding="UTF8", newline='') as file:
        file.write(view_data)
    
    file_column_names = get_file_column_name(apiKey, viewId)
    file_ids = []

    for column_name in file_column_names:
        file_ids.extend(get_file_ids_from_files_column(view_data, column_name))

    for item in file_ids:
        if item != '':
            for key, value in item.items():
                file_extension = get_file_extension(value)                        
                response = get_file_data(apiKey, viewId, value)    
                with open(os.path.join(filesPath, key + file_extension), 'wb') as f:
                    f.write(response.content)
                print('Binary response saved to file')

    # Optimization: Exit after processing the required view
    return  # Exit early since the required view has been processed

# Helper function definitions remain the same
def get_file_extension(filename):
    _, extension = os.path.splitext(filename)
    return extension

def get_file_data(apiKey, viewId, fileId):
    return gridly_api_call(apiKey, f"https://api.gridly.com/v1/views/{viewId}/files/{fileId}", False)

def get_file_ids_from_files_column(csv_string, header_name):
    rows = csv.DictReader(csv_string.splitlines())
    column_data = []
    for row in rows:
        if row[header_name]:
            column_data.append({row["Record ID"]: row[header_name]})
    return column_data

def get_file_column_name(apiKey, viewId):
    fileColumns = []
    try:
        columns = gridly_api_call(apiKey, f"https://api.gridly.com/v1/views/{viewId}")['columns']
        for column in columns:
            if 'type' in column and column['type'] == "files":
                fileColumns.append(column['name'])
    except Exception as e:
        print("View does not have columns:", e)
    return fileColumns

def export_grid_as_csv(apiKey, viewId):
    return gridly_api_call(apiKey, f"https://api.gridly.com/v1/views/{viewId}/export", False).text

def list_grids(apiKey, dbId):
    return gridly_api_call(apiKey, f"https://api.gridly.com/v1/grids?dbId={dbId}")

def list_databases(apiKey, projectId):
    return gridly_api_call(apiKey, f"https://api.gridly.com/v1/databases?projectId={projectId}")

def list_projects(apiKey):
    return gridly_api_call(apiKey, "https://api.gridly.com/v1/projects")

def get_views(apiKey, gridId):
    return gridly_api_call(apiKey, f"https://api.gridly.com/v1/views?gridId={gridId}")

def get_view_data(apiKey, viewId):
    return gridly_api_call(apiKey, f"https://api.gridly.com/v1/views/{viewId}")

def gridly_api_call(apiKey, url, js=True):
    headers = {
        'Authorization': f'ApiKey {apiKey}'
    }
    response = requests.get(url, headers=headers)
    if js:
        return response.json()
    else:
        return response

# Example usage
export_all_files("APIKEY", "VIEWID", r"ROOTPATH")
