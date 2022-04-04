import json
import argparse
import csv
import glob


def load_data(filename):
    with open(filename, "r") as json_file:
        return json.loads(json_file.read())


def fetch_activities(timelineobjects):
    count_of_activities = 0
    activities = []
    for obj in timelineobjects:
        if is_activity(obj):
            count_of_activities += 1
            activities.append(obj.get('activitySegment'))
    return activities


def fetch_places_visited(timelineobjects):
    count_of_places = 0
    places = []
    for obj in timelineobjects:
        if is_place(obj):
            count_of_places += 1
            places.append(obj.get('placeVisit'))
    return places


def is_activity(timelineobject):
    return timelineobject.get('activitySegment') is not None


def is_place(timelineobject):
    return timelineobject.get('placeVisit') is not None


def find_end_place(travel_end_time, places):
    for place in places:
        duration = place.get('duration')
        start_time = duration.get('startTimestamp')
        if travel_end_time == start_time:
            return place.get('location').get('address')

    return None


def find_start_place(travel_start_time, places):
    for place in places:
        duration = place.get('duration')
        end_time = duration.get('endTimestamp')
        if travel_start_time == end_time:
            return place.get('location').get('address')

    return None


def meters_to_miles(meters):
    return meters / 1609.34


def build_routes(activities, places):
    routes = []
    for activity in activities:
        duration = activity.get('duration')
        start_time = duration.get('startTimestamp')
        end_time = duration.get('endTimestamp')
        end_address = find_end_place(end_time, places)
        start_address = find_start_place(start_time, places)
        distance = 0
        if activity.get('distance') is not None:
            distance = activity.get('distance')


        route = {}
        route['start_date'] = start_time
        route['end_date'] = end_time
        route['distance_in_miles'] = meters_to_miles(distance)
        route['start_address'] = start_address
        route['end_address'] = end_address

        routes.append(route)

    return routes


def write_routes_to_csv(routes, filename):
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["start_date", "end_date", "start_address", "end_address", "distance_in_miles"])
        for route in routes:
            writer.writerow([route.get('start_date'), route.get('end_date'),
                                                                route.get('start_address'),
                                                                route.get('end_address'),
                                                                route.get('distance_in_miles')])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='generate csv of route data from google maps.')
    parser.add_argument('input_file_dir', metavar='F', help='json file containing google map data export')
    parser.add_argument('output_file', metavar='F', help='csv file to write the report to')
    args = parser.parse_args()
    input_file_dir = args.input_file_dir

    global_routes = []
    for filename in glob.glob(input_file_dir+'/*.json'):
        data = load_data(filename)
        timelineobjects = data.get('timelineObjects')
        activities = fetch_activities(timelineobjects)
        places = fetch_places_visited(timelineobjects)
        routes = build_routes(activities, places)
        global_routes.extend(routes)

    outfile = args.output_file
    write_routes_to_csv(global_routes, outfile)

