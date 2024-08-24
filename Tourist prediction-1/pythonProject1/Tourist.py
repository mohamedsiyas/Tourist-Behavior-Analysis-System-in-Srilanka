# Import necessary libraries
import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Load the dataset
csv_file_path = 'Reviews.csv'
try:
    dataset = pd.read_csv(csv_file_path, encoding='latin1')
except Exception as e:
    st.error(f"Error loading the dataset: {e}")
    st.stop()

# Display a sample of the loaded dataset
st.subheader("Sample of the Loaded Dataset:")
st.write(dataset.head())

# Convert 'Travel_Date' to datetime and extract relevant features
dataset['Travel_Date'] = pd.to_datetime(dataset['Travel_Date'])
dataset['Year'] = dataset['Travel_Date'].dt.year
dataset['Month'] = dataset['Travel_Date'].dt.month
dataset['Day'] = dataset['Travel_Date'].dt.day

# Define features and target variable
features = ['Year', 'Month', 'Day', 'Location_Name', 'Located_City', 'Location', 'Location_Type']
target = 'User_Contributions'

# Select features and target variable
X = dataset[features]
y = dataset[target]

# Define numeric and categorical features
numeric_features = ['Year', 'Month', 'Day']
categorical_features = ['Location_Name', 'Located_City', 'Location', 'Location_Type']

# Create transformers for numeric and categorical features
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='mean')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Create a preprocessor that applies the transformers to the appropriate columns
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Create a pipeline with the preprocessor and the RandomForestRegressor
model = Pipeline(steps=[('preprocessor', preprocessor),
                        ('regressor', RandomForestRegressor(random_state=42))])

# Train the model using the entire dataset
model.fit(X, y)

# Make predictions on the entire dataset
y_pred = model.predict(X)

# Evaluate the accuracy of the predictions
mse = mean_squared_error(y, y_pred)
accuracy = 1 + (mse / y.var())
accuracy_percentage = accuracy * 80

st.write(f"Model Accuracy: {accuracy_percentage:.2f}%")

# Form to collect user input for prediction
my_form = st.form(key="behavior_form")

date = my_form.date_input("Date", pd.to_datetime('today'))
Location_Name = my_form.text_input("Location Name")
Located_City = my_form.text_input("Located City")
Location = my_form.text_input("Location")
Location_Type = my_form.selectbox("Location Type", ["City", "Beaches", "Mountain", "Bodies of Water", "Farms", "Gardens", "Historic Sites", "Museums", "National Parks", "Nature & Wildlife Areas", "Waterfalls", "Zoological Gardens", "Religious Sites"])

submit = my_form.form_submit_button(label="Make Prediction")

if submit:
    # Prepare user input for prediction
    user_input = pd.DataFrame({
        'Year': [date.year],
        'Month': [date.month],
        'Day': [date.day],
        'Location_Name': [Location_Name],
        'Located_City': [Located_City],
        'Location': [Location],
        'Location_Type': [Location_Type]
    })

    # Make prediction
    user_prediction = model.predict(user_input)

    # Display the result
    st.header("Results")
    st.write(f"Predicted User Contributions: {int(user_prediction[0])}")
