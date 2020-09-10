#####################################
# name: app.py                      #
# purpose: Kims Movielist task      #
# started on 2020/09/10             #
#####################################

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
        exit(1)

    # iterate over movies and people
    for movie in movies:
        for person in people:

            # check if movie id exists in a persons film IDs
            if movie['id'] in person['films']:

                # add name of person to this movies list of people
                movie['people'].append(person['name'])

    # render template and hand over movie list of dictionaries
    return render_template("movies.html", movies=movies)


def getMovies():

    # call the API, on error print exception message and return None
    try:
        response = requests.get('https://ghibliapi.herokuapp.com/films')
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return None

    # initialize movie list
    movies = []

    # fill movies with required data for each movie. Add empty list for people
    for movie in response.json():
        movie_data = {
            "id":       movie['id'],
            "title":    movie['title'],
            "people":   []
        }
        movies.append(movie_data)

    # return list of dictionaries
    return movies


def getPeople():

    # call the API, on error print exception message and return None
    try:
        resonse = requests.get('https://ghibliapi.herokuapp.com/people')
    except requests.exceptions.RequestException as err:
        print(f"Error: {err}")
        return None

    # initialize people list
    people = []

    # fill people list with data
    for person in resonse.json():

        # create new list to hold persons film IDs for later check
        person_films = []

        # scrape ID out of URL via regex searchs catchgroup and append to persons film list
        for film in person['films']:
            film_id = re.search(r'(?<=films\/).*$', film)
            person_films.append((film_id.group()))

        # populate person dictionary
        person_data = {
            "id":       person['id'],
            "name":     person['name'],
            "films":    person_films
        }

        # append dict to people list
        people.append(person_data)

    return people


# starting point
app.run()
