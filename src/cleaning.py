import pandas as pd

df = pd.read_csv('data/dataset.csv')

# _____________________<( Columns )>___________________________
df_columns = df.columns
print(df_columns)
# ['Unnamed: 0', 'Pregnancies', 'Glucose', 'BloodPressure','SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']


# _____________________<( DF Shape )>__________________________
print(df.shape) #(768, 9)

# _____________________<( exemple de data )>___________________
print(df.head(3))
#    Unnamed: 0  Pregnancies  Glucose  BloodPressure  SkinThickness  Insulin   BMI  DiabetesPedigreeFunction  Age
# 0           0            6      148             72             35        0  33.6                     0.627   50
# 1           1            1       85             66             29        0  26.6                     0.351   31
# 2           2            8      183             64              0        0  23.3                     0.672   32


# _____________________<( identifier les doublons )>___________________
dupl_sum = df.duplicated().sum()
print(f'nombre des doubons : {dupl_sum}')
# nombre des doubons : 0

# _____________________<( identifier null values )>___________________
null_values = df.isna().sum()
print(f'null values in each column : {null_values}')

# null values in each column : Unnamed: 0                  0
# Pregnancies                 0
# Glucose                     0
# BloodPressure               0
# SkinThickness               0
# Insulin                     0
# BMI                         0
# DiabetesPedigreeFunction    0
# Age                         0


# _____________________<( columns data type )>___________________
column_type = df.dtypes
print(f'columns types : {column_type}')

# columns types : 
# Unnamed: 0                    int64
# Pregnancies                   int64
# Glucose                       int64
# BloodPressure                 int64
# SkinThickness                 int64
# Insulin                       int64
# BMI                         float64
# DiabetesPedigreeFunction    float64
# Age                           int64


# _____________________<( drop the index column )>___________________
df = df.drop(columns=['Unnamed: 0'])

# _____________________<( search for outliers )>___________________
import seaborn as sns
import matplotlib.pyplot as plt

sns.boxplot(x=df['delivery_time'])
plt.show()
