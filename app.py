from distutils.cygwinccompiler import Mingw32CCompiler
from multiprocessing.dummy.connection import families
import streamlit as st

st.set_page_config(
    page_title="ridgemapp",
    page_icon="🗺️",
    initial_sidebar_state="expanded"
    )

from streamlit_folium import st_folium
from streamlit_image_select import image_select
import json
import matplotlib.pyplot as plt
from plotting import create_map
from folium_map_render import *

#load predefined styles stored in json file
with open('map_styles.json', 'r') as json_file:
    map_styles = json.load(json_file)

# Initialise states
if "initialise_map" not in st.session_state:
    st.session_state.initialise_map = True

if "area_drawn" not in st.session_state:
    st.session_state.area_drawn = False

if "disabled" not in st.session_state:
    st.session_state.disabled = False

if "map_data" not in st.session_state:
    st.session_state.map_data = None

# disable set area button after it is clicked
def disable():
    st.session_state.disabled = True

#=== Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("You like maps? You like visualisations? Then you'll love ridgemapp!")
    st.markdown("Create ridge plots of elevation data, customise and download. Print ready for postcards, posters or anything really - makes for some great gifts too.")
    st.subheader("Limitations")
    st.markdown("Data might not be available for some parts of the world. Please be mindful with the area you select, if too large the app might crash.")
    st.subheader("Credits")
    st.markdown("This app uses the awesome `ridge-map` library to create visually stunning elevation maps. Topographic data comes from NASA's Shuttle Radar Topography Mission ([SRTM](https://www.earthdata.nasa.gov/sensors/srtm)).")
    st.markdown("Check out ridge-map's [full documentation](https://pypi.org/project/ridge-map/) for more details. The original code is changed slightly to allow transparent backgrounds.")
    st.markdown("")
    st.subheader("Get in touch")
    st.markdown("I'm on [Github](https://github.com/Lisa-Ho), [Mastodon](https://fosstodon.org/@LisaHornung), [Linkedin](https://www.linkedin.com/in/lisa-maria-hornung/), [Twitter](https://twitter.com/LisaHornung_)")
    st.markdown("Made by Lisa Hornung")

#==== Main App
st.title('ridgemapp')
st.markdown("### Create stunning elevation maps")
st.markdown("")

# ========= Make selection
#interactive folium map and set all draw options to false except rectangle

# User instructions and buttons
st.markdown('Draw a ◼️ rectangle on the map. Click `Set area` to create ridge map or `reset` to draw again.')

col0a, col0b,col0 = st.columns([1,1,5], gap="small")
with col0b:
    button_reset = st.button('Reset')
if button_reset:
    st.session_state.initialise_map = True
    st.session_state.area_drawn = False
    st.session_state.disabled = False

with col0a:
    button_set_area = st.button('Set area', on_click=disable, disabled=st.session_state.disabled)

if button_set_area == True:
    st.session_state.initialise_map = False
    st.session_state.area_drawn = True

# create container to hold the interactive and static map
map_container = st.empty()

# if first time or reset, render interactive map
if st.session_state.initialise_map == True:
    with map_container.container():
        interactive_map = st_folium(render_interactive_map(), width=800, height=450, key="folium_map1")
        st.session_state.map_data = interactive_map

# if area set, replace with static map and disable set area button
if st.session_state.initialise_map == False:
    try:
        with map_container.container():
            static_map = st_folium(render_static_map_with_input(st.session_state.map_data), 
            width=800, height=450, key="folium_map2")
    except ValueError:
        with map_container.container():
            st.write("No area selected. Reset and draw rectangle, then try again")
            static_map = st_folium(render_static_map(), width=800, height=450, key="folium_map3")
            

#=========== Select style from image
#write user instructions
st.markdown('Change starter style')

#provide a caption for each style
captions=["Dark", "Transparent", "Comic", "Flat"]

#display images (images are saved in "examples" folder)
style_id = image_select(
    label="",
    images=["examples/dark.png",
        "examples/transparent.png",
        "examples/comic.png",
        "examples/flat.png"],
    captions=captions,
    index = 0,
    return_value ="index",
    key="style_selected"
)
#get values for selected style using the returned index
style_selected = map_styles[captions[style_id]]

# ========== Customise styles
style_updated = {}
font_styles = ['Calibri','Cambria','Candara', 'Courier New', 'DejaVu Sans','Ebrima', 'Gabriola','Impact',
             'Lucida Console','Segoe Print', 'Segoe UI', 'Tahoma','Times New Roman', 'Ubuntu', "Verdana"]
title_positions = ['top left', 'top right', 'bottom left', 'bottom right']
fig_shapes = ["square", "rectangle"]

