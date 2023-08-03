from typing import List, Dict
from functools import partial

import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter 

class NasaPowerCities:
    def __init__(self, names: List[str]) -> None:
        self._names = names

        self._addresses = None
        self._coordinates = None
        self._geodetails = None
    
    @property
    def names(self) -> List[str]:
        """
        Retrieves or sets the names list

        Args:
            ___ (list[str]): The new list of cities names.

        Returns:

        Raises:
        """
        return self._names
    
    @names.setter
    def names(self, value: List[str]) -> None:
        if not isinstance(value, list):
            raise TypeError(f"'names' must be a list, received {type(value).__name__}")
        
        if not all([isinstance(city, str) for city in value]):
            raise TypeError(f"All cities inside the 'names' list must be strings.")
        
        self._names = value
    
    
    
    @property
    def addresses(self) -> List[str]:
        """
        Retrieves the cities geopy addresses.

        Returns:
            List[str]: A list of strings containing the geopy addresse for the 'name' query.
        """
        return self._addresses
    
    @property
    def coordinates(self) -> Dict[str, Dict[str, float]]:
        """
        Retrieves the cities latitude and longitude coordinates extracted from geopy.

        Returns: 
            Dict[str, Dict[str, float]: A nested dictionary where the outer dict key is the 
                given city name in 'names' attribute. The corresponding value for each key is another
                dict which contains the latitude and longitude values as float.
        """
        return self._coordinates
    
    @property
    def geodetails(self) -> Dict[str, dict]:
        """
        Retrieves the cities geographical information details from the geopy request.

        Returns:
            Dict[str, dict]: A nested dictionary where the outer dict key is the 
                given city name in 'names' attribute. The corresponding value for each key is the json
                response from the geopy query.
        """
        return self._geodetails

    def __str__(self) -> str:
        cities_names = ", ".join(self._names)
        return cities_names
        
    def get_geocoding_details(self, min_delay_seconds: float=3, **kwargs):
        
        # Set the geocode object once with specified kwargs
        geolocator = Nominatim(user_agent="NasaPowerCities")
        geocode_kwargs = {k: v for k, v in kwargs.items()}
        timeout_arg = geocode_kwargs.pop("timeout", 10)
        custom_geocode = partial(geolocator.geocode, timeout=timeout_arg, **geocode_kwargs)

        geocode = RateLimiter(custom_geocode, min_delay_seconds=min_delay_seconds)    # Single threaded request with 1s delay

        # Update addresses, coordinates, geodetails attributes from geocode query data
        addresses = []
        coordinates_container = {}
        geodetails_container = {}
        
        for city_name in self._names:
            coordinates = {}

            print(f"Fetching geocoding information for city of {city_name}...")
            try:
                location = geocode(city_name)
            except Exception as e:
                print(e)
            
            if location:
                addresses.append(location.address)
                
                coordinates["latitude"] = location.latitude
                coordinates["longitude"] = location.longitude
                coordinates_container[city_name] = coordinates

                geodetails_container[city_name] = location.raw
        
        self._addresses = addresses
        self._coordinates = coordinates_container
        self._geodetails = geodetails_container
        
        print("Done!")
    
    