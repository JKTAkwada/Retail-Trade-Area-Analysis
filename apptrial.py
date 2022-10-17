pip install streamlit
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import openrouteservice as openrouteservice
from openrouteservice import client

from folium import Marker
from folium.plugins import MarkerCluster

#Geopy's Nominatim
from geopy.geocoders import Nominatim

#Scipy's Spatial
from scipy import spatial


import requests
from io import StringIO
from io import BytesIO




wards = gpd.read_file('https://github.com/JayRolla/Team-27-/raw/main/Wards.zip')
#The population data is in csv file and contains data on population and income
population = pd.read_csv('https://raw.githubusercontent.com/JayRolla/Team-27-/main/Popdata.csv')
type_dict = {'WARD_NAME': 'int64'}
type_dict1 = {'WARD_NAME': 'int64',
             'Population_Density (People/Sq Km)': 'float64'}
wards = wards.astype(type_dict)
population = population.astype(type_dict1)
new_gpd = pd.merge(population, wards, on = 'WARD_NAME', how = 'right')
new_gpd = new_gpd[['OBJECTID', 'WARD_NAME', 'Total_Poplation', 'Households', 'Population_Density (People/Sq Km)', 'Average_Annual_Household_Income (Rands)', 'Average_annual_retail_spend (Rands)', 'geometry']]
new_gpd = gpd.GeoDataFrame(new_gpd)
#Add the coordinates for the default locations
lct1 = [[-34.09987438515951, 18.85273548861275]]
lct2 = [[-33.93514743516671, 18.676218389656704]]
lct3 = [[-33.90905058860111, 18.564177161133983]]

#Create the function to be executed when the markers change position

def handle_observe(event):
  event_owner = event['owner']
  #Capture the location of the marker
  loci = event_owner.location
  #Add location to the marker's location list
  lct1.append(loci)
def handle_observe1(event):
  event_owner = event['owner']
  #Capture the location of the marker
  loci1 = event_owner.location
  #Add location to the marker's location list
  lct2.append(loci1)
def handle_observe2(event):
  event_owner = event['owner']
  #Capture the location of the marker
  loci2 = event_owner.location
  #Add location to the marker's location list
  lct3.append(loci2)

# center = (-33.9289920, 18.4173960)
# m = Map(center=center, basemap=basemaps.CartoDB.Positron, zoom=9)
# #Create three markers, set the default location
# loc1 = Marker(location= lct1[-1])
# loc2 = Marker(location= lct2[-1])
# loc3 = Marker(location= lct3[-1])
# #Add the markers to the map
# m.add(loc1)
# m.add(loc2)
# m.add(loc3)
#
# #Instruct folium to observe the markers and execute the functions defined earlier when the markers change position
# loc1.observe(handle_observe, 'location')
# loc2.observe(handle_observe1, 'location')
# loc3.observe(handle_observe2, 'location')
# #Add the third selection as a geojson object
# # geo_data = GeoData(geo_dataframe = selection3, name = 'Viable locations')
# # #Add the data as a layer
# # m.add(geo_data)
# #Add full screen functionality
# m.add(FullScreenControl())
# #Save the output to html
# m.save(outfile= "viable.html")
# #Display the map
# st_map = st_folium(m, width=700, height=450)

#capture the last location that was added to the locations list.
#Reverse the coordinates since folium uses a different format.
#Change it to a list to make it useable
location1 = list(reversed(lct1[-1]))
location2 = list(reversed(lct2[-1]))
location3 = list(reversed(lct3[-1]))

# Provide your personal API key
api_key = '5b3ce3597851110001cf62480ac62be4cc3747a890840c0cfde8bd1d'
#Instruct openroute service to use the api key provided
ors = client.Client(key=api_key)

# Set up folium map
map1 = folium.Map(location=([-33.9249, 18.4241]), zoom_start=10)
#we create the locations of the stores based on the last positions of the markers in the above map
loca1 = [location1]
loca2 = [location2]
loca3 = [location3]
    # Set up the apartment dictionary with real coordinates
apartments = {'first': {'location': location1}, 'second': {'location': location2},' third': {'location': location3}}
# Request of isochrones with 20 minute walking.
params_iso = {'profile': 'driving-car', 'range': [900], 'attributes': ['total_pop']}  # Get population count for isochrones
for name, apt in apartments.items():
    params_iso['locations'] = [apt['location']]  # Add apartment coords to request parameters
    apt['iso'] = ors.isochrones(**params_iso)  # Perform isochrone request
    folium.features.GeoJson(apt['iso']).add_to(map1)  # Add GeoJson to map
    folium.map.Marker(list(reversed(apt['location'])),  # reverse coords due to weird folium lat/lon syntax
                  icon=folium.Icon(color='lightgray',
                                   icon_color='#cc0000',
                                   icon='home',
                                   draggable = True,
                                   prefix='fa',
                                   ),
                  popup=name,
                  ).add_to(map1)
    # Add apartment locations to map
    #Add fullscreen functionality
