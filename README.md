# df_report
makes exploratory statistics of data in a pandas/DataFrame

df_report automates statatistics :
 - shape rows, columns and cells numbers;
 - info() like with percents;
 - describes() or/and values_counts for each column;
 - duplicated().sum() for DataFrame and DataFrames without each column;
 - DataFrame.corr()

positional arguments:
  filename
options:
  -h, --help            show this help message and exit
  -s SEP, --sep SEP     column separator
  --target TARGET       name of the target column(s)
  --index INDEX
  --max_list_len MAX_LIST_LEN
  --encoding ENCODING
  -v, --verbose

df_report may be use as a callable function or a command.
