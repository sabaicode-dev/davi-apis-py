import pandas as pd
import numpy as np
import uuid
from collections import Counter
from utils.file_util import is_boolean_column

from metafile.api.services import data_cleaning
from metafile.api.models import Metadata


import logging

logger = logging.getLogger(__name__)

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


  # def initialize_columns(self, df):
  #   print('Initializing columns...')
  #   print('df cols:::' , df.columns)
  #   self.columns = df.columns.tolist()
  #   print('columns:', self.columns)
  #   for idx, col in enumerate(self.columns):
  #     # Record data type and order
  #     self.data_types[col] = str(df[col].dtype)
  #     self.column_order[col] = idx
  #     # Initialize counts and unique values
  #     self.total_counts[col] = 0
  #     self.non_null_counts[col] = 0
  #     self.valid_counts[col] = 0
  #     self.unique_values[col] = set()

  #     # Decide whether to treat the column as numeric or string
  #     if pd.api.types.is_numeric_dtype(df[col]):
  #       # Initialize structures for numeric columns
  #       self.numeric_stats[col] = {
  #           'sum': 0.0,
  #           'sum_sq': 0.0,
  #           'min': np.inf,
  #           'max': -np.inf,
  #           'count': 0,
  #           'finite_count': 0,
  #           'all_data': []  # For quantile calculation
  #       }
  #       self.histograms[col] = Counter()
  #     elif data_cleaning.is_date_column(series=df[col]):
  #       # Convert to datetime
  #       df[col] = pd.to_datetime(df[col], errors='coerce')
  #       self.datetime_stats[col] = {
  #         'min': None,
  #         'max': None,
  #         'mean': None,
  #         'all_data': []
  #       }
  #     else:
  #       # Initialize structures for string columns
  #       self.string_stats[col] = Counter()

  def initialize_columns(self, df):
    print('Initializing columns...')
    self.columns = df.columns.tolist()
    
    for idx, col in enumerate(self.columns):
        # Record data type and order
        self.data_types[col] = str(df[col].dtype)
        self.column_order[col] = idx
        
        # Initialize counts and unique values
        self.total_counts[col] = 0
        self.non_null_counts[col] = 0
        self.valid_counts[col] = 0
        self.unique_values[col] = set()

        # Initialize appropriate statistics based on column type
        if is_boolean_column(df[col]):
            self.string_stats[col] = Counter()  # We'll use this for boolean values too
        elif pd.api.types.is_numeric_dtype(df[col]):
            self.numeric_stats[col] = {
                'sum': 0.0,
                'sum_sq': 0.0,
                'min': np.inf,
                'max': -np.inf,
                'count': 0,
                'finite_count': 0,
                'all_data': []
            }
        elif data_cleaning.is_date_column(df[col]):
            df[col] = pd.to_datetime(df[col], errors='coerce')
            self.datetime_stats[col] = {
                'min': None,
                'max': None,
                'mean': None,
                'all_data': []
            }
        else:
            self.string_stats[col] = Counter()

  def process_boolean_column(self, col, col_data):
    """Process boolean column data safely."""
    try:
        if col not in self.string_stats:
            self.string_stats[col] = Counter()
            
        # Convert to string and standardize
        str_data = col_data.fillna('').astype(str).str.lower().str.strip()
        
        # Map various boolean representations to True/False
        bool_map = {
            'true': True, '1': True, 'yes': True, 't': True, 'y': True,
            'false': False, '0': False, 'no': False, 'f': False, 'n': False,
            '': None  # Handle empty strings
        }
        
        # Count valid values
        valid_mask = str_data.isin(bool_map.keys())
        self.valid_counts[col] += valid_mask.sum()
        
        # Update string stats for boolean values
        valid_data = str_data[valid_mask]
        if not valid_data.empty:
            value_counts = valid_data.value_counts()
            for value, count in value_counts.items():
                self.string_stats[col][value] += count
            
    except Exception as e:
        logger.error(f"Error processing boolean column {col}: {str(e)}")
        # Initialize empty counter if error occurs
        self.string_stats[col] = Counter()
  # def update_statistics(self, df):
  #   for col in self.columns:
  #     col_data = df[col]
  #     self.total_counts[col] += len(col_data)
  #     # Count non-null (not NaN) values
  #     non_null_mask = col_data.notnull()
  #     self.non_null_counts[col] += non_null_mask.sum()
  #     # Update unique values
  #     self.unique_values[col].update(col_data.dropna().unique())
  #     if col in self.numeric_stats:
  #       # Process numeric columns
  #       self.process_numeric_column(col, col_data)
  #     elif col in self.datetime_stats:
  #       # Process datetime columns
  #       self.process_datetime_column(col, col_data)
  #     else:
  #       # Process string columns
  #       self.process_string_column(col, col_data)

  def update_statistics(self, df):
    try:
        for col in self.columns:
            try:
                col_data = df[col]
                self.total_counts[col] += len(col_data)

                # Count non-null values
                non_null_mask = col_data.notnull()
                self.non_null_counts[col] += non_null_mask.sum()

                # Update unique values safely
                try:
                    unique_vals = col_data.dropna().unique()
                    if isinstance(unique_vals, np.ndarray):
                        unique_vals = unique_vals.tolist()
                    self.unique_values[col].update(unique_vals)
                except Exception as e:
                    logger.warning(f"Error updating unique values for column {col}: {str(e)}")

                # Process column based on type
                if col in self.numeric_stats:
                    self.process_numeric_column(col, col_data)
                elif col in self.datetime_stats:
                    self.process_datetime_column(col, col_data)
                elif is_boolean_column(col_data):
                    self.process_boolean_column(col, col_data)
                else:
                    self.process_string_column(col, col_data)
                    
            except KeyError:
                logger.error(f"Column {col} not found in dataframe")
                continue
            except Exception as e:
                logger.error(f"Error processing column {col}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in update_statistics: {str(e)}")
        raise



  # def compile_metadata(self):
  #   for col in self.columns:
  #     # Initialize column metadata
  #     col_metadata = {
  #       'type': 'OBJECT_TYPE_TABLE_COLUMN',
  #       'key': str(uuid.uuid4().hex),
  #       'name': col,
  #       'description': '',  # Add descriptions if available
  #       'table_column_info': {},
  #       'table_column_metrics': {}
  #     }
  #     # Populate table column info
  #     col_info = {
  #       'order': self.column_order[col],
  #       'original_type': self.data_types[col],
  #     }


  #     if col in self.numeric_stats:
  #       # Column is numeric
  #       col_info['type'] = 'NUMERIC'
  #       col_info['extended_type'] = 'INTEGER' if pd.api.types.is_integer_dtype(self.data_types[col]) else 'FLOAT'
  #       # Compute numeric metrics
  #       col_metrics = self.compute_numeric_metrics(col, histogram_method="fd")
  #     elif col in self.datetime_stats:
  #       # Column is datetime
  #       col_info['type'] = 'DATE_TIME'
  #       col_info['extended_type'] = 'DATE_TIME'
  #       # Compute datetime metrics
  #       col_metrics = self.compute_datetime_metrics(col)
  #     else:
  #       # Column is string
  #       col_info['type'] = 'STRING'
  #       col_info['extended_type'] = 'STRING'
  #       # Compute string metrics
  #       col_metrics = self.compute_string_metrics(col)
        
  #     col_metadata['table_column_info'] = col_info
  #     col_metadata['table_column_metrics'] = col_metrics
  #     self.metadata.append(col_metadata)

  def compile_metadata(self):
    try:
        for col in self.columns:
            try:
                col_metadata = {
                    'type': 'OBJECT_TYPE_TABLE_COLUMN',
                    'key': str(uuid.uuid4().hex),
                    'name': col,
                    'description': '',
                    'table_column_info': {},
                    'table_column_metrics': {}
                }

                # Determine column type
                col_info = {
                    'order': self.column_order.get(col, 0),
                    'original_type': self.data_types.get(col, 'unknown'),
                }

                try:
                    # Get column data for type checking
                    if col in self.string_stats:
                        series = pd.Series(list(self.string_stats[col].elements()))
                        is_bool = is_boolean_column(series)
                    else:
                        is_bool = False

                    # Assign type and metrics based on column characteristics
                    if is_bool:
                        col_info['type'] = 'BOOLEAN'
                        col_info['extended_type'] = 'BOOLEAN'
                        col_metrics = self.compute_boolean_metrics(col)
                    elif col in self.numeric_stats:
                        col_info['type'] = 'NUMERIC'
                        col_info['extended_type'] = 'INTEGER' if 'int' in self.data_types.get(col, '') else 'FLOAT'
                        col_metrics = self.compute_numeric_metrics(col)
                    elif col in self.datetime_stats:
                        col_info['type'] = 'DATE_TIME'
                        col_info['extended_type'] = 'DATE_TIME'
                        col_metrics = self.compute_datetime_metrics(col)
                    else:
                        col_info['type'] = 'STRING'
                        col_info['extended_type'] = 'STRING'
                        col_metrics = self.compute_string_metrics(col)

                except Exception as e:
                    logger.error(f"Error determining column type for {col}: {str(e)}")
                    # Fallback to string type
                    col_info['type'] = 'STRING'
                    col_info['extended_type'] = 'STRING'
                    col_metrics = self.compute_string_metrics(col)

                col_metadata['table_column_info'] = col_info
                col_metadata['table_column_metrics'] = col_metrics
                self.metadata.append(col_metadata)

            except Exception as e:
                logger.error(f"Error processing metadata for column {col}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Error in compile_metadata: {str(e)}")
        raise


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

  
  # def process_string_column(self, col, col_data):
  #   # Count valid (non-null) entries
  #   non_null_mask = col_data.notnull()
  #   self.valid_counts[col] += non_null_mask.sum()
  #   # Update string value counts
  #   self.string_stats[col].update(col_data.dropna().astype(str))

  def process_string_column(self, col, col_data):
    # Handle non-null values
    non_null_mask = col_data.notnull()
    self.valid_counts[col] += non_null_mask.sum()
    
    # Convert to string and standardize case
    str_data = col_data.dropna().astype(str).str.lower()
    
    # Update string value counts without using numpy operations
    for value in str_data:
        self.string_stats[col][value] += 1
   
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












  # Detect metadata for boolean type
  def _process_column(self, series):
      column_type = self._detect_column_type(series)
      metrics = self._compute_column_metrics(series, column_type)
      return {
          "name": series.name,
          "type": column_type,
          "metrics": metrics,
      }
  def _detect_column_type(self, series):
      if is_boolean_column(series):
          return "BOOLEAN"
      elif data_cleaning.is_date_column(series):
          return "DATE_TIME"
      elif pd.api.types.is_numeric_dtype(series):
          return "NUMERIC"
      else:
          return "STRING"
  def compute_column_metrics(self, series, column_type):
      if column_type == "NUMERIC":
          return self.compute_numeric_metrics(series)
      elif column_type == "DATE_TIME":
          return self.compute_datetime_metrics(series)
      elif column_type == "BOOLEAN":
          return self.compute_boolean_metrics(series)
      else:
          return self.compute_string_metrics(series)
      
  # def compute_boolean_metrics(self, col):
  #   """Compute metrics specific to boolean columns."""
  #   # Get the series data
  #   data = pd.Series(self.string_stats[col].elements())
    
  #   # Convert to standardized boolean values
  #   bool_map = {
  #       'true': True, '1': True, 'yes': True, 't': True, 'y': True,
  #       'false': False, '0': False, 'no': False, 'f': False, 'n': False
  #   }
    
  #   standardized_data = data.str.lower().map(bool_map)
    
  #   # Calculate metrics
  #   total_true = int((standardized_data == True).sum())
  #   total_false = int((standardized_data == False).sum())
    
  #   return {
  #       'total_count': self.total_counts[col],
  #       'non_null_count': self.non_null_counts[col],
  #       'valid_count': self.valid_counts[col],
  #       'boolean_metrics': {
  #           'true_count': total_true,
  #           'false_count': total_false,
  #           'true_ratio': float(total_true / len(standardized_data)) if len(standardized_data) > 0 else 0.0
  #       }
  #   }

  def compute_boolean_metrics(self, col):
    """Compute metrics specific to boolean columns."""
    try:
        counts = self.string_stats.get(col, Counter())
        
        # Map various boolean representations
        true_values = {'true', '1', 'yes', 't', 'y'}
        false_values = {'false', '0', 'no', 'f', 'n'}
        
        # Calculate true/false counts safely
        true_count = sum(counts.get(val, 0) for val in true_values)
        false_count = sum(counts.get(val, 0) for val in false_values)
        total_valid = true_count + false_count
        
        return {
            'total_count': self.total_counts.get(col, 0),
            'non_null_count': self.non_null_counts.get(col, 0),
            'valid_count': self.valid_counts.get(col, 0),
            'boolean_metrics': {
                'true_count': true_count,
                'false_count': false_count,
                'true_ratio': float(true_count / total_valid) if total_valid > 0 else 0.0,
                'counts': [
                    {'value': 'true', 'count': true_count},
                    {'value': 'false', 'count': false_count}
                ]
            }
        }
    except Exception as e:
        logger.error(f"Error computing boolean metrics for column {col}: {str(e)}")
        # Return basic metrics structure
        return {
            'total_count': self.total_counts.get(col, 0),
            'non_null_count': self.non_null_counts.get(col, 0),
            'valid_count': 0,
            'boolean_metrics': {
                'true_count': 0,
                'false_count': 0,
                'true_ratio': 0.0,
                'counts': []
            }
        }


def update_description(metadata_key, new_description):
    """
    Update the description of a column in the metadata based on its key.

    Args:
        metadata_key (str): The key of the column whose description needs to be updated.
        new_description (str): The new description to set.

    Returns:
        dict: Result message indicating success or failure.
    """
    try:
        # Find the metadata instance containing the column
        metadata_instance = Metadata.objects.filter(metadata__contains=[{"key": metadata_key}]).first()

        if not metadata_instance:
            return {"error": "Metadata not found"}

        # Update the description field for the matching key
        updated = False
        for column in metadata_instance.metadata:
            if column["key"] == metadata_key:
                column["description"] = new_description
                updated = True
                break

        if not updated:
            return {"error": "Key not found in metadata"}

        # Save the updated metadata instance
        metadata_instance.save()
        return {"message": "Description updated successfully"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
