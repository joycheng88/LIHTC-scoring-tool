#######################################################################################################################################
# Import necessary libraries and modules
#######################################################################################################################################

import streamlit as st
import pandas as pd
import geopandas as gpd
from streamlit_folium import st_folium
import folium
from pathlib import Path

from aggregate_scoring import (
    CommunityTransportationOptions,
    DesirableUndesirableActivities,
    QualityEducation,
    StableCommunities
)
from map_layers.build_layers import *
from map_layers.colours import YlGnBu_20, YlGnBu_5, status_colours

#######################################################################################################################################
# Cached data loading functions
#######################################################################################################################################

@st.cache_data(persist="disk")
def load_gdf(path):
    return gpd.read_file(path)

@st.cache_data(persist="disk")
def load_csv(path, **kwargs):
    return pd.read_csv(path, **kwargs)

@st.cache_data
def get_core_data():
    return {
        'df_transit': load_csv("data/community_transportation_options/georgia_transit_locations_with_hub.csv"),
        'rural_gdf': load_gdf("data/shapefiles/usda_rural_tracts.geojson").to_crs("EPSG:4326"),
        'csv_desirable': load_csv("data/desirable_undesirable_activities/desirable_activities_google_places_v3.csv"),
        'csv_usda': load_csv("data/desirable_undesirable_activities/food_access_research_atlas.csv", dtype={'CensusTract': str}),
        'tract_shape': load_gdf("data/shapefiles/tl_2024_13_tract/tl_2024_13_tract.shp"),
        'csv_undesirable': load_csv("data/desirable_undesirable_activities/undesirable_hsi_tri_cdr_rcra_frs_google_places.csv"),
        'df_school': load_csv("data/quality_education_areas/Option_C_Scores_Eligibility_with_BTO.csv"),
        'df_indicators': load_csv("data/stable_communities/stable_communities_2024_processed_v3.csv")
    }

@st.cache_data
def get_school_boundaries():
    return [
        load_gdf(f"data/quality_education_areas/{name}").to_crs("EPSG:4326")
        for name in ["Administrative.geojson", "APSBoundaries.json", "DKE.json", "DKM.json", "DKBHS.json"]
    ]

@st.cache_data
def get_map_layer_data(layer_name):
    layer_paths = {
        "Total Score": "data/maps/total_location_score/total_score_metro_atl.geojson",
        "Community Transportation Score": "data/maps/community_transportation_options/transportation_options_score_metro_atl.geojson",
        "Desirable/Undesirable Activities Score": "data/maps/desirable_undesirable_activities/desirable_undesirable_score_metro_atl.geojson",
        "Quality Education Score": "data/maps/quality_education_areas/education_score_metro_atl_point_with_scores.geojson",
        "Stable Communities Score": "data/maps/stable_communities/stable_communities_score_metro_atl.geojson",
        "Past Applicant Locations": "data/maps/application_list_2022_2023_2024_metro_atl.geojson",
        "Housing Needs": "data/maps/housing_need_characteristics/housing_need_indicators_metro_atl.geojson",
        "Environmental Health Index": "data/maps/stable_communities/environmental_health_index_metro_atl.geojson",
        "Jobs Proximity Index": "data/maps/stable_communities/jobs_proximity_index_metro_atl.geojson",
        "Median Income": "data/maps/stable_communities/median_income_metro_atl.geojson",
        "Percent Population Above Poverty Level": "data/maps/stable_communities/above_poverty_level_metro_atl.geojson",
        "Transit Access Index": "data/maps/stable_communities/transit_access_index_metro_atl.geojson",
    }
    
    if layer_name in layer_paths:
        gdf = load_gdf(layer_paths[layer_name])
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")
        return gdf
    return None

#######################################################################################################################################
# Score Calculation Function
#######################################################################################################################################

