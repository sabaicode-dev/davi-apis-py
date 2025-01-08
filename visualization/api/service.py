# visualization/api/service.py
import importlib
from venv import logger
from dotenv import load_dotenv
from django.conf import settings
import seaborn as sns
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import chardet
import matplotlib
import uuid
import re
import plotly.graph_objects as go
import plotly.express as px
import os
import uuid
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import matplotlib.colors as mcolors
matplotlib.use("Agg")

dotenv_path_dev = '.env'
load_dotenv(dotenv_path=dotenv_path_dev)
color_graph ="#0346A5"
file_server_path_file = os.getenv("FILE_SERVER_PATH_FILE")
file_server_path_image = os.getenv("FILE_SERVER_PATH_IMAGE")
file_base_url = os.getenv("BASE_URL_FILE")

ALLOWED_EXTENSIONS_FILE = ['.csv', '.json', '.txt', '.xlsx']

valid_chart_types = {
    'line_chart': (True, True),     # Requires both labels and numbers. 
    'histogram': (False, True),     # Requires only numbers.
    'bar_chart': (True, True),      # Requires both labels and numbers.
    'pie_chart': (False, True),     # Requires only numbers.
    'scatter_plot': (True, True),   # Requires both labels and numbers.
    'heatmap': (True, True),       # Requires both labels and numbers.
    'area_chart': (True, True),     # Requires both labels and numbers.
    'doughnut_chart': (False, True),# Requires only numbers.
    'bubble_chart': (True, True),   # Requires both labels and numbers.
    'radar_chart': (True, True),    # Requires both labels and numbers.
    'column_chart': (True, True),   # Requires both labels and numbers.
    'map_chart': (True, True) # Requires both labels and numbers.
}

def get_file_extension(filename):
    _, extension = os.path.splitext(filename)
    return extension


def detect_delimiter(file_path):

    with open(file_path, 'r') as file:
        sample = file.read(1024)  # Read a sample of the file
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter


def load_dataset(filename):

    file_path = file_server_path_file+filename
    type_file = get_file_extension(filename).replace('.', "").strip()
    data = None

    try:

        with open(file_path, 'rb') as raw_data:
            result = chardet.detect(raw_data.read(1000))
        encoding = result['encoding']

        if type_file == 'csv':
            try:
                data = pd.read_csv(file_path, encoding=encoding,
                                   on_bad_lines="skip")
            except UnicodeDecodeError:
                data = pd.read_csv(file_path, encoding="latin1",
                                   on_bad_lines="skip")

        elif type_file == 'json':

            try:
                data = pd.read_json(file_path, encoding=encoding)

            except Exception as e:

                print(e)
        elif type_file == 'txt':

            data = pd.read_csv(file_path, encoding=encoding,
                               delimiter=detect_delimiter(file_path))
        elif type_file == 'xlsx':

            data = pd.read_excel(file_path)

    except FileNotFoundError as e:

        print(e)

    if data is not None and not data.empty:

        data = data.where(pd.notnull(data), None)
        data = data.apply(lambda x: x.astype(str) if x.dtype == 'float' else x)
        for col in data.columns:
            data.rename(columns={col: str(col).strip()}, inplace=True)

        numeric_columns = view_type_load_dataset(data)["numeric_columns"]
        for col in numeric_columns:
            data[col]= pd.to_numeric(data[col].replace('[^0-9.]', '', regex=True), errors='coerce')
        return data

    return None

def view_type_load_dataset(data):

    if data is not None:
        numeric_columns = []
        object_columns = []

        for column in data.columns:
            original_type = str(data[column].dtype)

            if original_type == 'object':

                numeric_values = data[column].astype(str).str.extract(r'(\d+)', expand=False)
                if not numeric_values.dropna().empty:

                    if find_character(str(data[column].head(1).iloc[0])):
                        object_columns.append(column)
                    else:    
                        numeric_columns.append(column)
                else:
                    object_columns.append(column)
            else:
                numeric_columns.append(column)

        return {
            "count_header": len(data.columns),
            "count_records": len(data),
            "all_columns": data.columns.tolist(),
            "numeric_columns": numeric_columns,
            "object_columns": object_columns
        }
    
    return None