folium.plugins.Fullscreen().add_to(map1)
    #Save the output to a html file
map1.save(outfile= "map6.html")
    #Display the output
st_map = st_folium(map1, width=700, height=450)
# Set up the apartment dictionary with real coordinates
apartments = {'first': {'location': location1},
              'second': {'location': location2},
              'third': {'location': location3}
              }

# Request of isochrones with 15 minute walking.
params_iso = {'profile': 'foot-walking',
              'range': [900],
              'attributes': ['total_pop']  # Get population count for isochrones
              }

for name, apt in apartments.items():
    params_iso['locations'] = [apt['location']]  # Add apartment coords to request parameters
    apt['iso'] = ors.isochrones(**params_iso)
#Create empty lists to save the location and the values of the parameter search within the isochrones
names = []
values = []
# Common request parameters
params_poi = {'request': 'pois',
              'sortby': 'distance'}

# POI categories according to
# https://giscience.github.io/openrouteservice/documentation/Places.html
categories_poi = {'Taxi stops': [607],
                  'Parking Available': [601],
                  'Competitors': [518]}
#Save the  the store
cats = list(categories_poi.keys())

for name, apt in apartments.items():
    apt['categories'] = dict()  # Store in pois dict for easier retrieval
    params_poi['geojson'] = apt['iso']['features'][0]['geometry']
    #print("\n{} location".format(name))
    names.append("{} location".format(name))#add the names of our location to the names list

    for typ, category in categories_poi.items():
        params_poi['filter_category_ids'] = category
        apt['categories'][typ] = dict()
        apt['categories'][typ]['geojson'] = ors.places(**params_poi)['features']  # Actual POI request
        #print(f"\t{typ}: {len(apt['categories'][typ]['geojson'])}")
        values.append(len(apt['categories'][typ]['geojson']))#Add the values to the list
def getrows(l):
  n = len(cats)
  return [l[i:i + n] for i in range(0, len(l), n)]
values = getrows(values)
locations_df = pd.DataFrame(values, columns = cats, index = names)
def negative(df):
  lis = df['Competitors']
  lis = lis * -1
  df['Competitors'] = lis
  lis1 = df.sum(axis='columns').values.tolist()
  xmin = min(lis1)
  xmax=max(lis1)
  for i, x in enumerate(lis1):
    lis1[i] = (x-xmin) / (xmax-xmin)
  lis1 = [x + 1 for x in lis1]
  df['Attractiveness']  = lis1
  return df
scaled = negative(locations_df)
cordinates1 = list(loca1) + cor_list
cordinates2 = list(loca2) + cor_list
cordinates3 = list(loca3) + cor_list
dest = [0]
ors = client.Client(key=api_key)
matrix1 = ors.distance_matrix(locations = cordinates1, destinations = dest, metrics = ['duration', 'distance'], units = 'km')
matrix2 = ors.distance_matrix(locations = cordinates2, destinations = dest, metrics = ['duration', 'distance'], units = 'km')
matrix3 = ors.distance_matrix(locations = cordinates3, destinations = dest, metrics = ['duration', 'distance'], units = 'km')
def flatten(l):
  list_l = [item for sublist in l for item in sublist]
  list_l = list_l[1:]
  return list_l
loc1_dist = flatten(matrix1['distances'])
loc2_dist = flatten(matrix2['distances'])
loc3_dist = flatten(matrix3['distances'])
Dist_dict = {'WARD_NAME' : w_names,
             'first location': loc1_dist,
             'second location': loc2_dist,
             'third location': loc3_dist}
distances = pd.DataFrame(Dist_dict)
distances = distances.set_index('WARD_NAME')
keys = [(x, y) for x in w_names for y in names]
neum = {}
for key in keys:
  neum[key]= scaled.loc[key[1], ['Attractiveness']][0]/distances.loc[key[0],key[1]]**2
Pijs={}
for key in keys:
    Pijs[key]= neum[key]/sum([v for k,v in neum.items() if k[0]== key[0]])
pop_gpd = new_gpd.copy()
pop_gpd  = pop_gpd.set_index('WARD_NAME')
### expected_per_key
exp_key={}

for key in keys:
    exp_key[key]= Pijs[key]* pop_gpd.loc[key[0],'Average_annual_retail_spend (Rands)']

exp_store= {}

for store in names:
    exp_store[store]= sum([v for k,v in exp_key.items() if k[1]==store])

exp_store
for location, sales in exp_store.items():
    st.text(location, ':', sales)



if __name__ == "__main__":
    main()



