# NASA POWER climatology API data consumption for cities

A simple Python3+ module to fetch climate data for cities using the NASA POWER API climatology endpoint. Be careful for rate limits on querries

## Installation
The module could be further customized but here's my simple implementation.

What's needed:
- Firefox browser
- Conda
- Python 3+

### Steps:
1. Install Firefox and Conda if not already done.
2. `git clone https://github.com/simlal/nasa-power-cities.git`
3. `cd nasa-power-cities`
4. `conda create -n nasa_power_env --file requirements.txt`
5. `conda activate nasa_power_env`

## Example usage
First instantiate a NasaPowerCities object from a single city name or a list of cities names.
```python
from nasa_power_query import NasaPowerCities, get_nasapower_params

# Instantiate a NasaPowerCities object from a list of city names
>>> cities = ["Montreal", "Paris", "Tokyo"]
>>> nasa_cities = NasaPowerCities(names=cities)
>>> print(nasa_cities.names)
['Montreal', 'Paris', 'Tokyo']
```

Then get the geocoding details for each city and update the object's properties

```python
# Get the geocoding details using geopy
>>> nasa_cities.get_geocoding_details(min_delay_seconds=4)    # Provide additionnal kwargs to Nomatim.geolocator.geocode if needed
Fetching geocoding information for city of Montreal...
Fetching geocoding information for city of Paris...
Fetching geocoding information for city of Tokyo...
Done!

>>> print(nasa_cities)
NasaPowerCities(
	Montreal, latitude=45.5031824, longitude=-73.5698065
	Paris, latitude=48.8534951, longitude=2.3483915
	Tokyo, latitude=35.6840574, longitude=139.7744912
)
# Updated geocoding-related attributes
>>> print(nasa_cities.addresses)    # Also updates 'coordinates' and 'geodetails' properties
['Montréal, Agglomération de Montréal, Montréal (région administrative), Québec, Canada', 'Paris, Île-de-France, France métropolitaine, France', '東京都, 日本']
```

Fetch all the possible parameters for the NASA POWER Climatology API endpoint using Selenium and client-side web scrapping.
```python
# Get all the possible climatology params in NASA POWER
>>> nasa_climatology_params = get_nasapower_params()
Opening FireFox webdriver with Selenium 4...
Requesting https://power.larc.nasa.gov/#resources for client-side scrapping...
Full client-side rendered containing parameterDictSelect options.

# Exmaple: Choose 3 random shorthand names from all params
>>> nasa_clim_shorthands = list(nasa_climatology_params.keys())
>>> random_params = random.choices(nasa_clim_shorthands, k=3)
```

Finally fetch all the climatologies for the cities in the NasaPowerCities objects for a given set of parameters
```python
# Fetch climatologies with a maximum of 20 params per query
>>> nasa_cities.fetch_climatology(random_params)
Preparing to fetch climatologies with base parameters:
	-parameters: T10M_MIN,CLOUD_AMT_01,TS_MIN
	-community: SB
	-format: JSON
Fetching climatology for Montreal...
Done!
Fetching climatology for Paris...
Done!
Fetching climatology for Tokyo...
Done!
>>> print(nasa_cities.climatologies["Montreal"])
{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [139.7744912, 35.6840574, 38.67]}, 'properties': {'parameter': {'TS_MIN': {'JAN': -2.36, 'FEB': -2.2, 'MAR': -1.23, 'APR': 0.31, 'MAY': 6.26, 'JUN': 10.38, 'JUL': 16.79, 'AUG': 17.67, 'SEP': 12.12, 'OCT': 7.9, 'NOV': 2.09, 'DEC': -0.82, 'ANN': -2.36}, 'T10M_MIN': {'JAN': -2.87, 'FEB': -2.38, 'MAR': -1.26, 'APR': 1.07, 'MAY': 6.45, 'JUN': 12.26, 'JUL': 16.14, 'AUG': 18.19, 'SEP': 12.17, 'OCT': 7.26, 'NOV': 2.1, 'DEC': -1.67, 'ANN': -2.87}, 'CLOUD_AMT_01': {'JAN': 40.88, 'FEB': 51.3, 'MAR': 56.64, 'APR': 60.09, 'MAY': 66.72, 'JUN': 80.23, 'JUL': 73.77, 'AUG': 62.32, 'SEP': 69.81, 'OCT': 64.95, 'NOV': 53.79, 'DEC': 44.07, 'ANN': 60.38}}}, 'header': {'title': 'NASA/POWER CERES/MERRA2 Native Resolution Climatology Climatologies', 'api': {'version': 'v2.4.4', 'name': 'POWER Climatology API'}, 'sources': ['power'], 'fill_value': -999.0, 'range': '20-year Meteorological and Solar Monthly & Annual Climatologies (January 2001 - December 2020)'}, 'messages': [], 'parameters': {'TS_MIN': {'units': 'C', 'longname': 'Earth Skin Temperature Minimum'}, 'T10M_MIN': {'units': 'C', 'longname': 'Temperature at 10 Meters Minimum'}, 'CLOUD_AMT_01': {'units': '%', 'longname': 'Cloud Amount at 01 GMT'}}, 'times': {'data': 13.567, 'process': 0.56}}

# Specify a year range
>>> nasa_cities.fetch_climatology(
    climate_params=random_params,
    start=2015,
    end=2018
)
```
