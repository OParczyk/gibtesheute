import datetime
import json

from flask import Blueprint, render_template, url_for, redirect

import requests

from gibtesheute.main.forms import SearchForm

main = Blueprint('main', __name__)

__mealcache = None
__mealcache_date = datetime.datetime.min


def mealcache():
    # Alte Mensa: 51.0269203, 13.7264508
    # HSZ: 51.0288985,13.7282453
    # xkcd: 2170
    def sq_distance(canteen, from_point=(51.0269203, 13.7264508)):
        canteen_coords=canteen['coordinates']
        latitude_diff=canteen_coords[0]-from_point[0]
        longitude_diff=canteen_coords[1]-from_point[1]

        return latitude_diff**2+longitude_diff**2

    def update():
        global __mealcache
        global __mealcache_date
        today = datetime.date.today()

        all_canteens = requests.get(
            "https://api.studentenwerk-dresden.de/openmensa/v2/canteens")
        if all_canteens.status_code != 200:
            return render_template('error.html',
                                   reason="could not query canteens")
        all_canteens = json.loads(all_canteens.content)
        filtered_canteens=[]
        for canteen in all_canteens:
            if canteen['address'].find('Dresden') == -1:
                continue

            filtered_canteens.append(canteen)

        filtered_canteens.sort(key=lambda x: sq_distance(x))

        all_meals = {}
        for canteen in filtered_canteens:
            meals = requests.get(
                f"https://api.studentenwerk-dresden.de/openmensa/v2/canteens/{canteen['id']}/days/{today}/meals")
            if meals.status_code != 200:
                continue
            meals = json.loads(meals.content)
            meals = [meal for meal in meals if 'Studierende' in meal['prices']]
            if meals:
                all_meals[canteen['name']] = meals
        __mealcache = all_meals
        __mealcache_date = datetime.datetime.now()

    if __mealcache_date + datetime.timedelta(
            hours=2) <= datetime.datetime.now():
        print("updating")
        update()

    return __mealcache


@main.route("/", methods=['GET', 'POST'])
def home():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('main.search', query=form.query.data))

    return render_template('home.html', form=form)


@main.route("/<query>/")
def search(query: str):
    canteens = mealcache()
    results = {}
    for canteen in canteens:
        for meal in canteens[canteen]:
            if meal['name'].upper().find(query.upper()) != -1:
                if canteen not in results:
                    results[canteen] = []
                results[canteen].append(meal)
    return render_template('query.html', query=query, results=results)


@main.route("/about")
def about():
    return render_template('about.html', title='About')
