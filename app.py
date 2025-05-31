import streamlit as st
from streamlit_folium import st_folium
import folium
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderUnavailable, GeocoderTimedOut
from utils import compute_mst  # make sure this returns a NetworkX Graph with edge attributes 'weight' and 'geometry'

# Page config
st.set_page_config(page_title="Electric Grid MST", layout="wide")
st.title("⚡ Electricity Grid Optimizer Using MST")

# Session state defaults
if 'locations' not in st.session_state:
    st.session_state['locations'] = []
if 'connection_type' not in st.session_state:
    st.session_state['connection_type'] = "direct"

# Setup geolocator
geolocator = Nominatim(user_agent="electricity-grid-app", timeout=10)

# Sidebar
with st.sidebar:
    st.header("📍 Add Location")
    place = st.text_input("Enter a place name (e.g., Mumbai)")
    if st.button("Add Location"):
        if place.strip():
            try:
                loc = geolocator.geocode(place)
                if loc:
                    st.session_state['locations'].append((place, loc.latitude, loc.longitude))
                    st.success(f"✅ Added: {place}")
                else:
                    st.error("❌ Location not found.")
            except (GeocoderUnavailable, GeocoderTimedOut) as e:
                st.error(f"🌐 Geocoding timed out/unavailable. Try again later.\nError: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")

    st.markdown("---")
    st.header("🔌 Connection Type")
    choice = st.radio("Choose connection type:", ["Direct (Line of Sight)", "Road-wise (Routing Distance)"])
    st.session_state['connection_type'] = "direct" if "Direct" in choice else "road"

    st.markdown("---")
    if st.button("🧹 Reset All"):
        st.session_state['locations'] = []

# Main Map
m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, control_scale=True)

# Add location markers
for name, lat, lon in st.session_state['locations']:
    folium.Marker([lat, lon], tooltip=name).add_to(m)

# Draw MST if enough locations
if len(st.session_state['locations']) >= 2:
    mst = compute_mst(st.session_state['locations'], st.session_state['connection_type'])
    if mst and mst.edges:
        total = 0
        for u, v, data in mst.edges(data=True):
            # Ensure coordinates are in (lat, lon) format for Folium
            path = [(lat, lon) for lon, lat in data['geometry']]
            folium.PolyLine(
                locations=path,
                color="blue",
                weight=3,
                tooltip=f"{u} ↔ {v}: {data['weight']:.2f} km"
            ).add_to(m)
            total += data['weight']

        st.markdown(f"### 🧮 Total Grid Cost ({choice}): **{total:.2f} km**")
    else:
        st.warning("⚠️ MST could not be computed. Please check your data or connection type.")

# Show the map
st_data = st_folium(m, height=600, width=1000)
