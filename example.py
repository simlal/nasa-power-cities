from nasa_power_query import NasaPowerCities, get_nasapower_params
import random

# Instantiate a NasaPowerCities object from a list of city names
cities = ["Montreal", "Paris", "Tokyo"]
nasa_cities = NasaPowerCities(names=cities)
print(nasa_cities.names)

# Get the geocoding details using geopy and updates the object's attributes
nasa_cities.get_geocoding_details(min_delay_seconds=4)    # Provide additionnal kwargs to Nomatim.geolocator.geocode if needed
print(nasa_cities)
# Updated geocoding-related attributes
print(nasa_cities.addresses)    # Also updates 'coordinates' and 'geodetails' properties

# Get all the possible climatology params in NASA POWER
nasa_climatology_params = get_nasapower_params()

# Exmaple: Choose 3 random shorthand names from all params
nasa_clim_shorthands = list(nasa_climatology_params.keys())
random_params = random.choices(nasa_clim_shorthands, k=3)

# Fetch climatologies with a maximum of 20 params per query
nasa_cities.fetch_climatology(random_params)
print(nasa_cities.climatologies["Montreal"])

# Specify a year range
nasa_cities.fetch_climatology(
    climate_params=random_params,
    start=2015,
    end=2018
)
