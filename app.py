import streamlit as st
import googlemaps
import requests
import openai
import sqlite3
from sqlite3 import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize APIs with keys from environment variables
gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
openai.api_key = os.getenv('OPENAI_API_KEY')
weather_api_key = os.getenv('OPENWEATHERMAP_API_KEY')

# Database connection
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('ecoroute.db')
    except Error as e:
        print(e)
    return conn

def create_table():
    conn = create_connection()
    try:
        sql_create_routes_table = """ CREATE TABLE IF NOT EXISTS routes (
                                        id integer PRIMARY KEY,
                                        start_location text NOT NULL,
                                        end_location text NOT NULL,
                                        route_info text NOT NULL,
                                        weather_info text NOT NULL,
                                        tips text NOT NULL
                                    ); """
        conn.execute(sql_create_routes_table)
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

# Function to get directions from Google Maps
def get_directions(start, end):
    directions_result = gmaps.directions(start, end)
    return directions_result

# Function to get distance matrix from Google Maps
def get_distance_matrix(origins, destinations):
    distance_matrix_result = gmaps.distance_matrix(origins, destinations)
    return distance_matrix_result

# Function to geocode an address
def geocode_address(address):
    geocode_result = gmaps.geocode(address)
    return geocode_result

# Function to get weather data
def get_weather(location):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}'
    response = requests.get(url)
    return response.json()

# Function to get place details
def get_place_details(place_id):
    place_result = gmaps.place(place_id)
    return place_result

# Function to get eco-driving tips from ChatGPT
def get_tips(route_info):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Provide eco-driving tips for the following route: {route_info}",
        max_tokens=150
    )
    return response.choices[0].text

# Function to store route information
def store_route(start, end, route, weather, tips):
    conn = create_connection()
    try:
        sql_insert_route = """ INSERT INTO routes (start_location, end_location, route_info, weather_info, tips)
                               VALUES (?, ?, ?, ?, ?) """
        cur = conn.cursor()
        cur.execute(sql_insert_route, (start, end, str(route), str(weather), tips))
        conn.commit()
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

# Create the routes table if it doesn't exist
create_table()

# Streamlit UI
st.title('EcoRoute')
st.header('Find the most fuel-efficient route for your trips')

start_location = st.text_input('Start Location')
end_location = st.text_input('End Location')

if st.button('Find Route'):
    if start_location and end_location:
        directions = get_directions(start_location, end_location)
        distance_matrix = get_distance_matrix([start_location], [end_location])
        weather = get_weather(end_location)
        tips = get_tips(directions)

        # Store route information
        store_route(start_location, end_location, directions, weather, tips)

        st.subheader('Route Information')
        st.write(directions)

        st.subheader('Distance and Time')
        st.write(distance_matrix)

        st.subheader('Weather Information')
        st.write(weather)

        st.subheader('Eco-Driving Tips')
        st.write(tips)
    else:
        st.error('Please enter both start and end locations')
