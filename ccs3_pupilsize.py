# -*- coding: utf-8 -*-
"""CCS3_pupilsize.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1vEylsUOYPjd0eXodjavsIA6sluSXjp1H
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
#for anova
import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy import stats

file_path = '/content/drive/MyDrive/CCS3/data_renia/Figure2a_pupil size.xlsx'
df = pd.read_excel(file_path, sheet_name='Sheet1')

df.head()

# Select the time columns for clustering
X = df[[-2, -1, 0, 1, 2]]

# Standardize the features (KMeans works better with normalized data)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Set the number of clusters
kmeans = KMeans(n_clusters=4, random_state=42)

# Fit the KMeans model
kmeans.fit(X_scaled)

# Get the cluster labels
df['Cluster'] = kmeans.labels_

# View the first few rows with the clusters
df[['SubID', 'Group', 'Cluster']].head()


# Import PCA for visualization
from sklearn.decomposition import PCA

# Reduce data to 2 components for visualization
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

# Add the PCA components to the dataframe
df['PCA1'] = X_pca[:, 0]
df['PCA2'] = X_pca[:, 1]

# Plot the clusters
plt.figure(figsize=(8,6))
sns.scatterplot(x='PCA1', y='PCA2', hue='Cluster', data=df, palette='viridis', s=100)
plt.title('K-means Clustering with 4 Groups')
plt.show()

# Compare the original group labels with the clusters
df.groupby(['Group', 'Cluster']).size().unstack().fillna(0)

from sklearn.metrics import silhouette_score
score = silhouette_score(X_scaled, kmeans.labels_)
print(f'Silhouette Score: {score}')

# Compare the original group labels with the clusters
comparison = df.groupby(['Group', 'Cluster']).size().unstack().fillna(0)
print(comparison)

# Calculate descriptive statistics for each group
descriptive_stats = df.groupby('Group')[[-2, -1, 0, 1, 2]].describe()
print(descriptive_stats[0])

#is there a statistically significant difference across the mean values of the groups?
# Melt the DataFrame so that all the columns (-2, -1, 0, 1, 2) are in a single column
df_melted = df.melt(id_vars=['SubID', 'Group'], value_vars=[-2, -1, 0, 1, 2],
                    var_name='Measurement', value_name='Value')

print(df_melted.head())


# Fit the ANOVA model
model = ols('Value ~ Group', data=df_melted).fit()
anova_table = sm.stats.anova_lm(model, typ=2)
print(anova_table)


from statsmodels.stats.multicomp import pairwise_tukeyhsd

#Tukey HSD
tukey = pairwise_tukeyhsd(endog=df_melted['Value'], groups=df_melted['Group'], alpha=0.05)
print(tukey)

"""PREPICTION OF MEMORY SCORES"""

import pandas as pd
file1 = pd.read_excel('/content/drive/MyDrive/CCS3/data_renia/Figure2a_pupil size.xlsx')
file2 = pd.read_excel('/content/drive/MyDrive/CCS3/data_renia/Figure5A-5D.xlsx')

columns_to_keep_file1 = ['SubID', 'Group'] + file1.columns[-5:].tolist()  # Last two columns
columns_to_keep_file2 = ['memory1（remember）', 'memory2（detail）']

#DataFrames with selected columns
df1 = file1[columns_to_keep_file1]
df2 = file2[columns_to_keep_file2]

combined_df = pd.concat([df1.reset_index(drop=True), df2.reset_index(drop=True)], axis=1)

print(combined_df)

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

file1 = pd.read_excel('/content/drive/MyDrive/CCS3/data_renia/Figure2a_pupil size.xlsx')
file2 = pd.read_excel('/content/drive/MyDrive/CCS3/data_renia/Figure5A-5D.xlsx')

columns_to_keep_file1 = ['SubID', 'Group'] + file1.columns[-2:].tolist()  # Last two columns
columns_to_keep_file2 = ['memory1（remember）', 'memory2（detail）']

df1 = file1[columns_to_keep_file1]
df2 = file2[columns_to_keep_file2]
combined_df = pd.concat([df1.reset_index(drop=True), df2.reset_index(drop=True)], axis=1)

features = combined_df[['Group']].join(combined_df.iloc[:, 2:-2])  # Include 'Group' and the last three columns
target1 = combined_df['memory1（remember）']
target2 = combined_df['memory2（detail）']
features = pd.get_dummies(features, columns=['Group'], drop_first=True)
features.columns = features.columns.astype(str)

#training and testing sets
X_train, X_test, y_train1, y_test1 = train_test_split(features, target1, test_size=0.2, random_state=42)
X_train2, X_test2, y_train2, y_test2 = train_test_split(features, target2, test_size=0.2, random_state=42)

#regression model for the first memory score
model1 = LinearRegression()
model1.fit(X_train, y_train1)

#regression model for the second memory score
model2 = LinearRegression()
model2.fit(X_train2, y_train2)

predictions1 = model1.predict(X_test)
predictions2 = model2.predict(X_test2)

# Get the group information from the original DataFrame
group_info = combined_df.loc[X_test.index, 'Group']

# Combine predictions with actual values and group information
results_memory1 = pd.DataFrame({
    'Actual memory1': y_test1,
    'Predicted memory1': predictions1,
    'Group': group_info
})

results_memory2 = pd.DataFrame({
    'Actual memory2': y_test2,
    'Predicted memory2': predictions2,
    'Group': group_info
})


print(results_memory1.head())

#MSE claculations
grouped_memory1 = results_memory1.groupby('Group').apply(lambda x: mean_squared_error(x['Actual memory1'], x['Predicted memory1']))
grouped_memory2 = results_memory2.groupby('Group').apply(lambda x: mean_squared_error(x['Actual memory2'], x['Predicted memory2']))

print("Mean Squared Error by Group for memory1 (remember):")
print(grouped_memory1)

print("\nMean Squared Error by Group for memory2 (detail):")
print(grouped_memory2)

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import scipy.stats as stats
# Prepare features and target variables
features = combined_df.iloc[:, 2:7]  # Adjust the index based on your actual DataFrame structure
target1 = combined_df['memory1（remember）']
target2 = combined_df['memory2（detail）']

# Ensure all column names are strings
features.columns = features.columns.astype(str)

# Split the data into training and testing sets for both memory scores
X_train, X_test, y_train1, y_test1 = train_test_split(features, target1, test_size=0.2, random_state=42)
X_train2, X_test2, y_train2, y_test2 = train_test_split(features, target2, test_size=0.2, random_state=42)

# Train the regression model for the first memory score
model1 = LinearRegression()
model1.fit(X_train, y_train1)

# Train the regression model for the second memory score
model2 = LinearRegression()
model2.fit(X_train2, y_train2)

# Make predictions
predictions1 = model1.predict(X_test)
predictions2 = model2.predict(X_test2)

# Calculate MSE for both memory scores
mse_memory1 = mean_squared_error(y_test1, predictions1)
mse_memory2 = mean_squared_error(y_test2, predictions2)

print(f'Mean Squared Error for memory1 (remember): {mse_memory1}')
print(f'Mean Squared Error for memory2 (detail): {mse_memory2}')

# Group memory scores by group for ANOVA
grouped_memory1 = combined_df.groupby('Group')['memory1（remember）'].apply(list)
grouped_memory2 = combined_df.groupby('Group')['memory2（detail）'].apply(list)

# Perform ANOVA test for memory1
anova_memory1 = stats.f_oneway(*grouped_memory1)
print(f'ANOVA test results for memory1 (remember): F-statistic = {anova_memory1.statistic}, p-value = {anova_memory1.pvalue}')

# Perform ANOVA test for memory2
anova_memory2 = stats.f_oneway(*grouped_memory2)
print(f'ANOVA test results for memory2 (detail): F-statistic = {anova_memory2.statistic}, p-value = {anova_memory2.pvalue}')

#DESCRIPTIVES
mean_scores_memory1 = combined_df.groupby('Group')['memory1（remember）'].mean().sort_values(ascending=False)
mean_scores_memory2 = combined_df.groupby('Group')['memory2（detail）'].mean().sort_values(ascending=False)


print("Mean scores for memory1 (remember):")
print(mean_scores_memory1)
print("\nMean scores for memory2 (detail):")
print(mean_scores_memory2)

"""DOES PUPIL DIAMETER MEDIATE THE RELATIONSHIP BETWEEN GROUP & MEMORY SCORES?"""

#CODE TO EXPLORE THE QUESTION: does pupil size relate to memory performance metrics?
import pandas as pd
import pandas as pd

file1 = pd.read_excel('/content/drive/MyDrive/CCS3/data_renia/Figure2a_pupil size.xlsx')
file2 = pd.read_excel('/content/drive/MyDrive/CCS3/data_renia/Figure5A-5D.xlsx')

columns_to_keep_file1 = ['SubID', 'Group'] + file1.columns[-5:].tolist()  # Last two columns
columns_to_keep_file2 = ['memory1（remember）', 'memory2（detail）']
df1 = file1[columns_to_keep_file1]
df2 = file2[columns_to_keep_file2]

combined_df = pd.concat([df1.reset_index(drop=True), df2.reset_index(drop=True)], axis=1)

print(combined_df)
# Print the column names to check
print(combined_df.columns)

correlation_columns = [-2, -1, 0, 1, 2, 'memory1（remember）', 'memory2（detail）']
correlation_data = combined_df[correlation_columns]

#correlation matrix
correlation_matrix = correlation_data.corr()
print("Correlation Matrix:")
print(correlation_matrix)

"""conclusion: weak positive association between pupil size at certain points and memory performance, hinting at a potential but limited connection between pupil size and memory recall."""

#correlation matrix for the short-R group
short_r_data = combined_df[combined_df['Group'] == 'short-R']
correlation_columns = [-2, -1, 0, 1, 2, 'memory1（remember）', 'memory2（detail）']
short_r_correlation_data = short_r_data[correlation_columns]
short_r_correlation_matrix = short_r_correlation_data.corr()


print("Correlation Matrix for Short-R Group:")
print(short_r_correlation_matrix)

"""In the following part I perform regression. Only within the short-R group. Question: do changes in pupil dilation predict differences in memory scores?"""

import statsmodels.api as sm

combined_df['Group'] = combined_df['Group'].str.strip().str.lower()
#filter for the 'short-r' group (lowercase, as standardized above)
short_r_group = combined_df[combined_df['Group'] == 'short-r']

print(short_r_group)

# Define the independent variables (dilation values) and dependent variables (memory scores)
X = short_r_group[[-2, -1, 0, 1, 2]]
y_memory1 = short_r_group['memory1（remember）']
y_memory2 = short_r_group['memory2（detail）']

# Add a constant to the model (intercept)
X = sm.add_constant(X)

# Fit linear regression models for both memory scores
model_memory1 = sm.OLS(y_memory1, X).fit()
model_memory2 = sm.OLS(y_memory2, X).fit()


print("Memory1（remember） Regression Results:")
print(model_memory1.summary())
print("\nMemory2（detail） Regression Results:")
print(model_memory2.summary())

"""Result: pupil dilation alone, at these time segmentation points, does not predict memory performance across this subset of participants (short-R group)."""

#BELOW REGRESSION WITHIN ALL SUBGROUPS IS PERFORMED

# Function to perform OLS regression for a specific group
def run_regression_for_group(group_name):
    combined_df['Group'] = combined_df['Group'].str.strip().str.lower()
    group_data = combined_df[combined_df['Group'] == group_name]

    #(predictor (X) and outcome (y) variables
    X = group_data[[-2, -1, 0, 1, 2]]  # Dilation values
    X = sm.add_constant(X)  # Add constant term for intercept

    # Memory1 (Remember) and Memory2 (Detail) as outcome variables
    y_memory1 = group_data['memory1（remember）']
    y_memory2 = group_data['memory2（detail）']

    # Fit
    model_memory1 = sm.OLS(y_memory1, X).fit()
    model_memory2 = sm.OLS(y_memory2, X).fit()

    # Print
    print(f"\n--- Regression Results for {group_name.capitalize()} Group ---")

    print("\nMemory1 (Remember) Regression Results:")
    print(model_memory1.summary())

    print("\nMemory2 (Detail) Regression Results:")
    print(model_memory2.summary())

# List of groups to analyze (lowercased)
groups = ['schema', 'short-p', 'long']

for group in groups:
    run_regression_for_group(group)

# Function to run single-predictor regression for each time point
def run_single_predictor_regression_for_group(group_name):
    # Filter the data for the specified group
    group_data = combined_df[combined_df['Group'].str.strip().str.lower() == group_name.lower()]

    # List of time points for pupil dilation
    time_points = [-2, -1, 0, 1, 2]

    # Looping through each time point and run a regression with only that time point as the predictor
    for time_point in time_points:
        # Define the predictor (X) and add constant
        X = group_data[[time_point]]
        X = sm.add_constant(X)  # Add constant term for intercept

        # Memory1 (Remember) as outcome variable
        y_memory1 = group_data['memory1（remember）']
        model_memory1 = sm.OLS(y_memory1, X).fit()

        # Memory2 (Detail) as outcome variable
        y_memory2 = group_data['memory2（detail）']
        model_memory2 = sm.OLS(y_memory2, X).fit()

        print(f"\n--- Single-Predictor Regression Results for {group_name} Group ---")
        print(f"Using Pupil Diameter at Time Point {time_point} as Predictor\n")

        print("Memory1 (Remember) Regression Results:")
        print(model_memory1.summary())

        print("\nMemory2 (Detail) Regression Results:")
        print(model_memory2.summary())
        print("\n" + "="*80 + "\n")

# List of groups to analyze
groups = ['Schema', 'short-P', 'Long']

# Run the single-predictor analysis for each group
for group in groups:
    run_single_predictor_regression_for_group(group)

# Function to run single-predictor regression for the short-P group
def run_single_predictor_regression_short_P():
    # Filter the data for the "short-P" group
    group_data = combined_df[combined_df['Group'].str.strip().str.lower() == 'short-p']

    # List of time points for pupil dilation
    time_points = [-2, -1, 0, 1, 2]

    # Looping through each time point and run a regression with only that time point as the predictor
    for time_point in time_points:
        X = group_data[[time_point]]
        X = sm.add_constant(X)  # Add constant term for intercept

        # Memory1 (Remember) as outcome variable
        y_memory1 = group_data['memory1（remember）']
        model_memory1 = sm.OLS(y_memory1, X).fit()

        # Memory2 (Detail) as outcome variable
        y_memory2 = group_data['memory2（detail）']
        model_memory2 = sm.OLS(y_memory2, X).fit()

        print(f"\n--- Single-Predictor Regression Results for Short-P Group ---")
        print(f"Using Pupil Diameter at Time Point {time_point} as Predictor\n")

        print("Memory1 (Remember) Regression Results:")
        print(model_memory1.summary())

        print("\nMemory2 (Detail) Regression Results:")
        print(model_memory2.summary())
        print("\n" + "="*80 + "\n")

#single-predictor analysis for the short-P group
run_single_predictor_regression_short_P()

#single-predictor regression for the short-R group
def run_single_predictor_regression_short_R():
    group_data = combined_df[combined_df['Group'].str.strip().str.lower() == 'short-r']
    time_points = [-2, -1, 0, 1, 2]


    for time_point in time_points:
        X = group_data[[time_point]]
        X = sm.add_constant(X)  # Add constant term for intercept

        # Memory1 (Remember) as outcome variable
        y_memory1 = group_data['memory1（remember）']
        model_memory1 = sm.OLS(y_memory1, X).fit()

        # Memory2 (Detail) as outcome variable
        y_memory2 = group_data['memory2（detail）']
        model_memory2 = sm.OLS(y_memory2, X).fit()


        print(f"\n--- Single-Predictor Regression Results for Short-R Group ---")
        print(f"Using Pupil Diameter at Time Point {time_point} as Predictor\n")

        print("Memory1 (Remember) Regression Results:")
        print(model_memory1.summary())

        print("\nMemory2 (Detail) Regression Results:")
        print(model_memory2.summary())
        print("\n" + "="*80 + "\n")

run_single_predictor_regression_short_R()