def calculate_scores_if_needed(latitude, longitude):
    """Calculate scores only when button is clicked"""
    core_data = get_core_data()
    school_boundaries = get_school_boundaries()
    
    kwargs = {
        # --- CommunityTransportationOptions ---
        "transit_df": core_data['df_transit'],

        # --- DesirableUndesirableActivities ---
        "rural_gdf_unary_union": core_data['rural_gdf'].geometry.union_all(),
        "desirable_csv": core_data['csv_desirable'], 
        "grocery_csv": core_data['csv_desirable'],
        "usda_csv": core_data['csv_usda'],
        "tract_shapefile": core_data['tract_shape'],
        "undesirable_csv": core_data['csv_undesirable'],

        # --- QualityEducation ---
        "school_df": core_data['df_school'],
        "school_boundary_gdfs": school_boundaries,       
        "state_avg_by_year": {
            "elementary": {2018: 77.8, 2019: 79.9},
            "middle": {2018: 76.2, 2019: 77},
            "high": {2018: 75.3, 2019: 78.8}
        },

        # --- StableCommunities ---
        "indicators_df": core_data['df_indicators'],
        "tracts_shp": core_data['tract_shape'],
    }

    # Calculate scores
    ct_score = CommunityTransportationOptions(latitude, longitude, **kwargs).calculate_score()
    du_score = DesirableUndesirableActivities(latitude, longitude, **kwargs).calculate_score()
    qe_score = QualityEducation(latitude, longitude, **kwargs).calculate_score()
    sc_score = StableCommunities(latitude, longitude, **kwargs).calculate_score()

    return ct_score, du_score, qe_score, sc_score

#######################################################################################################################################
# Main Page Configuration and Formatting
#######################################################################################################################################

st.set_page_config(layout="wide")

st.markdown("""
    <style>
        /* === Global Defaults === */
        * {
            border-radius: 4px !important;
        }

        /* === Input Styling === */
        .stButton > button,
        .stTextInput > div > div,
        .stSelectbox > div,
        .stSlider > div,
        .stCheckbox > div,
        .stRadio > div,
        .stForm,
        .stDataFrame,
        .stMetric {
            border-radius: 4px !important;
        }

        /* === Label Styling for All Common Form Inputs === */
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stCheckbox"] label,
        div[data-testid="stSlider"] label,
        div[data-testid="stRadio"] label {
            font-size: 16px !important;
            font-weight: 500 !important;
            color: #222 !important;
        }

        /* === Optional: Input text size for consistency === */
        input[type="text"] {
            font-size: 15px !important;
        }
    </style>
""", unsafe_allow_html=True)


#######################################################################################################################################
# Initialize session state variables
#######################################################################################################################################

# Initialize default session state values
if "map_form_submitted" not in st.session_state:
    st.session_state.map_form_submitted = True 
    st.session_state.last_layer_selection = ["Total Score", "Past Applicant Locations"]
    st.session_state.last_max_points = 6000
    st.session_state.show_user_point = False

if 'lat_main' not in st.session_state:
    st.session_state.lat_main = ""
if 'lon_main' not in st.session_state:
    st.session_state.lon_main = ""

if 'map_cache' not in st.session_state:
    st.session_state.map_cache = {}
if 'last_layer_selection' not in st.session_state:
    st.session_state.last_layer_selection = []

#######################################################################################################################################
# Sidebar - Theme Selection
#######################################################################################################################################

