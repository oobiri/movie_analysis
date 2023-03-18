import os
import requests
from requests_html import HTML
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# Function that retrieves a url and then returns the html text
def url_to_txt(url, filename=None, save=False):
    r = requests.get(url, headers={"Accept-Language": "en-US"})
    if r.status_code == 200:
        html_text = r.text
        if save: # Option to save the html as a file for later use
            with open(filename, 'w') as f:
                f.write(html_text)
        return html_text
    return None

def parse_and_extract(url):
    html_text = url_to_txt(url)

    r_html = HTML(html=html_text)
    table_class = '.mode-advanced'
    movie_container = r_html.find(table_class)

    titles = []
    runtimes = []
    mpaas = []
    ratings = []
    years = []

    for movie in movie_container[:]:
        if movie.find(".certificate",first=True) is not None:
            title = movie.find("a")[1].text
            titles.append(title)

            rating = movie.find('.ratings-imdb-rating',first=True).text
            ratings.append(rating)
        
            mpaa = movie.find(".certificate", first=True).text
            mpaas.append(mpaa)

            runtime = movie.find(".runtime", first=True).text
            runtimes.append(runtime)

            year = movie.find(".lister-item-year", first=True).text
            years.append(year)
    
    return titles, runtimes, mpaas, ratings, years

"""
first movie = start_asc
can no longer sort by asc once film number reaches 10,000 or page = 9950

stop_num = 10000
stop_page = 10000 - 50

num_pages = (stop_page - start_asc)/50
end_asc = start_asc + (int(num_pages) * 50) 

last_asc_film = end_asc + 49
start_desc = (num_titles - last_asc_film) + 2

last_desc_page = (start_desc - (int(start_desc/50) *50))
end_desc = last_desc_page - 50
"""
#9156 first 1990 film

def run(start_asc=2812, end_asc=9912, start_desc=0, end_desc = 9350, name='imdb_data'):
    assert isinstance(start_asc, int)
    assert isinstance(end_asc, int)
    assert (end_asc > start_asc)

    movie_titles = []
    movie_runtimes = []
    movie_mpaas = []
    movie_ratings = []
    movie_years = []

    """while start_asc <= end_asc:
        url = f'https://www.imdb.com/search/title/?title_type=feature&num_votes=5000,&languages=en&sort=release_date,asc&start={start_asc}&explore=genres&ref_=adv_prv'
        titles, runtimes, mpaas, ratings, years = parse_and_extract(url)
        movie_titles.extend(titles)
        movie_runtimes.extend(runtimes)
        movie_mpaas.extend(mpaas)
        movie_ratings.extend(ratings)
        movie_years.extend(years)

        start_asc += 50

    while start_desc >= end_desc:
        url = f'https://www.imdb.com/search/title/?title_type=feature&num_votes=5000,&languages=en&sort=release_date,desc&start={start_desc}&explore=genres&ref_=adv_nxt'
        titles, runtimes, mpaas, ratings, years = parse_and_extract(url)
        movie_titles.extend(titles)
        movie_runtimes.extend(runtimes)
        movie_mpaas.extend(mpaas)
        movie_ratings.extend(ratings)
        movie_years.extend(years)

        start_desc -= 50
    """

    #test
    while start_desc <= end_desc:
        url = f'https://www.imdb.com/search/title/?title_type=feature&num_votes=5000,&languages=en&sort=release_date,desc&start={start_desc}&explore=genres&ref_=adv_nxt'
        titles, runtimes, mpaas, ratings, years = parse_and_extract(url)
        movie_titles.extend(titles)
        movie_runtimes.extend(runtimes)
        movie_mpaas.extend(mpaas)
        movie_ratings.extend(ratings)
        movie_years.extend(years)

        start_desc += 50


    imdb_df = pd.DataFrame({'Title': movie_titles,
    'Runtime': movie_runtimes,
    'MPAA Rating': movie_mpaas,
    'IMDb Score': movie_ratings,
    'Release Year': movie_years})

    path = os.path.join(BASE_DIR, 'data', 'raw')
    os.makedirs(path, exist_ok=True)
    file_path = os.path.join(path, f'{name}.csv')
    imdb_df.to_csv(file_path, index=False)

if __name__ == "__main__":
    run()