def is_number(data,column):
    # Check if a specific column is numeric
    if pd.api.types.is_numeric_dtype(data[str(column)]):
        return True
    else:
        return False


def generateBASEURL(str_url):
    return file_base_url+str_url+"/"
    

def perform_visualize(filename, chart_name="bar_chart", x_axis=[None], y_axis=None):
    # Ensure the filename is correct
    data = load_dataset(filename)

    # Log the incoming request data for debugging purposes
    logger.info(f"Received data: {data.head()}")

    # Based on the chart name, call the respective function
    if chart_name == "line_chart":
        return generate_line_chart(data, x_axis, y_axis)

    elif chart_name == "bar_chart":
        return generate_bar_chart(data, x_axis, y_axis)
    
    elif chart_name == "pie_chart":
        return generate_pie_chart(data, x_axis)
    
    elif chart_name == "scatter_plot":
        return generate_scatter_plot(data, x_axis, y_axis)
    
    elif chart_name == "histogram":
        return generate_histogram(data, x_axis, y_axis)

    elif chart_name == "area_chart":
        return generate_area_chart(data, x_axis, y_axis)
    
    elif chart_name == "bubble_chart":
        return generate_bubble_chart(data, x_axis, y_axis)

    elif chart_name == "column_chart":
        return generate_column_chart(data, x_axis, y_axis)
    
    elif chart_name == "map_chart":
        return generate_map_chart(data, x_axis, y_axis)
    
    elif chart_name == "donut_chart":
        return generate_donut_chart(data, x_axis)
    
    elif chart_name == "heatmap":
        return generate_heatmap_chart(data, x_axis, y_axis)
    
    elif chart_name == "waterfall":
        return generate_waterfall(data, x_axis, y_axis)

    return None


def generate_waterfall(data, x_axis, y_axis):
    if x_axis and y_axis:
        counts = find_sum(data, x_axis, y_axis).head(10)

        fig = go.Figure(go.Waterfall(
            name="20", orientation="v",
            measure=["relative"] * len(counts[x_axis]) + ["total"],
            x=counts[x_axis],
            textposition="outside",
            y=counts["sum"],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))

        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title=str(y_axis) + " and " + str(x_axis),
            showlegend=True
        )

        # Check if kaleido is installed
        if importlib.util.find_spec("kaleido") is None:
            raise ImportError("The 'kaleido' package is required for exporting images. Install it using 'pip install -U kaleido'.")

        filename_visualize = uuid.uuid4().hex + ".png"
        fig.write_image(file_server_path_image + filename_visualize)

        return {
            "_id": str(uuid.uuid4().hex),
            "img": generateBASEURL(filename_visualize)
        }

    return None
   
def generate_column_chart(data, x_axis, y_axis):
    
    if x_axis:

        plt.figure(figsize=(15, 8))  # Increased figure size
        # for x in x_axis:
        counts = find_sum(data, x_axis, y_axis).head(10)
        plt.bar(counts[str(x_axis)], counts["sum"], color=color_graph, label=x_axis)  
        plt.xlabel(str(x_axis))  # Set generic x-label
        plt.ylabel("sum of "+str(y_axis))
        plt.title(f"{x_axis} and {y_axis}")
        plt.legend()  # Add legend if multiple lines

        filename_visualize = uuid.uuid4().hex + ".png"
        plt.savefig(file_server_path_image + filename_visualize,transparent=True)

        return {
            "_id":str(uuid.uuid4().hex),
            "img": generateBASEURL(filename_visualize)
        }

    return None

