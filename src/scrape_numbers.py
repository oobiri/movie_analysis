import os
import sys
import requests
from requests_html import HTML
import pandas as pd
from datetime import date, datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# Function that retrieves a url and then returns the html text
def url_to_txt(url, filename=None, save=False):
    r = requests.get(url)
    if r.status_code == 200:
        html_text = r.text
        if save: # Option to save the html as a file for later use
            with open(filename, 'w') as f:
                f.write(html_text)
        return html_text
    return None

def parse_and_extract(url, name='1990', file_num=1):
    html_text = url_to_txt(url)
    if html_text == None:
        return False

    r_html = HTML(html=html_text)
    table_class = "#page_filling_chart"
    r_table = r_html.find(table_class)

    # print(r_table)
    table_data = []
    header_names = []

    if len(r_table) == 0:
        return False
    # Creating a list of lists that will be turned into a csv later
    parsed_table = r_table[1] # parses the table
    rows = parsed_table.find('tr') # tr stands for table row inside html
    header_row = rows[0] # assume first row is the header row
    header_cols = header_row.find("th")
    header_names = [x.text for x in header_cols]
    header_names[0] = 'Opening Weekend Rank' # col #1 was blank leading to issues during analysis
    header_names[2] = 'Worldwide Release' # full name was not captured

# loops through all the rows
    for row in rows[1:]:
        # print(row.text)
        cols = row.find("td")
        row_data = []
        for i, col in enumerate(cols): # loops through all the columns
            # print(i, col.text, '\n\n')
            row_data.append(col.text) # each column is put in a list of its own based on a specific iteration that corresponds to its posittion in the row data
        table_data.append(row_data)
    
    path = os.path.join(BASE_DIR, 'data', 'raw')
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, f'{name}-{file_num}.csv')
    df = pd.DataFrame(table_data, columns=header_names)
    df.to_csv(file_path, index=False)

    max_opening_rev = int(df['Opening Weekend\nRevenue'].iloc[-1].replace('$', '').replace(',', '')) #Extracts the last val, which is then used to set the next url
    max_opening_rev = max_opening_rev/1000000
    
    return True, max_opening_rev

def run(start_year=None, years_ago=0):
    if start_year == None: 
        start_year = date.today().year
    assert isinstance(start_year, int)
    assert isinstance(years_ago, int)
    assert len(f"{start_year}") == 4

    for i in range(0, years_ago+1):
        max_open = 'None'
        file_num = 1
        while max_open != 0: #moves onto the next year once the opening weekend revenue is found to be 0
            url = f'https://www.the-numbers.com/current/movies/report/All/All/All/All/All/All/All/All/All/None/None/{start_year}/{start_year}/None/None/None/None/None/{max_open}?show-release-date=On&view-order-by=opening-weekend-revenue&view-order-direction=desc&show-production-budget=On&show-opening-weekend-theaters=On&show-domestic-box-office=On&show-maximum-theaters=On&show-inflation-adjusted-domestic-box-office=On&show-international-box-office=On&show-opening-weekend-revenue=On&show-worldwide-box-office=On&show-worldwide-release-date=On&show-theatrical-distributor=On&show-genre=On&show-source=On&show-production-method=On&show-creative-type=On'
            finished, max_open = parse_and_extract(url, name=start_year, file_num=file_num)
            if finished:
                print(f"Finished {start_year}: Page - {file_num}")
            else:
                print(f"{start_year} Page - {file_num} not finished")
            file_num +=1
        start_year -=1

if __name__ == "__main__":
    try:
        start = int(sys.argv[1])
    except:
        start = None
    try: 
        count = int(sys.argv[2])
    except:
        count = 0
    run(start_year=start, years_ago=count)