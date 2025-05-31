# utils.py
import networkx as nx
from geopy.distance import geodesic
import openrouteservice

# Replace this with your actual API key
ORS_API_KEY = "5b3ce3597851110001cf624887032465df0c4600b5f67f82870b581e"
client = openrouteservice.Client(key="5b3ce3597851110001cf624887032465df0c4600b5f67f82870b581e")

def get_road_distance_and_geometry(coord1, coord2):
    try:
        route = client.directions([coord1, coord2], profile='driving-car', format='geojson')
        distance = route['features'][0]['properties']['summary']['distance'] / 1000  # meters to km
        geometry = route['features'][0]['geometry']['coordinates']
        return distance, geometry
    except Exception as e:
        print(f"[ORS ERROR] Using fallback geodesic: {e}")
        distance = geodesic(coord1[::-1], coord2[::-1]).km
        return distance, [coord1, coord2]

def compute_mst(locations, connection_type="direct"):
    G = nx.Graph()
    coord_dict = {name: (lon, lat) for name, lat, lon in locations}
    
    for i in range(len(locations)):
        name1, lat1, lon1 = locations[i]
        for j in range(i+1, len(locations)):
            name2, lat2, lon2 = locations[j]
            coord1 = (lon1, lat1)
            coord2 = (lon2, lat2)
            
            if connection_type == "road":
                dist, geometry = get_road_distance_and_geometry(coord1, coord2)
                G.add_edge(name1, name2, weight=dist, geometry=geometry)
            else:
                dist = geodesic((lat1, lon1), (lat2, lon2)).km  
                
                G.add_edge(name1, name2, weight=dist, geometry=[coord1, coord2])
    return nx.minimum_spanning_tree(G)