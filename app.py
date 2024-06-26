import streamlit as st
import requests
import openai
import sqlite3
from sqlite3 import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
weather_api_key = os.getenv('OPENWEATHERMAP_API_KEY')

# Database connection function
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('ecoroute.db')
    except Error as e:
        print(e)
    return conn

# Create the database table if it doesn't exist
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

# Function to get directions from OSRM
def get_directions(start_coords, end_coords):
    url = f'http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=false'
    response = requests.get(url)
    return response.json()

# Function to geocode an address using Nominatim
def geocode_address(address):
    url = f'https://nominatim.openstreetmap.org/search?q={address}&format=json'
    response = requests.get(url).json()
    if response:
        return float(response[0]['lat']), float(response[0]['lon'])
    return None, None

# Function to get weather data
def get_weather(location):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}'
    response = requests.get(url)
    return response.json()

# Function to get eco-driving tips from ChatGPT
def get_tips(route_info):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Provide eco-driving tips for the following route: {route_info}",
        max_tokens=150
    )
    return response.choices[0].text

# Function to store route information in SQLite
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

# Streamlit UI starts here
st.title('EcoRoute')  # App title
st.header('Find the most fuel-efficient route for your trips')  # App header

# Input fields for start and end locations
start_location = st.text_input('Start Location')
end_location = st.text_input('End Location')

# Button to trigger route finding
if st.button('Find Route'):
    if start_location and end_location:
        # Geocode the start and end locations
        start_coords = geocode_address(start_location)
        end_coords = geocode_address(end_location)

        # Check if geocoding was successful
        if start_coords and end_coords:
            # Get directions using OSRM
            directions = get_directions(start_coords, end_coords)
            # Get weather information for the end location
            weather = get_weather(end_location)
            # Get eco-driving tips from ChatGPT
            tips = get_tips(directions)

            # Store the route information in the database
            store_route(start_location, end_location, directions, weather, tips)

            # Display route information
            st.subheader('Route Information')
            st.write(directions)

            # Display weather information
            st.subheader('Weather Information')
            st.write(weather)

            # Display eco-driving tips
            st.subheader('Eco-Driving Tips')
            st.write(tips)
        else:
            st.error('Unable to geocode the provided addresses.')
    else:
        st.error('Please enter both start and end locations')