with st.sidebar:
    st.header("Settings")
    
    # Dark mode toggle
    dark_mode = st.toggle(
        "Dark Mode",
        value=st.session_state.get("dark_mode", False),
        key="dark_mode",
        help="Toggle between light and dark theme"
    )
    
    # Apply dark mode styling
    if dark_mode:
        st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        .stSidebar {
            background-color: #262730;
        }
        
        .stSelectbox > div > div {
            background-color: #262730;
            color: #fafafa;
        }
        
        .stTextInput > div > div > input {
            background-color: #262730;
            color: #fafafa;
            border: 1px solid #4a4a4a;
        }
        
        .stButton > button {
            background-color: #262730;
            color: #fafafa;
            border: 1px solid #4a4a4a;
        }
        
        .stButton > button:hover {
            background-color: #404040;
            border-color: #666;
        }
        
        .stForm {
            background-color: #1a1a1a;
            border: 1px solid #333;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background-color: #262730;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #262730;
            color: #fafafa;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #404040;
        }
        
        .stDataFrame {
            background-color: #262730;
        }
        
        .stMetric {
            background-color: #1a1a1a;
            border: 1px solid #333;
        }
        
        /* === Text Color Inversions === */
        /* Main text elements */
        p, span, div, label {
            color: #fafafa !important;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #fafafa !important;
        }
        
        /* Markdown content */
        .stMarkdown, .stMarkdown * {
            color: #fafafa !important;
        }
        
        /* Form labels specifically */
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label,
        div[data-testid="stCheckbox"] label,
        div[data-testid="stSlider"] label,
        div[data-testid="stRadio"] label {
            color: #fafafa !important;
        }
        
        /* Captions and smaller text */
        .stCaption {
            color: #cccccc !important;
        }
        
        /* Info/warning/error boxes */
        .stAlert > div {
            background-color: #1a1a1a !important;
            color: #fafafa !important;
            border: 1px solid #404040 !important;
        }
        
        /* Expander content */
        .streamlit-expanderContent {
            background-color: #1a1a1a !important;
            color: #fafafa !important;
        }
        
        /* Custom score display dark mode */
        div[style*="background-color: #2B2D42"] {
            background-color: #404040 !important;
            color: #fafafa !important;
        }
        
        /* Score breakdown text */
        div[style*="font-size: 16px"] {
            color: #fafafa !important;
        }
        
        /* Custom HTML content */
        div[style*="margin-bottom"] {
            color: #fafafa !important;
        }
        
        /* Map container dark mode */
        .folium-map {
            filter: invert(0.9) hue-rotate(180deg);
        }
        
        /* Preserve map readability */
        .leaflet-container {
            filter: invert(0.9) hue-rotate(180deg);
        }
        
        /* Fix any remaining dark text on dark background */
        .stApp * {
            color: #fafafa;
        }
        
        /* Exception for specific elements that should remain their original colors */
        .stProgress > div {
            color: inherit !important;
        }
        
        /* Sidebar text */
        .stSidebar * {
            color: #fafafa !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Navigation Section
    # st.markdown("---")
    # st.header("Pages")
    
    # col1, col2 = st.columns(2)
    # with col1:
    #     if st.button("About LIHTC", use_container_width=True):
    #         st.switch_page("pages/About.py")
        
    #     if st.button("Prediction Model", use_container_width=True):
    #         st.switch_page("pages/prediction_model.py")
        
    #     if st.button("QAP Criteria", use_container_width=True):
    #         st.switch_page("pages/QAP_Criteria.py")
    
    # with col2:
    #     if st.button("Documentation", use_container_width=True):
    #         st.switch_page("pages/QAP_Documentation.py")

#######################################################################################################################################
# Main UI Layout
#######################################################################################################################################

st.title("LIHTC Location Scoring Tool")
st.markdown("*Created by Emory's Center for AI*")
main_col1, space_column, main_col2 = st.columns([4, 1, 7])

#######################################################################################################################################
# Main Column 1: Input Form for Coordinates and Display Scores
#########################################################################################################################################

with main_col1:
    st.subheader("Enter Site Coordinates")

    # Form for latitude and longitude input
    with st.form(key="latlon_form"):
        lat_input = st.text_input(
            "Latitude", 
            placeholder="e.g. 33.856192",
            key="lat_main"
        )

        lon_input = st.text_input(
            "Longitude", 
            placeholder="e.g. -84.347348", 
            key="lon_main"
        )

        submit_button = st.form_submit_button(
            label="Calculate Scores"
        )

    # Score calculation
    if submit_button:
        if not lat_input.strip() or not lon_input.strip():
            st.warning("Enter both latitude and longitude, then click Calculate Scores")
        else:
            try:
                latitude = float(lat_input)
                longitude = float(lon_input)
                valid_coords = True
            except ValueError:
                valid_coords = False

            if not valid_coords:
                st.warning("Please enter valid numeric coordinates.")
            else:
                with st.spinner("Calculating scores..."):
                    ct_score, du_score, qe_score, sc_score = calculate_scores_if_needed(latitude, longitude)
                    total_score = ct_score + du_score + qe_score + sc_score

                st.session_state.scores_calculated = True
                st.session_state.latitude = latitude
                st.session_state.longitude = longitude
                st.session_state.ct_score = ct_score
                st.session_state.du_score = du_score
                st.session_state.qe_score = qe_score
                st.session_state.sc_score = sc_score
                st.session_state.total_score = total_score

    # Score display
    if hasattr(st.session_state, 'scores_calculated') and st.session_state.scores_calculated:
        st.markdown("---")
        st.markdown(
            f"""
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;'>
                <h4 style='margin: 0;'>Total Location Score:</h4>
                <div style='background-color: #2B2D42; color: white; padding: 8px 16px; border-radius: 4px; font-size: 24px; font-weight: bold;'>
                    {st.session_state.total_score:.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            "<h4 style='margin-bottom: 14px; font-size: 20px; '>Breakdown by Category</h4>",
            unsafe_allow_html=True
        )

        score_data = [
            ("Community Transport Options Score:", st.session_state.ct_score),
            ("Desirable/Undesirable Activities Score:", st.session_state.du_score),
            ("Quality Education Areas Score:", st.session_state.qe_score),
            ("Stable Communities Score:", st.session_state.sc_score)
        ]
        
        for label, score in score_data:
            col1, col2 = st.columns([5, 3])
            with col1:
                st.markdown(
                    f"""
                    <div style='margin-bottom: 28px; font-size: 16px;'>
                        {label}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col2:
                st.markdown(
                    f"""
                    <div style='text-align: right; font-weight: bold; font-size: 16px;'>
                        {score:.2f}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


#######################################################################################################################################
# Right Column: Interactive Map Display
########################################################################################################################################

with main_col2:

    tab1, tab2, tab3 = st.tabs([
        "Location Criteria Score Map",
        "Stable Communities Indicator Map",
        "Housing Needs Indicator Map"
    ])

    # Tab 1 - Location Criteria Score Map
    with tab1:
        # Map layer selection form
        with st.form(key="map_layer_form"):
            selected_score_layer = st.selectbox(
                "Choose one score layer to display:",
                options=[
                    "Total Score", 
                    "Desirable/Undesirable Activities Score", 
                    "Community Transportation Score",
                    "Stable Communities Score",
                    "Quality Education Score"
                ],
                index=0,
                key="score_layer_selection"
            )

            # Checkbox for showing past applicant locations
            show_applicants = st.checkbox(
                "Overlay Past Applicant Locations",
                value=st.session_state.get("show_applicant_locations", True),
                key="show_applicant_locations"
            )

            # Slider for max points in score layers
            max_points = st.slider(
                "Number of Points to Display (Map Performance Tuning for Lat/Lon-Based Scores)",
                min_value=6000,
                max_value=13000,
                value=st.session_state.get("last_max_points", 6000),
                step=500,
                help = "Controls how many points are shown for layers whose scores are based on latitude and longitude (Total Score, Desirable/Undesirable Activities Score, and Community Transportation Score). A smaller number loads faster, but provides less visual detail. Showing the maximum number of points (~13,000) may slow map performance, but gives the most comprehensive view. The sample is stratified to preserve the overall score distribution. Adjust this slider to balance map detail with performance based on your needs.",
                key="max_points_slider"
            )

            # Checkbox for showing user point on map
            show_user_point = st.checkbox(
                "Show Site on Map",
                value=st.session_state.get("show_user_point", False),
                disabled=not st.session_state.get("scores_calculated", False),
                help="Enter latitude and longitude in the form on the left to enable this option.",
                key="show_user_point_checkbox"
            )

            update_map_button = st.form_submit_button("Update Map")

        # Handle form submission
        if update_map_button:
            selected_layers = [selected_score_layer]
            if show_applicants:
                selected_layers.append("Past Applicant Locations")

            st.session_state.last_layer_selection = selected_layers
            st.session_state.last_max_points = max_points
            st.session_state.show_user_point = show_user_point
            st.session_state.map_form_submitted = True

        selected_score_layer = st.session_state.get("score_layer_selection", "Total Score")
        show_applicants = st.session_state.get("show_applicant_locations", True)

        # Dynamic title for the map
        selected_layers = [selected_score_layer]
        if show_applicants:
            selected_layers.append("Past Applicant Locations")

        if len(selected_layers) == 1:
            map_title = f"#### Map of {selected_layers[0]}"
        else:
            map_title = f"#### Map of {', '.join(selected_layers[:-1])} and {selected_layers[-1]}"
        st.markdown(map_title)
    
        # Legend for applicant locations
        if show_applicants:
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 16px; height: 16px; background-color: red; border: 1px solid black; margin-right: 5px;"></div>
                        <span>Non-Selected Applicants</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 16px; height: 16px; background-color: #7CFC00; border: 1px solid black; margin-right: 5px;"></div>
                        <span>Selected Applicants</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Map rendering logic
        # Create a cache key based on selected layers and max points
        cache_key = f"{'-'.join(sorted(selected_layers))}_{max_points}"
        def all_layers_present(cached_map, selected_layers):
            return all(any(layer_name in str(child) for child in cached_map._children.values()) for layer_name in selected_layers)

        # Check if the map already exists in the cache
        map_exists = cache_key in st.session_state.map_cache
        cached_map = st.session_state.map_cache.get(cache_key) if map_exists else None

        # Determine if need to rebuild the map
        should_rebuild = (
            not map_exists
            or selected_layers != st.session_state.get("last_layer_selection", [])
            or not all_layers_present(cached_map, selected_layers)
        )

        # If selected layers are provided, build or update the map
        if selected_layers:
            if should_rebuild:
                with st.spinner("Loading map layers..."):
                    try:
                        m = folium.Map(
                            location=[33.886297, -84.362697],
                            zoom_start=9,
                            tiles="cartodbpositron",
                            prefer_canvas=True
                        )
                        for layer_name in selected_layers:
                            gdf = get_map_layer_data(layer_name)
                            if gdf is None or gdf.empty:
                                continue
                            if layer_name == "Past Applicant Locations":
                                add_coloured_markers_to_map(
                                    folium_map=m,
                                    gdf=gdf,
                                    lat_col="lat",
                                    lon_col="lon",
                                    colour_by="status",
                                    layer_name="Past Applicant Locations",
                                    clustered=False,
                                    categorical_colours=status_colours
                                )
                            elif layer_name == "Total Score":
                                layer, legend = add_lat_lon_score_layer(
                                    gdf, "Total Score", "score", YlGnBu_20, 4, max_points
                                )
                                layer.add_to(m)
                                if legend:
                                    legend.add_to(m)
                            elif layer_name == "Desirable/Undesirable Activities Score":
                                layer, legend = add_lat_lon_score_layer(
                                    gdf, layer_name, "score", YlGnBu_20, 4, max_points
                                )
                                layer.add_to(m)
                                if legend:
                                    legend.add_to(m)
                            elif layer_name == "Community Transportation Score":
                                layer, legend = add_lat_lon_score_layer(
                                    gdf, layer_name, "score", YlGnBu_5, 4, max_points
                                )
                                layer.add_to(m)
                                if legend:
                                    legend.add_to(m)
                            elif layer_name == "Stable Communities Score":
                                add_tract_score_layer_stable(
                                    m, gdf, "score", layer_name, simplify_tolerance=0.005
                                )
                            elif layer_name == "Quality Education Score":
                                layer, legend = add_lat_lon_score_layer(
                                    gdf, layer_name, "score", YlGnBu_5, 4, max_points
                                )
                                layer.add_to(m)
                                if legend:
                                    legend.add_to(m)

                        st.session_state.map_cache[cache_key] = m

                    except Exception as e:
                        st.error(f"Error creating map: {str(e)}")
                        st.stop()

            st.session_state.last_layer_selection = selected_layers.copy()

            cached_map = st.session_state.map_cache[cache_key]

            # If user point should be shown, add it to the map
            if show_user_point and st.session_state.get("scores_calculated", False):
                #import copy
                #display_map = copy.deepcopy(cached_map)
                display_map = cached_map
                folium.Marker(
                    [st.session_state.latitude, st.session_state.longitude],
                    tooltip="Your Site",
                    popup=f"Total Score: {st.session_state.total_score:.2f}",
                    icon=folium.Icon(
                    color="white",         
                    icon_color="#B8860B",  
                    icon="star"
                    )   
                ).add_to(display_map)
            else:
                display_map = cached_map

            # Render the map using st_folium
            st_folium(
                display_map,
                width=700,
                height=600,
                returned_objects=[],
                key=f"main_map_{hash(tuple(sorted(selected_layers)))}"
            )

        else:
            st.info("Select a layer to display the map.")

    with tab2:
        # Map layer selection form for Stable Communities
        with st.form(key="stable_map_layer_form"):
            stable_score_layer = st.selectbox(
                "Choose one Stable Communities layer to display:",
                options=[
                    "Stable Communities Score",
                    "Environmental Health Index",
                    "Jobs Proximity Index",
                    "Median Income",
                    "Percent Population Above Poverty Level",
                    "Transit Access Index"
                ],
                index=0,
                key="stable_score_layer_selection"
            )

            # Checkbox for showing past applicant locations
            stable_show_applicants = st.checkbox(
                "Overlay Past Applicant Locations",
                value=st.session_state.get("stable_show_applicants", True),
                key="stable_show_applicants"
            )

            # Checkbox for showing user point on map
            stable_show_user_point = st.checkbox(
                "Show Site on Map",
                value=st.session_state.get("stable_show_user_point", False),
                disabled=not st.session_state.get("scores_calculated", False),
                help="Enter latitude and longitude in the form on the left to enable this option.",
                key="stable_show_user_point_checkbox"
            )

            # Submit button to update the map
            stable_update_button = st.form_submit_button("Update Map")

        # Handle form submission
        stable_score_layer = st.session_state.get("stable_score_layer_selection", "Stable Communities Score")
        stable_show_applicants = st.session_state.get("stable_show_applicants", True)

        stable_selected_layers = [stable_score_layer]
        if stable_show_applicants:
            stable_selected_layers.append("Past Applicant Locations")

        # Dynamic title for the map
        if len(stable_selected_layers) == 1:
            map_title = f"#### Map of {stable_selected_layers[0]}"
        else:
            map_title = f"#### Map of {', '.join(stable_selected_layers[:-1])} and {stable_selected_layers[-1]}"
        st.markdown(map_title)

        # Legend for applicant locations
        if "Past Applicant Locations" in stable_selected_layers:
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 16px; height: 16px; background-color: red; border: 1px solid black; margin-right: 5px;"></div>
                        <span>Non-Selected</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 16px; height: 16px; background-color: #7CFC00; border: 1px solid black; margin-right: 5px;"></div>
                        <span>Selected</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Map rendering logic
        stable_cache_key = f"stable-{'-'.join(sorted(stable_selected_layers))}"

        def stable_layers_present(cached_map, selected_layers):
            return all(any(layer_name in str(child) for child in cached_map._children.values()) for layer_name in selected_layers)

        # Check if the map already exists in the cache
        map_exists = stable_cache_key in st.session_state.map_cache
        cached_map = st.session_state.map_cache.get(stable_cache_key) if map_exists else None

        # Determine if need to rebuild the map
        should_rebuild = (
            not map_exists
            or stable_selected_layers != st.session_state.get("stable_layer_selection", [])
            or not stable_layers_present(cached_map, stable_selected_layers)
        )

        # If selected layers are provided, build or update the map
        if stable_selected_layers:
            if should_rebuild:
                with st.spinner("Loading stable community layers..."):
                    try:
                        m = folium.Map(
                            location=[33.886297, -84.362697],
                            zoom_start=9,
                            tiles="cartodbpositron",
                            prefer_canvas=True
                        )
                        for layer_name in stable_selected_layers:
                            gdf = get_map_layer_data(layer_name)

                            if gdf is None or gdf.empty:
                                continue
                            if layer_name == "Past Applicant Locations":
                                add_coloured_markers_to_map(
                                    folium_map=m,
                                    gdf=gdf,
                                    lat_col="lat",
                                    lon_col="lon",
                                    colour_by="status",
                                    layer_name="Past Applicant Locations",
                                    clustered=False,
                                    categorical_colours=status_colours
                                )
                            elif layer_name == "Stable Communities Score":
                                add_tract_score_layer_stable(
                                    m, gdf, "score", "Stable Communities Score", simplify_tolerance=0.005
                                )
                            elif layer_name == "Environmental Health Index":
                                add_tract_score_layer_stable(
                                    m, gdf, "Environmental Health Index", layer_name, simplify_tolerance=0.005
                                )
                            elif layer_name == "Jobs Proximity Index":
                                add_tract_score_layer(
                                    m, gdf, "Jobs Proximity Index", layer_name, simplify_tolerance=0.005
                                )
                            elif layer_name == "Median Income":
                                add_tract_score_layer_stable(
                                    m, gdf, "Median Income", layer_name, simplify_tolerance=0.005
                                )
                            elif layer_name == "Percent Population Above Poverty Level":
                                add_tract_score_layer_stable(
                                    m, gdf, "Percent of Population Above the Poverty Level", layer_name, simplify_tolerance=0.005
                                )
                            elif layer_name == "Transit Access Index":
                                add_tract_score_layer_stable(
                                    m, gdf, "Transit Access Index", layer_name, simplify_tolerance=0.005
                                )

                        st.session_state.map_cache[stable_cache_key] = m

                    except Exception as e:
                        st.error(f"Error creating map: {str(e)}")
                        st.stop()

            cached_map = st.session_state.map_cache[stable_cache_key]

            # If user point should be shown, add it to the map
            if stable_show_user_point and st.session_state.get("scores_calculated", False):
                #import copy
                #display_map = copy.deepcopy(cached_map)
                display_map = cached_map
                folium.Marker(
                    [st.session_state.latitude, st.session_state.longitude],
                    tooltip="Your Site",
                    popup=f"Total Score: {st.session_state.total_score:.2f}",
                    icon=folium.Icon(
                        color="white",
                        icon_color="#B8860B",
                        icon="fa-star",
                        prefix="fa"
                    )
                ).add_to(display_map)
            else:
                display_map = cached_map

            # Render the map using st_folium
            st_folium(
                display_map,
                width=700,
                height=600,
                returned_objects=[],
                key=f"stable_map_{hash(tuple(sorted(stable_selected_layers)))}"
            )
        else:
            st.info("Select a layer to display the map.")

    with tab3:
        # Map layer selection form for Housing Needs indicators
        with st.form(key="housing_needs_map_layer_form"):
            housing_needs_layer = st.selectbox(
                "Choose one Housing Needs indicator layer to display:",
                options=[
                    "Severe Housing Problems (% of Renters ≤80% AMI)",
                    "YoY Population Growth (2018-2022)",
                    "Employment Growth Rate (2020-2022)",
                ],
                index=0,
                key="housing_needs_layer_selection"
            )

            # Checkbox for showing past applicant locations
            housing_needs_show_applicants = st.checkbox(
                "Overlay Past Applicant Locations",
                value=st.session_state.get("housing_needs_show_applicants", True),
                key="housing_needs_show_applicants"
            )

            # Checkbox for showing user point on map
            housing_needs_show_user_point = st.checkbox(
                "Show Site on Map",
                value=st.session_state.get("housing_needs_show_user_point", False),
                disabled=not st.session_state.get("scores_calculated", False),
                help="Enter latitude and longitude in the form on the left to enable this option.",
                key="housing_needs_show_user_point_checkbox"
            )

            housing_needs_update_button = st.form_submit_button("Update Map")

        #  Handle form submission
        housing_needs_layer = st.session_state.get("housing_needs_layer_selection", "Percent of Population with Severe Housing Needs")
        housing_needs_show_applicants = st.session_state.get("housing_needs_show_applicants", True)

        housing_needs_selected_layers = [housing_needs_layer]
        if housing_needs_show_applicants:
            housing_needs_selected_layers.append("Past Applicant Locations")

        # Dynamic title
        if len(housing_needs_selected_layers) == 1:
            map_title = f"#### Map of {housing_needs_selected_layers[0]}"
        else:
            map_title = f"#### Map of {', '.join(housing_needs_selected_layers[:-1])} and {housing_needs_selected_layers[-1]}"
        st.markdown(map_title)

        # Legend for applicant locations
        if "Past Applicant Locations" in housing_needs_selected_layers:
            st.markdown(
                """
                <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 16px; height: 16px; background-color: red; border: 1px solid black; margin-right: 5px;"></div>
                        <span>Non-Selected</span>
                    </div>
                    <div style="display: flex; align-items: center;">
                        <div style="width: 16px; height: 16px; background-color: #7CFC00; border: 1px solid black; margin-right: 5px;"></div>
                        <span>Selected</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # Map rendering logic
        housing_needs_cache_key = f"housing-needs-{'-'.join(sorted(housing_needs_selected_layers))}"
        def housing_needs_layers_present(cached_map, selected_layers):
            return all(any(layer_name in str(child) for child in cached_map._children.values()) for layer_name in selected_layers)

        # Check if the map already exists in the cache
        map_exists = housing_needs_cache_key in st.session_state.map_cache
        cached_map = st.session_state.map_cache.get(housing_needs_cache_key) if map_exists else None

        # Determine if need to rebuild the map
        should_rebuild = (
            not map_exists
            or housing_needs_selected_layers != st.session_state.get("housing_needs_layer_selection", [])
            or not housing_needs_layers_present(cached_map, housing_needs_selected_layers)
        )

        # If selected layers are provided, build or update the map
        if housing_needs_selected_layers:
            if should_rebuild:
                with st.spinner("Loading housing needs layers..."):
                    try:
                        m = folium.Map(
                            location=[33.886297, -84.362697],
                            zoom_start=9,
                            tiles="cartodbpositron",
                            prefer_canvas=True
                        )

                        housing_needs_gdf = get_map_layer_data("Housing Needs")
                        applicants_gdf = get_map_layer_data("Past Applicant Locations")

                        housing_needs_field_map = {
                            "Severe Housing Problems (% of Renters ≤80% AMI)": "% of rental units occupied by 80% AMI and below with Severe Housing Problems",
                            "YoY Population Growth (2018-2022)": "avg_pop_yoy_growth_2018_2021",
                            "Employment Growth Rate (2020-2022)": "avg_emp_growth_2020_2022"
                        }

                        for layer_name in housing_needs_selected_layers:
                            if layer_name == "Past Applicant Locations":
                                gdf = applicants_gdf
                            else:
                                gdf = housing_needs_gdf
                            if gdf is None or gdf.empty:
                                continue

                            if layer_name == "Past Applicant Locations":
                                add_coloured_markers_to_map(
                                    folium_map=m,
                                    gdf=gdf,
                                    lat_col="lat",
                                    lon_col="lon",
                                    colour_by="status",
                                    layer_name="Past Applicant Locations",
                                    clustered=False,
                                    categorical_colours=status_colours
                                )
                            else:
                                gdf.columns = gdf.columns.str.strip()
                                data_field = housing_needs_field_map.get(layer_name)
                                if data_field and data_field in gdf.columns:
                                    gdf[data_field] = pd.to_numeric(gdf[data_field], errors="coerce") * 100
                                    gdf[data_field] = gdf[data_field].round(1)
                                    add_tract_score_layer_stable(
                                        m, gdf, data_field, layer_name, simplify_tolerance=0.005
                                    )
                                    print(gdf[data_field].max(), gdf[data_field].min())
                                else:
                                    st.warning(f"Field '{data_field}' not found in dataset.")

                        st.session_state.map_cache[housing_needs_cache_key] = m

                    except Exception as e:
                        st.error(f"Error creating map: {str(e)}")
                        st.stop()

            cached_map = st.session_state.map_cache[housing_needs_cache_key]

            # If user point should be shown, add it to the map
            if housing_needs_show_user_point and st.session_state.get("scores_calculated", False):
                #import copy
                #display_map = copy.deepcopy(cached_map)
                display_map = cached_map
                folium.Marker(
                    [st.session_state.latitude, st.session_state.longitude],
                    tooltip="Your Site",
                    popup=f"Total Score: {st.session_state.total_score:.2f}",
                    icon=folium.Icon(
                        color="white",
                        icon_color="#B8860B",
                        icon="fa-star",
                        prefix="fa"
                    )
                ).add_to(display_map)
            else:
                display_map = cached_map

            # Render the map using st_folium
            st_folium(
                display_map,
                width=700,
                height=600,
                returned_objects=[],
                key=f"housing_needs_map_{hash(tuple(sorted(housing_needs_selected_layers)))}"
            )

        else:
            st.info("Select a layer to display the map.")