def generate_bubble_chart(data,x_axis,y_axis):

    if x_axis:

        # Create a new figure
        # Create a new figure
        plt.figure(figsize=(15, 8)) 
        
        # Get the aggregated data
        
        # Get the aggregated data
        counts = find_sum(data, x_axis, y_axis)

        # Normalize bubble size and clip it to avoid extreme sizes
        bubble_size = counts["sum"] * 10  # Scale the bubble size (adjust multiplier as needed)
        bubble_size = np.clip(bubble_size, 50, 2000)  # Avoid very small or very large bubbles

        # Normalize for color scale based on 'sum'
        norm = plt.Normalize(min(counts["sum"]), max(counts["sum"]))  
        colors = plt.cm.viridis(norm(counts["sum"]))  # Using 'viridis' colormap

        # Create the scatter plot (Bubble chart)
        plt.scatter(
            counts[str(x_axis)], 
            counts["sum"],  
            s=bubble_size,  # Size of the bubble
            marker='o', 
            c=colors,  # Color based on 'sum'
            label=x_axis
        )

        # Add labels and title

        # Normalize bubble size and clip it to avoid extreme sizes
        bubble_size = counts["sum"] * 10  # Scale the bubble size (adjust multiplier as needed)
        bubble_size = np.clip(bubble_size, 50, 2000)  # Avoid very small or very large bubbles

        # Normalize for color scale based on 'sum'
        norm = plt.Normalize(min(counts["sum"]), max(counts["sum"]))  
        colors = plt.cm.viridis(norm(counts["sum"]))  # Using 'viridis' colormap

        # Create the scatter plot (Bubble chart)
        plt.scatter(
            counts[str(x_axis)], 
            counts["sum"],  
            s=bubble_size,  # Size of the bubble
            marker='o', 
            c=colors,  # Color based on 'sum'
            label=x_axis
        )

        # Add labels and title
        plt.xlabel(str(x_axis))   
        plt.ylabel("sum of " + str(y_axis))
        plt.ylabel("sum of " + str(y_axis))
        plt.title(f"{x_axis} and {y_axis}")
        
        # Adjust y-axis limits dynamically based on data
        plt.ylim([min(counts["sum"]) * 0.9, max(counts["sum"]) * 1.1])
        
        # Show legend
        plt.legend()

        # Save the plot to file
        
        # Adjust y-axis limits dynamically based on data
        plt.ylim([min(counts["sum"]) * 0.9, max(counts["sum"]) * 1.1])
        
        # Show legend
        plt.legend()

        # Save the plot to file
        filename_visualize = uuid.uuid4().hex + ".png"
        plt.savefig(file_server_path_image + filename_visualize, transparent=True)

        # Return the image URL
        plt.savefig(file_server_path_image + filename_visualize, transparent=True)

        # Return the image URL
        return {
            "_id": str(uuid.uuid4().hex),
            "_id": str(uuid.uuid4().hex),
            "img": generateBASEURL(filename_visualize)
        }

    return None

def generate_heatmap_chart(data, x_axis, y_axis):
    if x_axis and y_axis:

        # Filter out rows where either column contains non-numeric values
        data[x_axis] = pd.to_numeric(data[x_axis], errors='coerce')  # Coerce non-numeric to NaN
        data[y_axis] = pd.to_numeric(data[y_axis], errors='coerce')  # Coerce non-numeric to NaN

        # Drop rows with NaN values after coercion
        data_clean = data.dropna(subset=[x_axis, y_axis])

        # Create the heatmap
        plt.figure(figsize=(15, 15)) 
        counts = find_sum(data_clean, x_axis, y_axis)
        df = pd.concat([data_clean[x_axis].astype(float), data_clean[y_axis].astype(float)], axis=1)

        # Create heatmap
        plt.imshow(df, cmap='autumn', interpolation='nearest')
        plt.colorbar()

        plt.xlabel(str(x_axis))   
        plt.ylabel("sum of "+str(y_axis))
        plt.title(f"{x_axis} and {y_axis}")
        plt.ylim([0, 15])

        # Optionally, you can add a legend if you have multiple lines or categories
        plt.legend()  # This might be unnecessary for a heatmap, unless you're plotting multiple series

        # Save the image
        filename_visualize = uuid.uuid4().hex + ".png"
        plt.savefig(file_server_path_image + filename_visualize, transparent=True)

        return {
            "_id": str(uuid.uuid4().hex),
            "img": generateBASEURL(filename_visualize)
        }

    return None

