# import flask, redirect and template rendering functionality
from flask import Flask, redirect, render_template

# used for api calls and caching
import requests
import requests_cache

# used to get IDs out of movie URLS
import re

# define app name
app = Flask(__name__)

# set host and port to desired values
app.config['SERVER_NAME'] = 'localhost:8000'

# set requests cache. save to memory and expire after 60 seconds
requests_cache.install_cache(
    cache_name='movies_cache', backend='memory', expire_after=60)

# set base url for Ghibli REST API requests
API_BASE_URL = 'https://ghibliapi.herokuapp.com/'


# redirect to /movies page. no content on index
@app.route("/")
def index():
    return redirect("/movies")


# get data, check for ID matches and render template with result
@app.route("/movies")
def movies():

    # functions to get movie and people data
    movies = getMovies()
    people = getPeople()

    # check if any of the functions threw an error.
    if movies == None or people == None:
        print("Something went wrong. check previous output.")
        return "No data found", 400

    # iterate over movies and people
    for movie in movies:

        movie['people'] = [person['name']
                           for person in people if movie['id'] in person['films']]

    # render template and hand over movie list of dictionaries
    return render_template("movies.html", movies=movies)


def getMovies():

    # call the API
    movies_json = callAPI('films')

    # return list of dictionaries containing only id, title and empty people list for each movie
    return [{"id": movie['id'], "title": movie['title'], "people": []} for movie in movies_json]


def getPeople():

    # call API for all people
    people_json = callAPI('people')

    # initialize people list
    people = []

    # fill people list with data
    for person in people_json:

        # set regex pattern
        re_pattern = r'(?<=films\/).*$'

        # get film ids via regex pattern out of every persons films
        # API data contains a URL to each film, we only need the id for comparison
        person_films = [re.search(re_pattern, film).group()
                        for film in person['films']]

        # populate person dictionary and append to people list
        people.append({
            "id":       person['id'],
            "name":     person['name'],
            "films":    person_films
        })

    return people


# make GET request to Ghibli Api on given endpoint
def callAPI(endpoint):

    # call the API, on error print exception message and return None
    try:
        response = requests.get(API_BASE_URL + endpoint)
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return None

    return response.json()


# starting point
app.run()
