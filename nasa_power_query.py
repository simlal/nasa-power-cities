from typing import List, Dict, Union, Optional
from functools import partial
import requests
import time

import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class NasaPowerCities:
    def __init__(self, names: List[str]) -> None:
        """
        Initializes a new instance of the NasaPowerCities class.

        Args:
            names (List[str]): A list of city names to be handled.

        Returns:
            None
        """
        self._names = self._validate_names(names)

        self._addresses = None
        self._coordinates = None
        self._geodetails = None

        self._climatologies = None
    
    @property
    def names(self) -> List[str]:
        """
        Retrieves or sets the names attributes corresponding to list of names of cities

        Args:
            value (List[str]): The new list of cities names.

        Returns:
            List[str]: The list of cities names.
        """
        return self._names
    
    @names.setter
    def names(self, value: List[str]) -> None:     
        self._names = self._validate_names(value)
    
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
    
    @property
    def climatologies(self) -> Dict[str, dict]:
        """
        Retrieves the cities climatologies extracted from the NASA POWER API with the 'fetch_climatogolies' method.

        Returns:
            Dict[str, dict]: A nested dictionary where the outer dict key is the 
                given city name in 'names' attribute. The corresponding value for each key is the
                response content from the NASA POWER climatology API endpoint.
        """
        return self._climatologies

    def __str__(self) -> str:
        #* IMPROVE LAYOUT OF PRINT
        cities_info = [
            f"\t{city}, "
            f"latitude={self._coordinates[city]['latitude'] if self._coordinates else None}, "
            f"longitude={self._coordinates[city]['longitude'] if self._coordinates else None}\n" 
            for city in self._names
        ]
        return f"NasaPowerCities(\n{''.join(cities_info)})"
    

    @staticmethod
    def _validate_names(names: Union[list, str]) -> list:
        if isinstance(names, str):
            names = [names]
        if not isinstance(names, list):
            raise TypeError(f"'names' must be a str or a list, received {type(names).__name__}")
        
        if not all([isinstance(city, str) for city in names]):
            raise TypeError(f"All cities inside the 'names' list must be strings.")
        else:
            return names
        
    def get_geocoding_details(self, min_delay_seconds: float=3, **kwargs):
        """
        Retrieves geocoding details for the given cities and updates the relevant attributes.

        Args:
            timeout (int, optional): The maximum time to wait for geocoding results, in seconds. Defaults to 3.
            min_delay_seconds (float, optional): The minimum delay between requests, in seconds. Defaults to 1.
            **kwargs: Additional keyword arguments for geocoding.

        Returns:
            None
        """
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

    def fetch_climatology(self, 
        climate_params: List[str],
        community: str="SB",
        format: str="JSON",
        start: Optional[int]=None,
        end: Optional[int]=None
    ) -> None:
        """
        Fetches the climatology data for the given cities and parameters.

        Args:
            climate_params (List[str]): A list of climatology parameters to fetch (maximum of 20).
            community (str, optional): The community for the query. Defaults to "SB".
            format (str, optional): The response format, either "JSON" or other formats. Defaults to "JSON".
            start (Optional[int], optional): The start year for the range. Must be specified with 'end'. Defaults to None.
            end (Optional[int], optional): The end year for the range. Must be specified with 'start'. Defaults to None.

        Returns:
            None

        Raises:
            TypeError: If the input types do not match the expected types.
            ValueError: If the input values are not consistent with the expected constraints.
        """
        # climate_params type and amount validation
        if not isinstance(climate_params, list):
            raise TypeError(f"'climate_params' must be of type list, received{type(climate_params).__name__}")
        if len(climate_params) > 20:
            raise ValueError("The number of climate_params should be less than or equal to 20.")
        
        if not isinstance(community, str) and not isinstance(format, str):
            raise TypeError(
                f"'community' and 'format must be of type list, "
                f"received{type(community).__name__} and {type(format).__name__} respectively"
            )
        # 'Start' and 'End' type/value validation
        try:
            start = int(start) if start is not None else None
        except:
            raise TypeError(f"'start' must be of type int, received {type(start).__name__}")
        try:
            end = int(end) if end is not None else None
        except:
            raise TypeError(f"'end' must be of type int, received {type(end).__name__}")
        if ((start is None and end is not None) or
            (start is not None and end is None)):
            raise ValueError("Both 'start' and 'end' should be None if no year range desired")
        if isinstance(start, int) and isinstance(end, int):
            if start > end:
                raise ValueError("'start' should be smaller than end")
            
        # Base params for NASA POWER query
        base_params = {
            "parameters": ",".join(climate_params),
            "community": community,
            "format": format,
            "start": start,
            "end": end
        }
        if start is None and end is None:
            base_params.pop("start")
            base_params.pop("end")
        base_params_string = (
            f"Preparing to fetch climatologies with base parameters:\n"
            f"\t-parameters: {base_params['parameters']}\n"
            f"\t-community: {base_params['community']}\n"
            f"\t-format: {base_params['format']}"
        )
        if "start" in base_params and "end" in base_params:
            start_end_string = (
                f"\t-start: {base_params['start']}\n"
                f"\t-end: {base_params['end']}"
            )
            base_params_string += start_end_string
        print(base_params_string)

        # Prepare query params for each city        
        params_cities = {}
        if self._coordinates is None:
            raise ValueError("Get the geocoding for the cities first using the 'get_geocoding_details' method.")
        for city in self._names:
            if city not in self._coordinates:
                print(f"Will not fetch climatology for {city} since no valid coordinates.")
            else:
                base_params["latitude"] = self._coordinates[city]["latitude"]
                base_params["longitude"] = self._coordinates[city]["longitude"]

            params_cities[city] = base_params
        
        # Multiple single-threaded queries for all cities within the object
        url = "https://power.larc.nasa.gov/api/temporal/climatology/point"
        climatologies = {}
        
        for city in params_cities:
            try:
                print(f"Fetching climatology for {city}...")
                resp = requests.get(url, params=params_cities[city])
                resp.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Request error for {city}: {e}")
            if format == "JSON":
                try:
                    data = resp.json()
                except Exception as e:
                    print(f"Error parsing the data from {city}: {e}")
            else:
                data = resp.content
            climatologies[city] = data
            print("Done!")
            time.sleep(1)    # Avoid API request limit errors
        self._climatologies = climatologies

