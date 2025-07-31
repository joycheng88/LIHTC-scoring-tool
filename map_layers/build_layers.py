import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium import CircleMarker, GeoJson, GeoJsonTooltip, FeatureGroup, LayerControl
from folium.plugins import MarkerCluster
import branca.colormap as cm
from branca.colormap import linear

#################################################################################################
# Build circle layer for lat/lon points - WITH max_points parameter for user control
def add_lat_lon_score_layer(gdf, layer_name, score_column="score", palette=None, radius=3, max_points=800):
    """
    Args:
        gdf (GeoDataFrame): Must contain geometry and a numeric score column.
        layer_name (str): Name for the layer.
        score_column (str): Name of the column containing numeric scores.
        palette (list): List of hex colours (e.g., YlGnBu_20).
        radius (int): Circle radius in pixels.
        max_points (int): Maximum points to render (user controllable).

    Returns:
        A tuple: (FeatureGroup layer, colourmap)
    """

    # Filter out rows with missing geometry or score
    valid_gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notnull()].copy()
    valid_gdf = valid_gdf[valid_gdf[score_column].notnull()]
    
    if valid_gdf.empty:
        return folium.FeatureGroup(name=layer_name), None

    # Sample data if too many points - stratified sampling to preserve distribution
    if len(valid_gdf) > max_points:
        valid_gdf = valid_gdf.sample(n=max_points, random_state=42)

    # Create colourmap using the score range and your custom palette
    colourmap = cm.LinearColormap(
        colors=palette,
        vmin=valid_gdf[score_column].min(),
        vmax=valid_gdf[score_column].max(),
        caption=layer_name
    )

    # Create a FeatureGroup to hold the markers
    layer = folium.FeatureGroup(name=layer_name)

    # Add each point as a circle marker 
    for _, row in valid_gdf.iterrows():
        lat = row.geometry.y
        lon = row.geometry.x
        score = row[score_column]
        colour = colourmap(score)

        CircleMarker(
            location=[lat, lon],
            radius=radius,
            color=colour,
            weight=0.1,
            fill=True,
            fill_color=colour,
            fill_opacity=0.4,
            popup=f"{score_column.title()}: {score:.2f}"
        ).add_to(layer)

    return layer, colourmap

##################################################################################################
# Build heat map layer for census tract level 
def add_tract_score_layer_stable(folium_map, gdf, score_column, layer_name, colour_scheme="YlGnBu_09", simplify_tolerance=0.005):
    """
    Adds a choropleth-style layer to a Folium map using polygon scores.
    Optimized for performance with geometry simplification.

    Args:
        folium_map: folium.Map object
        gdf: GeoDataFrame with polygon geometry and a score column
        score_column: name of the column to colour by
        layer_name: name of the layer shown in the layer control
        colour_scheme: colour palette name from branca.linear (default: YlGnBu_09)
        simplify_tolerance: tolerance for geometry simplification (default: 0.005)
    """

    # Ensure CRS is EPSG:4326 for folium compatibility
    gdf = gdf.to_crs("EPSG:4326")
    gdf[score_column] = pd.to_numeric(gdf[score_column], errors="coerce")
    print(gdf[score_column].head())
    
    # Get colour scale
    vals = gdf[score_column].dropna()
    if vals.empty:
        print(f"No valid numeric values for '{score_column}' — skipping layer: {layer_name}")
        return

    # Check if there are any valid numeric values
    if len(vals) == 0:
        print(f"No valid numeric values for '{score_column}' — skipping layer: {layer_name}")
        return
    print("Unique geometry types →", gdf.geom_type.unique())

    # Simplify geometries for better performance
    if simplify_tolerance > 0:
        gdf['geometry'] = gdf['geometry'].simplify(tolerance=simplify_tolerance, preserve_topology=False)
        # CRITICAL: Filter out invalid, null, AND empty geometries
        gdf = gdf[gdf.geometry.is_valid & gdf.geometry.notnull() & ~gdf.geometry.is_empty]
    
    # Check if we still have data after filtering
    if gdf.empty:
        print(f"No valid geometries after simplification for layer: {layer_name}")
        return

    cmap = getattr(linear, colour_scheme).scale(vals.min(), vals.max())
    cmap.caption = layer_name

    # Add GeoJSON layer
    folium.GeoJson(
        gdf,
        name=layer_name,
        style_function=lambda feature: {
            "fillColor": cmap(feature["properties"][score_column]) if feature["properties"][score_column] is not None else "#d3d3d3",
            "color": "gray",
            "weight": 1,
            "fillOpacity": 0.8
        },
        tooltip=folium.features.GeoJsonTooltip(
            fields=["GEOID", score_column],
            aliases=["Tract", layer_name],
            localize=True
        ),
        #options={"name": layer_name}
    ).add_to(folium_map)

    # Add legend
    cmap.add_to(folium_map)

#----------------------------------------------------------------------------#

##################################################################################################
# Add point layers (applicants)
def add_coloured_markers_to_map(
    folium_map,
    gdf,
    lat_col="lat",
    lon_col="lon",
    colour_by=None,
    popup_fields=None,
    layer_name="Markers",
    clustered=False, 
    categorical_colours=None,
):
    """
    Args:
        folium_map: folium.Map object
        gdf: GeoDataFrame or DataFrame
        lat_col: column for latitude
        lon_col: column for longitude
        colour_by: column with categorical values to colour by
        popup_fields: list of columns to include in popup
        layer_name: name of the feature group
        clustered: whether to use MarkerCluster 
        categorical_colours: dict mapping category to colour (optional)
    """

    feature_group = folium.FeatureGroup(name=layer_name)
    if clustered:
        marker_layer = MarkerCluster()
    else:
        marker_layer = folium.FeatureGroup(name=f"{layer_name} Markers")

    if colour_by and categorical_colours is None:
        unique_vals = gdf[colour_by].dropna().unique()
        colour_palette = ["green", "red", "blue", "orange", "purple", "gray"]
        categorical_colours = {
            val: colour_palette[i % len(colour_palette)]
            for i, val in enumerate(sorted(unique_vals))
        }

    for _, row in gdf.iterrows():
        lat = row[lat_col]
        lon = row[lon_col]

        if pd.isnull(lat) or pd.isnull(lon):
            continue  

        colour = "red"
        if colour_by:
            value = row.get(colour_by)
            colour = categorical_colours.get(value, "red")

        year = row.get("year", "")
        dev_name = row.get("development_name", "")
        owner_name = row.get("ownership_entity_name", "")
        status = row.get("status", "Unknown")
        dca_score = row.get("dca_score", "")

        tooltip_text = (
            f"<b>{dev_name}</b><br>"
            f"Owner: {owner_name}<br>"
            f"Year: {year}<br>"
            f"Status: {status}<br>"
            f"DCA Score: {dca_score}"
        )

        folium.CircleMarker(
            location=(lat, lon),
            radius=2,
            color='black',
            fill=True,
            fill_color=colour,
            fill_opacity=1,
            weight=0.8,
            tooltip=folium.Tooltip(tooltip_text, sticky=True)  
        ).add_to(marker_layer)

    marker_layer.add_to(feature_group)
    feature_group.add_to(folium_map)
