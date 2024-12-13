import pandas as pd
import numpy as np
import uuid
from metafile.models import Metadata
from collections import Counter

from metafile.api.services import data_cleaning


class MetadataExtractor:

  def __init__(self, df_iterator):
    self.df_iterator = df_iterator
    self.columns = None
    self.data_types = {}
    self.column_order = {}
    self.total_counts = {}
    self.non_null_counts = {}
    self.valid_counts = {}
    self.unique_values = {}
    self.numeric_stats = {}
    self.string_stats = {}
    self.datetime_stats = {}
    self.histograms = {}
    self.metadata = []

  # New code
  def extract_and_store(self):
      """
      Extract metadata and store it in the Metadata model
      """
      # Extract metadata
      metadata_list = self.extract()
      # Create Metadata instance
      metadata_instance = Metadata.objects.create(
          file=self.file_obj,
          columns=metadata_list,
          total_rows=self.total_counts[self.columns[0]] if self.columns else 0,
          total_columns=len(self.columns) if self.columns else 0
      )
      return metadata_instance

  def extract(self):
    for df in self.df_iterator:
      if self.columns is None:
        # Initialize structures based on the first chunk
        self.initialize_columns(df=df)
      # Update counts and statistics
      self.update_statistics(df)
    # Compile metadata for all columns
    self.compile_metadata()
    return self.metadata


  def initialize_columns(self, df):
    print('Initializing columns...')
    print('df cols:::' , df.columns)
    self.columns = df.columns.tolist()
    print('columns:', self.columns)
    for idx, col in enumerate(self.columns):
      # Record data type and order
      self.data_types[col] = str(df[col].dtype)
      self.column_order[col] = idx
      # Initialize counts and unique values
      self.total_counts[col] = 0
      self.non_null_counts[col] = 0
      self.valid_counts[col] = 0
      self.unique_values[col] = set()

      # Decide whether to treat the column as numeric or string
      if pd.api.types.is_numeric_dtype(df[col]):
        # Initialize structures for numeric columns
        self.numeric_stats[col] = {
            'sum': 0.0,
            'sum_sq': 0.0,
            'min': np.inf,
            'max': -np.inf,
            'count': 0,
            'finite_count': 0,
            'all_data': []  # For quantile calculation
        }
        self.histograms[col] = Counter()
      elif data_cleaning.is_date_column(series=df[col]):
        # Convert to datetime
        df[col] = pd.to_datetime(df[col], errors='coerce')
        self.datetime_stats[col] = {
          'min': None,
          'max': None,
          'mean': None,
          'all_data': []
        }
      else:
        # Initialize structures for string columns
        self.string_stats[col] = Counter()


  def update_statistics(self, df):
    for col in self.columns:
      col_data = df[col]
      self.total_counts[col] += len(col_data)
      # Count non-null (not NaN) values
      non_null_mask = col_data.notnull()
      self.non_null_counts[col] += non_null_mask.sum()
      # Update unique values
      self.unique_values[col].update(col_data.dropna().unique())
      if col in self.numeric_stats:
        # Process numeric columns
        self.process_numeric_column(col, col_data)
      elif col in self.datetime_stats:
        # Process datetime columns
        self.process_datetime_column(col, col_data)
      else:
        # Process string columns
        self.process_string_column(col, col_data)


  def compile_metadata(self):
    for col in self.columns:
      # Initialize column metadata
      col_metadata = {
        'type': 'OBJECT_TYPE_TABLE_COLUMN',
        'key': str(uuid.uuid4().hex),
        'name': col,
        'description': '',  # Add descriptions if available
        'table_column_info': {},
        'table_column_metrics': {}
      }
      # Populate table column info
      col_info = {
        'order': self.column_order[col],
        'original_type': self.data_types[col],
      }


      if col in self.numeric_stats:
        # Column is numeric
        col_info['type'] = 'NUMERIC'
        col_info['extended_type'] = 'INTEGER' if pd.api.types.is_integer_dtype(self.data_types[col]) else 'FLOAT'
        # Compute numeric metrics
        col_metrics = self.compute_numeric_metrics(col, histogram_method="fd")
      elif col in self.datetime_stats:
        # Column is datetime
        col_info['type'] = 'DATE_TIME'
        col_info['extended_type'] = 'DATE_TIME'
        # Compute datetime metrics
        col_metrics = self.compute_datetime_metrics(col)
      else:
        # Column is string
        col_info['type'] = 'STRING'
        col_info['extended_type'] = 'STRING'
        # Compute string metrics
        col_metrics = self.compute_string_metrics(col)
        
      col_metadata['table_column_info'] = col_info
      col_metadata['table_column_metrics'] = col_metrics
      self.metadata.append(col_metadata)


  def process_numeric_column(self, col, col_data):
    # Convert to numeric, coercing errors to NaN
    numeric_col_data = pd.to_numeric(col_data, errors='coerce')
    # Filter finite numbers (exclude NaN and infinity)
    finite_data = numeric_col_data[np.isfinite(numeric_col_data)]
    self.valid_counts[col] += finite_data.count()
    if not finite_data.empty:
      stats = self.numeric_stats[col]
      # Update sum and sum of squares
      stats['sum'] += finite_data.sum()
      stats['sum_sq'] += (finite_data ** 2).sum()
      # Update min and max
      stats['min'] = min(stats['min'], finite_data.min())
      stats['max'] = max(stats['max'], finite_data.max())
      # Update counts
      count = finite_data.count()
      stats['count'] += count
      stats['finite_count'] += count
      # Collect data for quantile calculation
      stats['all_data'].extend(finite_data.tolist())

  
  def process_string_column(self, col, col_data):
    # Count valid (non-null) entries
    non_null_mask = col_data.notnull()
    self.valid_counts[col] += non_null_mask.sum()
    # Update string value counts
    self.string_stats[col].update(col_data.dropna().astype(str))


   
  def process_datetime_column(self, col, col_data):
    col_data = pd.to_datetime(col_data, errors='coerce')
    finite_data = col_data.dropna()
    if not finite_data.empty:
        stats = self.datetime_stats[col]
        # Update min and max
        min_date = finite_data.min()
        max_date = finite_data.max()
        stats['min'] = min_date if stats['min'] is None else min(stats['min'], min_date)
        stats['max'] = max_date if stats['max'] is None else max(stats['max'], max_date)
        # Collect data for mean and histogram
        stats['all_data'].extend(finite_data.tolist())
  
 
  def compute_numeric_metrics(self, col, histogram_method='fd'):
    stats = self.numeric_stats[col]
    count = stats['count']
    # Compute mean
    mean = stats['sum'] / count if count > 0 else np.nan
    # Compute variance and standard deviation
    variance = (stats['sum_sq'] / count - mean ** 2) if count > 0 else np.nan
    std_dev = np.sqrt(variance) if variance >= 0 else np.nan
    # Calculate quantiles
    quantiles = []
    histogram = {'buckets': []}
    if stats['all_data']:
        data = np.array(stats['all_data'])
        quantile_values = np.quantile(data, [0.25, 0.5, 0.75])
        quantiles = [
            {'point': 0.25, 'value': quantile_values[0]},
            {'point': 0.5, 'value': quantile_values[1]},
            {'point': 0.75, 'value': quantile_values[2]},
        ]
        # Calculate histogram using the specified method
        histogram = self.calculate_histogram(data, method=histogram_method)
    # Compile numeric metrics
    col_metrics = {
        'total_count': self.total_counts[col],
        'non_null_count': self.non_null_counts[col],
        'valid_count': self.valid_counts[col],
        'numeric_metrics': {
            'finite_count': stats['finite_count'],
            'mean': mean,
            'standard_deviation': std_dev,
            'minimum': stats['min'] if stats['min'] != np.inf else np.nan,
            'maximum': stats['max'] if stats['max'] != -np.inf else np.nan,
            'quantiles': quantiles,
            'histogram': histogram
        }
    }
    return col_metrics
  

  def compute_string_metrics(self, col):
    counts = self.string_stats[col].most_common()
    most_common_value = counts[0][0] if counts else None
    most_common_value_count = counts[0][1] if counts else 0
    # Prepare counts data (top 5 values)
    counts_data = [{'key': k, 'value': v} for k, v in counts[:5]]
    # Compile string metrics
    col_metrics = {
        'total_count': self.total_counts[col],
        'non_null_count': self.non_null_counts[col],
        'valid_count': self.valid_counts[col],
        'string_metrics': {
            'most_common_value': most_common_value,
            'most_common_value_count': most_common_value_count,
            'counts': counts_data,
            'unique_value_count': len(self.unique_values[col])
        }
    }
    return col_metrics
  

  def compute_datetime_metrics(self, col):
    stats = self.datetime_stats[col]
    data = stats['all_data']
    if data:
        data_series = pd.Series(data)
        mean_date = data_series.mean()
        min_date = stats['min']
        max_date = stats['max']
        # Generate histogram
        histogram = self.calculate_datetime_histogram(data_series)
    else:
        mean_date = None
        min_date = None
        max_date = None
        histogram = {'buckets': []}

    col_metrics = {
        'total_count': self.total_counts[col],
        'non_null_count': self.non_null_counts[col],
        'valid_count': self.valid_counts[col],
        'date_time_metrics': {
            'mean': mean_date.isoformat() if mean_date else None,
            'minimum': min_date.isoformat() if min_date else None,
            'maximum': max_date.isoformat() if max_date else None,
            'histogram': histogram
        }
    }
    return col_metrics


  def calculate_histogram(self, data, method='fd'):
    histogram = {'buckets': []}
    
    if method == 'fd':
        # Freedman-Diaconis rule
        q25, q75 = np.percentile(data, [25, 75])
        iqr = q75 - q25
        bin_width = 2 * iqr / np.cbrt(len(data))
        if bin_width == 0:
            bin_width = 1
        bin_count = int(np.ceil((data.max() - data.min()) / bin_width))
    elif method == 'sturges':
        # Sturges' formula
        bin_count = int(np.ceil(np.log2(len(data)) + 1))
    elif method == 'rice':
        # Rice Rule
        bin_count = int(np.ceil(2 * np.cbrt(len(data))))
    elif method == 'sqrt':
        # Square Root Choice
        bin_count = int(np.ceil(np.sqrt(len(data))))
    elif method == 'doane':
        # Doane's formula
        skewness = pd.Series(data).skew()
        sigma_g1 = np.sqrt((6 * (len(data) - 2)) / ((len(data) + 1) * (len(data) + 3)))
        bin_count = int(1 + np.log2(len(data)) + np.log2(1 + abs(skewness) / sigma_g1))
    elif method == 'scott':
        # Scott's rule
        std_dev = np.std(data)
        bin_width = 3.5 * std_dev / np.cbrt(len(data))
        if bin_width == 0:
            bin_width = 1
        bin_count = int(np.ceil((data.max() - data.min()) / bin_width))
    elif method == 'custom':
        # Custom bin count
        bin_count = 10  # You can set this to any fixed number
    else:
        # Default to Freedman-Diaconis if method not recognized
        method = 'fd'
        q25, q75 = np.percentile(data, [25, 75])
        iqr = q75 - q25
        bin_width = 2 * iqr / np.cbrt(len(data))
        if bin_width == 0:
            bin_width = 1
        bin_count = int(np.ceil((data.max() - data.min()) / bin_width))
    
    if bin_count < 1:
        bin_count = 1  # Ensure at least one bin
    
    counts, bin_edges = np.histogram(data, bins=bin_count)
    
    for idx in range(len(counts)):
        bucket = {
            'index': idx,
            'label': f"{bin_edges[idx]:.2f} - {bin_edges[idx+1]:.2f}",
            'left_value': bin_edges[idx],
            'right_value': bin_edges[idx+1],
            'count': int(counts[idx])
        }
        histogram['buckets'].append(bucket)
    
    return histogram


  def calculate_datetime_histogram(self, data_series, bins=10):
    histogram_data = {'buckets': []}
    counts, bin_edges = np.histogram(data_series.values.astype(np.int64) // 10 ** 9, bins=bins)
    bin_edges = pd.to_datetime(bin_edges * 1e9)
    for idx in range(len(counts)):
        bucket = {
            'index': idx,
            'label': f"{bin_edges[idx].date()} - {bin_edges[idx+1].date()}",
            'left_value': bin_edges[idx].isoformat(),
            'right_value': bin_edges[idx+1].isoformat(),
            'count': int(counts[idx])
        }
        histogram_data['buckets'].append(bucket)
    return histogram_data