def generate_area_chart(data , x_axis , y_axis):

    if x_axis:

        plt.figure(figsize=(15, 8)) 
        plt.fill_between(data[x_axis].head(10), data[y_axis].head(10), color=color_graph)
        plt.xlabel(str(x_axis)) 
        plt.ylabel("sum of "+str(y_axis))
        plt.title(f"{x_axis} and {y_axis}")

        filename_visualize = uuid.uuid4().hex + ".png"
        plt.savefig(file_server_path_image + filename_visualize,transparent=True)


        return {
            "_id":str(uuid.uuid4().hex),
            "img": generateBASEURL(filename_visualize)
        }

    return None

def generate_histogram(data, x_axis, y_axis=None):

    if x_axis:

        plt.figure(figsize=(15, 8))
        data_to_plot = data[x_axis]
        plt.hist(data_to_plot, bins=15, color=color_graph, rwidth=10)  # Set rwidth to 1.0

        plt.xlabel(x_axis)  # Set x-label
        plt.ylabel("Frequency")  # Y-label represents the frequency
        plt.title(f"Histogram of {x_axis}")

        filename_visualize = uuid.uuid4().hex + ".png"
        plt.savefig(file_server_path_image + filename_visualize,transparent=True)

        plt.close()  # Close the current figure to avoid displaying it immediately
    
        return {
            "_id": str(uuid.uuid4().hex),
            "img": generateBASEURL(filename_visualize)
        }
    
    return None
    
def generate_scatter_plot(data,x_axis,y_axis):
    
    if x_axis:

        plt.figure(figsize=(15, 8)) 
        counts = find_sum(data, x_axis, y_axis)
        plt.scatter(counts[str(x_axis)], counts["sum"], marker='o', label=x_axis,color=color_graph)  

        plt.xlabel(str(x_axis))  # Set generic x-label
        plt.ylabel("sum of "+str(y_axis))
        plt.title(f"{x_axis} and {y_axis}")
        plt.legend()  # Add legend if multiple lines

        filename_visualize = uuid.uuid4().hex + ".png"
        plt.savefig(file_server_path_image + filename_visualize,transparent=True)

    
        return {
            "_id":str(uuid.uuid4().hex),
            "img": generateBASEURL(filename_visualize)
        }

    return None

def generate_line_chart(data, x_axis, y_axis):
    
    if x_axis:

        plt.figure(figsize=(15, 8)) 
        counts = find_sum(data, x_axis, y_axis)
        plt.plot(counts[str(x_axis)], counts["sum"], marker='o', label=x_axis,color=color_graph)  
        plt.xlabel(str(x_axis))  
        plt.ylabel("sum of "+str(y_axis))
        plt.title(f"{x_axis} and {y_axis}")
        plt.legend()  
        filename_visualize = uuid.uuid4().hex + ".png"
        plt.savefig(file_server_path_image + filename_visualize,transparent=False)

        return {
            "_id":str(uuid.uuid4().hex),
            "img": generateBASEURL(filename_visualize)
        }

    return None
    
def generate_bar_chart(data, x_axis, y_axis):
    
    if x_axis:

        plt.figure(figsize=(15, 8)) 
        counts = find_sum(data, x_axis, y_axis).head(10)
        plt.barh(counts[str(x_axis)],counts["sum"],color=color_graph, label=x_axis)  
        plt.ylabel(str(x_axis)) 
        plt.xlabel("sum of "+str(y_axis))
        plt.title(f"{x_axis} and {y_axis}")
        plt.legend()  

        filename_visualize = uuid.uuid4().hex + ".png"
        plt.savefig(file_server_path_image + filename_visualize,transparent=True)


        return {
            "_id":str(uuid.uuid4().hex),
            "img": generateBASEURL(filename_visualize)
        }

    return None

def generate_card_KPI_NUMBER(data, aggregation, field):
    try:
        if field not in data.columns:
            raise ValueError(f"Field '{field}' not found in the dataset.")

        data[field] = pd.to_numeric(data[field], errors='coerce')
        data = data.dropna(subset=[field])  
        print(data[field])

        if aggregation == "sum":
            return data[field].sum()
        elif aggregation == "average":
            return data[field].mean()
        elif aggregation == "count":
            return len(data)
        elif aggregation == "minimum":
            return data[field].min()
        elif aggregation == "maximum":
            return data[field].max()
        elif aggregation == "std_deviation":
            return data[field].std()
        elif aggregation == "variance":
            return data[field].var()
        elif aggregation == "median":
            return data[field].median()
        elif aggregation == "count_distinct":
            return data[field].nunique()
        else:
            raise ValueError(f"Invalid aggregation method: {aggregation}")

    except Exception as e:
        # Handle the error (e.g., log it, print it, etc.)
        print(f"Error in generate_card_KPI_NUMBER: {e}")
        return None