with st.form(key="Create map"):
    style_custom = {}
    st.markdown("Customise style")
    col1a, col1b = st.columns([2,1], gap="medium")
    with col1a:
        style_custom["title"] = st.text_input("Title (optional)", style_selected["title"])
    with col1b:
        style_custom["fig_shape"] = st.selectbox('Shape',options=fig_shapes,index=fig_shapes.index(style_selected["fig_shape"]) )
    with st.expander("Change colours, lines and more"):
        st.markdown("**Background**")
        col2a, col2b, col2c = st.columns([1,1,2], gap="small")
        with col2a:
            style_custom["bg_transparent"] = st.checkbox('Transparent',value=False)
        with col2b:
            style_custom["bg_color"] = st.color_picker("Colour", style_selected["bg_color"], key=0)

        st.markdown("")
        st.markdown("**Title**")
        col3a,col3b,col3c,col3d = st.columns([1.2,1.7,1,1], gap="small")
        with col3a:
            style_custom["title_pos"] = st.selectbox('Position',options=title_positions,index=title_positions.index(style_selected["title_pos"]))
        with col3b:
            style_custom["title_font"] = st.selectbox('Font',options=font_styles, index= font_styles.index(style_selected["title_font"] ))
        with col3c:
            style_custom["title_fontsize"] = st.slider("Fontsize", min_value=10, max_value=60, value=style_selected["title_fontsize"])
        with col3d:
            style_custom["title_color"] = st.color_picker('Colour', style_selected["title_color"], key=1)
        
        col4a,col4b,col4c = st.columns([1,1.2,2], gap="small")
        with col4a:
            style_custom["title_bg_color"] = st.color_picker('Background colour', style_selected["title_bg_color"], key=2)
        with col4b:
            style_custom["title_bg_alpha"] = st.slider("Background opacity", min_value=0.0, max_value=1.0, value=style_selected["title_bg_alpha"],
            help="0=transparent, 1=solid")
        
        st.markdown("")
        st.markdown("**Ridge lines**")
        col5a,col5b,col5c = st.columns([1,1,2], gap="small")
        with col5a:
            style_custom["num_lines"] = st.slider("Number of lines", min_value=30, max_value=150, value=style_selected["num_lines"])
        with col5b:
            style_custom["linewidth"] = st.slider("Linewidth", min_value=1, max_value=10, value=style_selected["linewidth"])
        with col5c:
            style_custom["line_color"] = st.color_picker('Colour', style_selected["line_color"], key=3)
        col6a,col6b,col6c,col6d = st.columns([1,1,1,1], gap="small")
        with col6a:
            style_custom["elevation_pts"] = st.slider("Elevation points", min_value=10, max_value=200, value=style_selected["elevation_pts"], help="The more points, the smoother the ridge lines")
        with col6b:
            style_custom["vertical_ratio"] = st.slider("Vertical ratio", min_value=10, max_value=150, value=style_selected["vertical_ratio"], help="How steep or flat hills are displayed")
        with col6c:
            style_custom["water_ntile"] = st.slider("Water ntile", min_value=0, max_value=8, value=style_selected["water_ntile"], help="Set to 0 if you do not want any water marked")
        with col6d:
            style_custom["lake_flatness"] = st.slider("Lake flatness", min_value=0, max_value=8, value=style_selected["lake_flatness"], help="Set to 0 if you do not want any water marked")

    button_update_map = st.form_submit_button('Update')
st.markdown('Your ridgemap design! :point_down: :tada:')

# ========== Display map
if "update_map" not in st.session_state:
    st.session_state.update_map = False
if button_update_map:
    st.session_state.update_map = True

# Create map when area drawn and update with custom map styles
if (st.session_state.update_map == False) & (st.session_state.area_drawn == True) & (st.session_state.map_data["last_active_drawing"] != None):
    bl = st.session_state.map_data["last_active_drawing"]["geometry"]['coordinates'][0][0]
    tr = st.session_state.map_data["last_active_drawing"]["geometry"]['coordinates'][0][2]
    style = style_selected
    fig = create_map(style, bl, tr)
    st.pyplot(fig)
elif (st.session_state.update_map) & (st.session_state.area_drawn == True) & (st.session_state.map_data["last_active_drawing"] != None):
    bl = st.session_state.map_data["last_active_drawing"]["geometry"]['coordinates'][0][0]
    tr = st.session_state.map_data["last_active_drawing"]["geometry"]['coordinates'][0][2]
    style = style_custom
    fig = create_map(style, bl, tr)
    st.pyplot(fig)
elif (st.session_state.update_map) & (st.session_state.area_drawn == False):
    st.markdown('**Select area first**')
    fig = "None" 
else:
    fig = "None" 

# ========== Download
#export image
if fig != "None":
    plt.savefig("ridgemaps.png", bbox_inches="tight", dpi=300, pad_inches=0, transparent=style["bg_transparent"])
    with open("ridgemaps.png", "rb") as image:
        png = st.download_button(
            label="Download png",
            data=image,
            file_name="ridgemap.png",
            mime="image/png"
        )
    plt.savefig("ridgemaps.svg", bbox_inches="tight", pad_inches=0)
    with open("ridgemaps.svg", "rb") as svg:
        svg = st.download_button(
            label="Download svg",
            data=svg,
            file_name="ridgemaps.svg"
        )