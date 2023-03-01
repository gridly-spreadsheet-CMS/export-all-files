import requests
import json
import csv
import os
import re
import pathlib

def export_all_files(apiKey, rootPath):
    projects = list_projects(apiKey)
    for project in projects:
        databases = list_databases(apiKey, project['id'])
        for database in databases:
            grids = list_grids(apiKey, database['id'])
            for grid in grids:
                view = export_grid_as_csv(apiKey, grid['defaultAccessViewId'])
                filesPath = os.path.join(rootPath, re.sub(r'[^a-zA-Z0-9 ]', '', project['name']).strip(), re.sub(r'[^a-zA-Z0-9 ]', '', database['name']).strip(), re.sub(r'[^a-zA-Z0-9 ]', '', grid['name']).strip(), "Files")
                viewPath = os.path.dirname(filesPath)
                #print(filesPath)
                pathlib.Path(filesPath).mkdir(parents=True, exist_ok=True)
                with open(os.path.join(viewPath, re.sub(r'[^a-zA-Z0-9 ]', '', grid['name']).strip() + '.csv'), 'w', encoding="UTF8") as file:
                    writer = csv.writer(file)
                    writer.writerow(view)
                file_column_names = get_file_column_name(apiKey, grid['defaultAccessViewId'])
                file_ids = []
                for column_name in file_column_names:
                    file_ids.append(get_file_ids_from_files_column(view, column_name))
                
                for file_id in file_ids:
                    for id in file_id:
                        if id != '':
                            response = get_file_data(apiKey, grid['defaultAccessViewId'], id)    
                            #print(file_id)                 
                            with open(os.path.join(filesPath, id), 'wb') as f:
                                f.write(response.content)
                            print('Binary response saved to file')
                        
def get_file_data(apiKey, viewId, fileId):
    return gridly_api_call(apiKey, "https://api.gridly.com/v1/views/" + viewId + "/files/" + fileId, False)

def get_file_ids_from_files_column(csv_string, header_name):
    # Convert the CSV string into a list of dictionaries
    rows = csv.DictReader(csv_string.splitlines())
    # Extract the data from the desired column
    column_data = []
    for row in rows:
        column_data.append(row[header_name])
    return column_data

def get_file_column_name(apiKey, viewId):
    fileColumns = []
    try:
        columns = gridly_api_call(apiKey, "https://api.gridly.com/v1/views/" + viewId)['columns']
        for column in columns:
            if 'type' in column:
                if column['type'] == "files":
                    fileColumns.append(column['name'])
    except:
        print("View does not have columns")
    return fileColumns

def export_grid_as_csv(apiKey, viewId):
    return gridly_api_call(apiKey, "https://api.gridly.com/v1/views/" + str(viewId) + "/export", False).text

def list_grids(apiKey, dbId):
    return gridly_api_call(apiKey, "https://api.gridly.com/v1/grids?dbId=" + str(dbId))

def list_databases(apiKey, projectId):
    return gridly_api_call(apiKey, "https://api.gridly.com/v1/databases?projectId=" + str(projectId))

def list_projects(apiKey):
    return gridly_api_call(apiKey, "https://api.gridly.com/v1/projects")


def gridly_api_call(apiKey, url, js=True):
    payload={}
    headers = {
    'Authorization': 'ApiKey ' + apiKey
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    if js:
        return json.loads(response.text)
    else:
        return response

export_all_files("APIKEY", r"ROOTPATHFORFILES")