def generate_pie_chart(data, x_axis):
    
    if x_axis:

        plt.figure(figsize=(8, 8)) 
        counts = find_sum_category(data, x_axis)
        plt.pie(counts["count"],labels=counts[str(x_axis)],autopct='%1.1f%%')  

        plt.xlabel(str(x_axis))  
        plt.title(f"{x_axis}")
        plt.legend()  

        filename_visualize = uuid.uuid4().hex + ".png"
        plt.savefig(file_server_path_image + filename_visualize,transparent=True)
        return {
            "_id":str(uuid.uuid4().hex),
            "img": generateBASEURL(filename_visualize)
        }

    return None

def generate_donut_chart(data, x_axis):
    
    if x_axis:

        plt.figure(figsize=(8, 8)) 
        counts = find_sum_category(data, x_axis)
        plt.pie(counts["count"],labels=counts[str(x_axis)],autopct='%1.1f%%',pctdistance=0.85,)  
        centre_circle = plt.Circle((0, 0), 0.50, fc='white')
        fig = plt.gcf()
        
        # Adding Circle in Pie chart
        fig.gca().add_artist(centre_circle)
        plt.xlabel(str(x_axis))  
        plt.title(f"{x_axis}")
        plt.legend()  

        filename_visualize = uuid.uuid4().hex + ".png"
        plt.savefig(file_server_path_image + filename_visualize,transparent=True)
        return {
            "_id":str(uuid.uuid4().hex),
            "img": generateBASEURL(filename_visualize)
        }

    return None


def generate_map_chart(data, x_axis, y_axis):
    if not x_axis or not y_axis:
        return {"error": "Both x_axis and y_axis must be provided."}

    shapefile_path = os.path.join(os.getcwd(), 'shapefiles', 'ne_110m_admin_0_countries.shp')
    if not os.path.exists(shapefile_path):
        return {"error": f"Shapefile not found at {shapefile_path}"}

    world = gpd.read_file(shapefile_path)
    country_col = find_location_column(world)
    if not country_col:
        return {"error": f"No valid country column found in the shapefile. Columns: {world.columns.tolist()}"}

    location_column = find_location_column(data, column_name=x_axis)
    if not location_column:
        return {"error": f"Location column '{x_axis}' not found in the data."}

    world = world.rename(columns={country_col: 'Country'})
    data = data.rename(columns={location_column: 'Country'})
    
    data['Country'] = data['Country'].str.lower().str.strip()
    world['Country'] = world['Country'].str.lower().str.strip()

    merged = world.merge(data, on='Country', how='left')

    if merged[y_axis].isnull().all():
        return {"error": "No matches found between dataset countries and the shapefile."}

    merged = merged.dropna(subset=[y_axis])
    merged = merged.sort_values(by=y_axis, ascending=False)

    fig, ax = plt.subplots(1, 1, figsize=(12, 6))
    norm = mcolors.Normalize(vmin=merged[y_axis].min(), vmax=merged[y_axis].max())
    sm = plt.cm.ScalarMappable(cmap='Blues', norm=norm)
    sm.set_array([])

    im = merged.plot(column=y_axis, ax=ax, legend=False, cmap='Blues')

    cbar = plt.colorbar(sm, ax=ax, orientation='vertical', shrink=0.6, aspect=25)
    cbar.set_label(y_axis, fontsize=12)
    cbar.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    cbar.ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
    cbar.set_ticks([merged[y_axis].min(), merged[y_axis].max()])
    cbar.set_ticklabels([f"{merged[y_axis].min():,.0f}", f"{merged[y_axis].max():,.0f}"])
    
    ax.set_title(f"{y_axis} Distribution by Country", fontsize=18, fontweight='bold', pad=20)
    ax.axis('off')

    filename_visualize = f"{uuid.uuid4().hex}.png"
    image_path = os.path.join(file_server_path_image, filename_visualize)
    os.makedirs(os.path.dirname(image_path), exist_ok=True)

    plt.savefig(image_path, transparent=True, dpi=300, bbox_inches='tight')
    plt.close()

    return {
        "_id": str(uuid.uuid4().hex),
        "img": generateBASEURL(filename_visualize),
        "metadata": {
            "x_axis": x_axis,
            "y_axis": y_axis,
            "description": f"This map highlights the distribution of {y_axis} across various {x_axis}.",
            "total_countries": len(merged)
        }
    }


