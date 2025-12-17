import math

import dash
import dash_leaflet as dl
import dash_mantine_components as dmc
import pandas as pd
from dash import Input, Output, callback, dcc, html
from flask import send_from_directory
from dotenv import load_dotenv
import os

load_dotenv()
app = dash.Dash(__name__)
server = app.server


@app.server.route("/business_photo/<path:filename>")
def serve_image(filename):
    return send_from_directory("business_photo", filename)


# Load businesses from CSV
df = pd.read_csv("mile_end_businesses.csv")


# https://tiles.stadiamaps.com/tiles/stamen_toner_blacklite/{z}/{x}/{y}{r}.png
stamen_url = (
    "https://tiles.stadiamaps.com/tiles/stamen_toner/"
    "{z}/{x}/{y}{r}.png?api_key=" + os.getenv("STADIA_API_KEY", "")
)

stamen_attrib = (
    '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, '
    '&copy; <a href="https://stamen.com/">Stamen Design</a>, '
    '&copy; <a href="https://openmaptiles.org/">OpenMapTiles</a>, '
    '&copy; <a href="https://www.openstreetmap.org/copyright">'
    "OpenStreetMap</a> contributors"
)

# Define color mapping for categories
category_colors = {
    "coffee": "#D4A574",  # Caramel/light brown
    "Restaurant": "#800020",  # Burgundy
    "Epicerie Fine": "#4CAF50",  # Green
    "Bar": "#2196F3",  # Blue
    "Brasserie": "#FF9800",  # Orange
    "Boulangerie": "#FFEB3B",  # Yellow
    "Cremerie": "#9C27B0",  # Violet
}


def create_business_popup(row, category_color):
    """Create an epic popup with image and detailed business information"""
    business_name = row["business_name"]
    category = row["category"]
    address = row["Addresse"] if pd.notna(row.get("Addresse")) else ""
    description = (
        row.get("description_fr", "") if pd.notna(row.get("description_fr")) else ""
    )
    instagram = row.get("instagram", "") if pd.notna(row.get("instagram")) else ""
    image = row.get("image_url", "") if pd.notna(row.get("image_url")) else ""

    # Use the custom route to serve images from business_photo folder
    img_url = f"/business_photo/{image}" if image else None
    image_orientation = (
        row.get("image_orientation", "")
        if pd.notna(row.get("image_orientation"))
        else "landscape"
    )

    # Image styling based on orientation
    img_class = (
        "popup-img-portrait"
        if image_orientation == "portrait"
        else "popup-img-landscape"
    )
    container_class = (
        "popup-container-portrait"
        if image_orientation == "portrait"
        else "popup-container-landscape"
    )

    # Image container
    img_container = html.Div(
        [
            (
                html.Img(
                    src=img_url,
                    className=img_class,
                    style={"backgroundColor": category_color},
                )
                if img_url
                else html.Div(
                    className=f"{img_class} popup-img-placeholder",
                    style={"backgroundColor": category_color},
                    children="📷",
                )
            ),
        ],
        className="popup-img-container",
        # style={"backgroundColor": category_color, "flexShrink": 0 if image_orientation == "portrait" else None},
    )

    # Metadata container with beautiful styling
    metadata_container = html.Div(
        [
            # Header row with title and Instagram button
            html.Div(
                [
                    html.H2(business_name, className="popup-business-name"),
                    (
                        html.A(
                            html.Img(
                                src="/assets/instagram_icon.png",
                                className="popup-instagram-icon",
                                alt="Instagram",
                            ),
                            href=(
                                f"https://www.instagram.com/{instagram}"
                                if instagram and isinstance(instagram, str)
                                else "#"
                            ),
                            target="_blank",
                            # className="popup-instagram-button",
                        )
                        if instagram
                        else None
                    ),
                ],
                className="popup-header-row",
            ),
            # Category badge
            html.Div(
                category,
                className="popup-category-badge",
                style={"backgroundColor": category_color},
            ),
            # Description
            html.P(
                (
                    description
                    if description
                    else "A wonderful local business in Montreal."
                ),
                className=f"popup-description {'popup-description-italic' if description else ''}",
            ),
            # Address section
            html.Div(
                [
                    html.Span("📍", className="popup-address-icon"),
                    html.Span(
                        address if address else "Address not available",
                        className="popup-address-text",
                    ),
                ],
                className="popup-address-container",
            ),
        ],
        className="popup-metadata",
    )

    return html.Div(
        [img_container, metadata_container],
        className=container_class,
    )


# Create markers from CSV data and store positions for click matching
markers = []
marker_positions = {}  # Store positions by index for click matching

for idx, row in df.iterrows():
    position = [row["lat"], row["lon"]]
    category = row["category"]
    color = category_colors.get(
        category, "#808080"
    )  # Default gray if category not found
    business_name = row["business_name"]
    website = row.get("instagram", "")
    address_tooltip = row.get("Addresse", "") if pd.notna(row.get("Addresse")) else ""
    image_orientation = (
        row.get("image_orientation", "")
        if pd.notna(row.get("image_orientation"))
        else "landscape"
    )
    max_width = "30vw" if image_orientation == "landscape" else "25vw"
    # max_height = "100%" if image_orientation == "landscape" else "20vh"

    # Store position for this marker
    marker_positions[idx] = {
        "position": position,
        "name": business_name,
        "category": category,
        "website": website,
    }

    markers.append(
        dl.CircleMarker(
            center=position,
            radius=9,
            children=[
                dl.Tooltip(
                    html.Div(
                        [
                            html.Strong(
                                business_name, className="tooltip-business-name"
                            ),
                            html.Span(
                                category,
                                className="tooltip-category",
                                style={"color": color},
                            ),
                            html.Br(),
                            html.Span(
                                (
                                    (
                                        (address_tooltip[:30] + "...")
                                        if len(address_tooltip) > 30
                                        else address_tooltip
                                    )
                                    if address_tooltip
                                    else "Address not available"
                                ),
                                className="tooltip-address",
                            ),
                        ],
                        className="tooltip-container",
                    ),
                    permanent=False,
                ),
                dl.Popup(create_business_popup(row, color), maxWidth=max_width),
            ],
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            weight=2,
        )
    )

# Create legend
legend_items = []
for category, color in category_colors.items():
    legend_items.append(
        html.Div(
            [
                html.Span(
                    className="legend-color-dot",
                    style={"backgroundColor": color},
                ),
                html.Span(category, className="legend-category-name"),
            ],
            className="legend-item",
        )
    )

legend = html.Div(
    [
        html.Div("Legend", className="legend-title"),
        *legend_items,
    ],
    className="legend-container",
)


# Floating welcome div
welcome_div = html.Div("Welcome to MTL.", className="welcome-div")

app.layout = dmc.MantineProvider(
    html.Div(
        [
            dl.Map(
                id="map",
                center=[45.5250, -73.5992],
                zoom=15.0,
                style={"width": "100%", "height": "100vh"},
                children=[
                    dl.TileLayer(url=stamen_url, attribution=stamen_attrib),
                    *markers,  # Add all business markers
                ],
            ),
            legend,
            welcome_div,
        ],
        className="app-layout",
    )
)


if __name__ == "__main__":
    app.run(debug=True, port=8051)