def get_nasapower_params(
            url: str="https://power.larc.nasa.gov/#resources", 
            webdriver_timeout: Union[float, int]=10,
            ele_id: str="parameterDictSelect",
        ) -> Dict[str, str]:
        """
        Retrieves NASA power parameters from the specified URL.

        Args:
            url (str, optional): The URL to scrape. Defaults to "https://power.larc.nasa.gov/#resources".
            webdriver_timeout (Union[float, int], optional): The maximum time to wait for the webdriver, in seconds. Defaults to 10.
            tag_name (str, optional): The HTML tag name to look for. Defaults to "option".
            skip (bool, optional): Whether to skip this operation. Defaults to True.

        Returns:
            List[str]: A list of NASA power parameters.
        """
        if not isinstance(url, str):
            raise TypeError(f"'url' must be a str, received {type(url).__name__}")
        try:
            webdriver_timeout = float(webdriver_timeout)
        except:
            raise TypeError(f"'webdriver_timeout' must be a float or int, received {type(webdriver_timeout).__name__}")
        
        # Perform client-side tag scraping
        print("Opening FireFox webdriver with Selenium 4...")
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        try:
            print(f"Requesting {url} for client-side scrapping...")
            driver.get(url=url)    # Navigate to url
            # Wait for select id tag to load before getting the source
            WebDriverWait(driver=driver, timeout=webdriver_timeout).until(
                EC.presence_of_element_located((By.ID, ele_id))
            )
            html = driver.page_source
            print(f"Full client-side rendered containing {ele_id} options.")
            
            # Extract all option from the select dropdown
            select_element = driver.find_element(By.ID, ele_id) 
            select = Select(select_element)
            # Wait for at least two option to be loaded within the select element
            WebDriverWait(driver, timeout=webdriver_timeout).until(
                lambda x: len(select.options) > 2
            )
            
            power_param_dict = {}
            for option in select.options:
                short_name = option.get_attribute("value")    # Abbreviation for the POWER params
                long_name = option.text    # Long name for the POWER params
                # Skip the option if it has no value or a specific text
                if short_name and long_name != "Select a parameter...":
                    power_param_dict[short_name] = long_name
        
        except NoSuchElementException as e:
            print(f"Could not find element of {id=}: Error {e}")
        except TimeoutException as e:
            print(f"Timed out waiting for element with ID '{ele_id}' to load. Error: {e}")
        finally:
            driver.quit()
        
        return power_param_dict

        