def find_location_column(df, column_name="Country"):
    
    print(f"Columns in the DataFrame: {df.columns.tolist()}")  # Debugging: Print column names in the shapefile
    
    if column_name in df.columns:
        return column_name
    
    possible_columns = ['NAME', 'SOVEREIGNT', 'ADMIN', 'COUNTRY', 'REGION_UN']
    for col in possible_columns:
        if col in df.columns:
            return col
    
    return None

def generate_card_KPI_CATEGORY(data,aggregation,field):

    if aggregation == "first":
        return find_first_category(data,field)
    elif aggregation == "last":
        return find_last_category(data,field)
    elif aggregation == "count":
        return len(data)
    elif aggregation == "count_distinct":
        return find_count_disinct(data,field)

# TODO:
    
def find_sum_category(data,x_axis):
    
    value_counts=data[x_axis].value_counts().reset_index()
    return value_counts.head(10)

def find_first_category(data, fiels):

    try:
        return data[fiels].iloc[0]

    except Exception as e:
        print(e)
        return None

def find_last_category(data,fiels):

    try:
        return data[fiels].iloc[len(data)-1]

    except Exception as e:
        print(e)
        return None

def find_count_disinct(data,fiels):
    return data[str(fiels)].nunique()

def find_KPI_CATEGORY(filename, chart_name,aggregation,fields):

    data = load_dataset(filename)
    list_data = []

    for field in fields:
        if chart_name == "card":
            result= generate_card_KPI_CATEGORY(data,aggregation,field)
            response = {}
            response["value"] = result
            response["aggregation"]=aggregation 
            response["message"]=str(aggregation+" of "+field).capitalize()
            list_data.append(response)



    return list_data

def find_KPI_NUMBER (filename, chart_name,aggregation,fields):

    data = load_dataset(filename)
    list_data = []
    for field in fields:
        if chart_name == "card":
            result = generate_card_KPI_NUMBER(data, aggregation, field)
            response = {}
            response["value"] = "{:.2f}".format(result) 
            response["aggregation"]=aggregation
            response["message"]=str(aggregation+" of "+field).capitalize()
            list_data.append(response) 
    
    return list_data

def find_sum(data, category_column, value_column):

    data[value_column] = data[value_column].replace(r'[^\d.]+', '', regex=True)
    data[value_column] = pd.to_numeric(data[value_column], errors='coerce')
    
    grouped_data = data.groupby(category_column)[value_column].sum().reset_index(name="sum")
    return grouped_data.head(10)


def find_range_of_dataset(size):

    values_only = [size * (i / 100) for i in range(0, 101, 10)]  
    return values_only

def view_type_dataset(filename):

    data = load_dataset(filename)
    if data is not None:
        numeric_columns = []
        object_columns = []

        for column in data.columns:
            original_type = str(data[column].dtype)

            if original_type == 'object':

                numeric_values = data[column].astype(str).str.extract(r'(\d+)', expand=False)
                if not numeric_values.dropna().empty:

                    if find_character(str(data[column].head(1).iloc[0])):
                        object_columns.append(column)
                    else:    
                        numeric_columns.append(column)
                else:
                    object_columns.append(column)
            else:
                numeric_columns.append(column)

        return {
            "count_header": len(data.columns),
            "count_records": len(data),
            "all_columns": data.columns.tolist(),
            "numeric_columns": numeric_columns,
            "object_columns": object_columns
        }
    
    return None

def find_character(text):

    regex_pattern = r'[A-Za-z]'
    matches = re.findall(regex_pattern, text)

    if matches: 
        return True
    return False