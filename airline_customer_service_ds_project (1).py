# -*- coding: utf-8 -*-
"""Airline_Customer_Service_DS_project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1EYsG3fUGM0717FvdhXSWSSoiSNn7FuO1

# ** AirlineCustomer Service**

# Predicting Airline Passenger Satisfaction

Using Machine Learning : A Data-Driven Approach to Enhancing Customer Experience

In the competitive airline industry, understanding customer satisfaction is essential for improving service quality and retaining loyal passengers. This project aims to develop a machine learning model that predicts whether a customer is "Satisfied" or "Neutral/Unhappy" based on various factors including demographic details, travel characteristics, and service-related ratings such as booking ease, inflight service, cleanliness, entertainment, and more. By identifying the key drivers of satisfaction, airlines can take proactive steps to enhance passenger experiences, optimize operations, and make informed, data-driven decisions to improve overall customer engagement.

Business Goal:
Improve overall customer experience by identifying pain points.

Predict customer satisfaction to proactively address service gaps.

Segment customers based on their likelihood of satisfaction for targeted service improvements.

# IMPORTING LIBRARIES
"""

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
from ast import increment_lineno
# imort lib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay,f1_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix,accuracy_score,classification_report
from joblib import Parallel, delayed

# %matplotlib inline
import pickle

"""# load the data set"""

df=pd.read_csv("/content/drive/MyDrive/Airline Customer Service project/Data.csv",low_memory=False)
df.head()

# info gives details about the data
df.info()

# checking the class imbalance in data.
df['Satisfaction'].value_counts()

df.shape

df['Satisfaction'].unique()

df.isnull().sum()

"""# droping Id"""

df= df.drop(df.iloc[:, [0]], axis=1)

df.nunique()

"""# Analysis of the columns : Statistical Summary of  data"""

df.describe()

df.head()

df['Flight Distance'].dtype

"""# converting str to numerical data type and replacing "$" ,"" to empty str"""

df['Flight Distance'] = pd.to_numeric(df['Flight Distance'].str.replace('$', ''), errors='coerce')

"""# EDA : Exploratory Data Analysis

# For Numeric columns
"""

numeric_cols = df.select_dtypes(include = np.number) ### selects numeric columns


column_names = list(numeric_cols.columns)

col_index = 0

plot_rows = 5
plot_cols = 3

fig, ax = plt.subplots(nrows = plot_rows,ncols=plot_cols,figsize = (20,20))

for row_count in range(plot_rows):
    for col_count in range(plot_cols):
        ax[row_count][col_count].scatter(y = numeric_cols[column_names[col_index]],x=numeric_cols.index)
        ax[row_count][col_count].set_ylabel(column_names[col_index])
        col_index = col_index + 1

"""# For Categorical columns"""

categorical_cols = df.select_dtypes(exclude=np.number) ### select cat_columns
column_names = ["Gender","Customer Type","Type of Travel","Class","Satisfaction"]

col_index = 0

plot_rows = 5
plot_cols = 3
num_subplots = plot_rows * plot_cols

fig, ax = plt.subplots(nrows = plot_rows,ncols=plot_cols,figsize = (20,20))

for row_count in range(plot_rows):
    for col_count in range(plot_cols):
        if col_index >= len(column_names):
            break
        ax[row_count][col_count].scatter(y = categorical_cols[column_names[col_index]],x=categorical_cols.index)
        ax[row_count][col_count].set_ylabel(column_names[col_index])
        col_index = col_index + 1

df.head(5)

df.tail(5)

df['Departure Delay'].value_counts()

df['Departure Delay'].unique()

df['Arrival Delay'].value_counts()

"""#"""

df['Arrival Delay'].isnull().sum()

df.info()

df['Age'].unique()

df.isnull().sum() * 100 /df.shape[0]

"""# Finding Outliers using Boxplot"""

df.boxplot(column=['Flight Distance','Departure Delay','Arrival Delay'])

df['Flight Distance'].unique()

df['Flight Distance'].value_counts()

"""# Flittering outliers"""

cols = ['Flight Distance', 'Departure Delay', 'Arrival Delay']


def copy_df(df):
    return df.copy()
def outliers(df,column):
    Q1 = df[column].quantile(0.05)
    Q3 = df[column].quantile(0.95)
    return df[df[column].between(Q1,Q3,inclusive = 'both')]

df = (df.pipe(copy_df)
              .pipe(outliers,cols[0])
              .pipe(outliers,cols[1])
              .pipe(outliers,cols[2]))

df.boxplot(column=['Flight Distance','Departure Delay','Arrival Delay'])

df['Satisfaction'].value_counts()

df.head(5)

"""# Data cleaning
## missing value treatment
"""

df['Arrival Delay']=df["Arrival Delay"].fillna(df["Arrival Delay"].mean())
df['Flight Distance']=df["Flight Distance"].fillna(df["Flight Distance"].mean())

df.isnull().sum()

df['Satisfaction'].unique()

df['Satisfaction'].replace({'Neutral or Dissatisfied':0,'Satisfied':1},inplace=True)

df.head()

df.describe()

"""# Identifing categorical, numerical, and categorical-but-cardinal variables in a dataframe"""

def all_col_names(dataframe, cat_th=10, car_th=20):
    """
    Identifies categorical, numerical, and categorical-but-cardinal variables in a dataframe.

    Parameters:
        dataframe: DataFrame
            The dataset to analyze.
        cat_th: int, optional (default=10)
            Threshold for treating numeric variables as categorical.
        car_th: int, optional (default=20)
            Threshold for treating categorical variables as cardinal.

    Returns:
        tuple: (cat_cols, num_cols, cat_but_car)
            Lists of categorical, numerical, and cardinal categorical variables.
    """

    cat_cols = [col for col in dataframe.columns if dataframe[col].dtype == "O"]
    num_but_cat = [col for col in dataframe.columns if dataframe[col].nunique() < cat_th and dataframe[col].dtype != "O"]
    cat_but_car = [col for col in dataframe.columns if dataframe[col].nunique() > car_th and dataframe[col].dtype == "O"]

    cat_cols = [col for col in cat_cols + num_but_cat if col not in cat_but_car]
    num_cols = [col for col in dataframe.select_dtypes(exclude="O").columns if col not in num_but_cat]

    print(f"Observations: {dataframe.shape[0]}, Variables: {dataframe.shape[1]}")
    print(f"Categorical: {len(cat_cols)}, Numerical: {len(num_cols)}, Cardinal: {len(cat_but_car)}")

    return cat_cols, num_cols, cat_but_car

cat_cols,num_cols,cat_but_car = all_col_names(df)

"""# Feature Engineering"""

df.groupby('Gender').agg({'Satisfaction':['mean','count']})

# Creating a count plot
plt.figure(figsize=(8, 5))
sns.countplot(x="Gender",hue="Satisfaction", data=df, palette="viridis")

# Adding labels
plt.title("Neutral or Dissatisfied vs satisfied ")

# Show plot
plt.show()

df.groupby('Customer Type').agg({'Satisfaction':['mean','count']})

df.groupby('Type of Travel').agg({'Satisfaction':['mean','count']})

df.groupby('Class').agg({'Satisfaction':['mean','count']})

# Generating new variables from gender variable and customer type

df.loc[(df['Gender']== 'Male') & (df['Customer Type'] == 'First-time'), 'new_cus_Gender'] = "Male Loyal"
df.loc[(df['Gender']== 'Female') & (df['Customer Type'] == 'First-time'), 'new_cus_Gender'] = "Female Loyal"

df.loc[(df['Gender']== 'Male') & (df['Customer Type'] == 'Returning'), 'new_cus_Gender'] = "Male Loyal"
df.loc[(df['Gender']== 'Female') & (df['Customer Type'] == 'Returning'), 'new_cus_Gender'] = "Female Loyal"

# Generating new age groups variables
df.loc[(df['Age'] >= 7) & (df['Age'] < 25) , 'New_Age'] = "Young"
df.loc[(df['Age'] >= 25) & (df['Age'] < 40) , 'New_Age'] = "Mature"
df.loc[(df['Age'] >= 40) & (df['Age'] < 65) , 'New_Age'] = "Mid_age"
df.loc[(df['Age'] >= 65) & (df['Age'] < 95) , 'New_Age'] = "Old_age"

df.groupby("New_Age").agg({"Satisfaction": ["mean" , "count"]})

# combining age group with Gender

df.loc[(df['New_Age']== 'young') & (df['Gender'] == 'Male'), 'New_Age_Gender'] = "Young Male"
df.loc[(df['New_Age']== 'young') & (df['Gender'] == 'Female'), 'New_Age_Gender'] = "Young Female"

df.loc[(df['New_Age']== 'Mature') & (df['Gender'] == 'Male'), 'New_Age_Gender'] = "Mature Male"
df.loc[(df['New_Age']== 'Mature') & (df['Gender'] == 'Female'), 'New_Age_Gender'] = "Mature Female"

df.loc[(df['New_Age']== 'Mid_age') & (df['Gender'] == 'Male'), 'New_Age_Gender'] = "Mid_age Male"
df.loc[(df['New_Age']== 'Mid_age') & (df['Gender'] == 'Female'), 'New_Age_Gender'] = "Mid_age Female"

df.loc[(df['New_Age']== 'Old_age') & (df['Gender'] == 'Male'), 'New_Age_Gender'] = "Old_age Male"
df.loc[(df['New_Age']== 'Old_age') & (df['Gender'] == 'Female'), 'New_Age_Gender'] = "Old_age Female"

df.groupby("New_Age_Gender").agg({"Satisfaction": ["mean" , "count"]})

# Generating new variables from type of travel and customer type variables

df.loc[(df['Type of Travel'] == 'Business') & (df['Customer Type'] == 'First-time'),"New_Travel_Type"] ="Business Frist Time"
df.loc[(df['Type of Travel'] == 'Personal') & (df['Customer Type'] == 'First-time'),"New_Travel_Type"] ="Personal First-time"


df.loc[(df['Type of Travel'] == 'Business') & (df['Customer Type'] == 'Returning'),"New_Travel_Type"] ="Business Returning"
df.loc[(df['Type of Travel'] == 'Personal') & (df['Customer Type'] == 'Returning'),"New_Travel_Type"] ="Personal Returning"

df.groupby("New_Travel_Type").agg({"Satisfaction": ["mean" , "count"]})

# Creating a count plot
plt.figure(figsize=(8, 5))
sns.countplot(x="New_Travel_Type",hue="Satisfaction", data=df, palette="viridis")

# Adding labels
plt.title("Neutral or Dissatisfied vs satisfied ")

# Show plot
plt.show()

# Generating a new variable with New_Travel_Type based on gender breakdown
df.loc[(df["New_Travel_Type"] == "Business Frist Time") & (df["Gender"] == "Male"),"New_Travel_Gender"] = "Business Frist Time Male"
df.loc[(df["New_Travel_Type"] == "Business Frist Time") & (df["Gender"] == "Female"),"New_Travel_Gender"] = "Business Frist Time Female"

df.loc[(df["New_Travel_Type"] == "Personal First-time") & (df["Gender"] == "Male"),"New_Travel_Gender"] = "Personal First-time Male"
df.loc[(df["New_Travel_Type"] == "Personal First-time") & (df["Gender"] == "Female"),"New_Travel_Gender"] = "Personal First-time Female"

df.loc[(df["New_Travel_Type"] == "Business Returning") & (df["Gender"] == "Male"),"New_Travel_Gender"] = "Business Returning Male"
df.loc[(df["New_Travel_Type"] == "Business Returning") & (df["Gender"] == "Female"),"New_Travel_Gender"] = "Business Returning Female"

df.loc[(df["New_Travel_Type"] == "Personal Returning") & (df["Gender"] == "Male"),"New_Travel_Gender"] = "Personal Returning Male"
df.loc[(df["New_Travel_Type"] == "Personal Returning") & (df["Gender"] == "Female"),"New_Travel_Gender"] = "Personal Returning Female"

df.groupby("New_Travel_Gender").agg({"Satisfaction": ["mean" , "count"]})

# Generating a new variable with New_Travel_Type in class
df.loc[(df["New_Travel_Type"] == "Business Frist Time") & (df["Class"] == "Business"),"New_Travel_Class"] = "Business Frist Time Business"
df.loc[(df["New_Travel_Type"] == "Business Frist Time") & (df["Class"] == "Economy"),"New_Travel_Class"] = "Business Frist Time Economy"
df.loc[(df["New_Travel_Type"] == "Business Frist Time") & (df["Class"] == "Economy Plus"),"New_Travel_Class"] = "Business Frist Time Economy Plus"

df.loc[(df["New_Travel_Type"] == "Personal First-time") & (df["Class"] == "Business"),"New_Travel_Class"] = "Personal Frist Time Business"
df.loc[(df["New_Travel_Type"] == "Personal Frist Time") & (df["Class"] == "Economy"),"New_Travel_Class"] = "Personal Frist Time Economy"
df.loc[(df["New_Travel_Type"] == "Personal Frist Time") & (df["Class"] == "Economy Plus"),"New_Travel_Class"] = "Personal Frist Time Economy Plus"

df.loc[(df["New_Travel_Type"] == "Business Returning") & (df["Class"] == "Business"),"New_Travel_Class"] = "Business Returning Business"
df.loc[(df["New_Travel_Type"] == "Business Returning") & (df["Class"] == "Economy"),"New_Travel_Class"] = "Business Returning Economy"
df.loc[(df["New_Travel_Type"] == "Business Returning") & (df["Class"] == "Economy Plus"),"New_Travel_Class"] = "Business Returning Economy Plus"

df.loc[(df["New_Travel_Type"] == "Personal Returning") & (df["Class"] == "Business"),"New_Travel_Class"] = "Personal Returning Business"
df.loc[(df["New_Travel_Type"] == "Personal Returning") & (df["Class"] == "Economy"),"New_Travel_Class"] = "Personal Returning Economy"
df.loc[(df["New_Travel_Type"] == "Personal Returning") & (df["Class"] == "Economy Plus"),"New_Travel_Class"] = "Personal Returning Economy Plus"

df.groupby("New_Travel_Class").agg({"Satisfaction": ["mean" , "count"]})

# Creating New_delay_gap
df['New_Delay_Gap'] = abs(df['Departure Delay'] - df['Arrival Delay'])
df['New_Delay_Gap'].head()

df.groupby("New_Delay_Gap").agg({"Satisfaction": ["mean" , "count"]})

# Creating a new variable by classifying over the Flight Distance variable

df.loc[(df['Flight Distance'] <= 1500), 'New_Distance'] = 'Short Distance'
df.loc[(df['Flight Distance'] > 1500),'New_Distance'] = 'Long Distance'

df.groupby("New_Distance").agg({"Satisfaction": ["mean" , "count"]})

# Creating a count plot
plt.figure(figsize=(8, 5))
sns.countplot(x="New_Distance",hue="Satisfaction", data=df, palette="viridis")
plt.title("Neutral or Dissatisfied vs satisfied ")

# Show plot
plt.show()

df.head(5)

# creating a new variables for the overall evaluation of inflight satisfaction
df['New_Flight_Situation']= (df["In-flight Wifi Service"] + df["Food and Drink"] + df["Seat Comfort"] + df["In-flight Entertainment"] + df["Leg Room Service"]) / 25

df.groupby("New_Flight_Situation").agg({"Satisfaction": ["mean" , "count"]})

# Creating a count plot
plt.figure(figsize=(8, 5))
sns.countplot(x="New_Flight_Situation",hue="Satisfaction", data=df, palette="viridis")

# Adding labels
plt.xlabel("flight Service")
plt.ylabel("Service gap")
plt.title("Neutral or Dissatisfied vs satisfied ")
plt.xticks(rotation=90)
# Show plot
plt.show()

# Creating a new variable for general evaluation of operational transactions
df["NEW_OPERATIONAL"] = (df["Departure and Arrival Time Convenience"] + df["Cleanliness"] + df["Baggage Handling"] + df["Gate Location"]) / 20

df.groupby("NEW_OPERATIONAL").agg({"Satisfaction": ["mean", "count"]})

# Creating a new variable for the general evaluation of online transactions
df["NEW_ONLINE"] = (df["Ease of Online Booking"] + df["Online Boarding"] + df["Check-in Service"]) / 15

df.groupby("NEW_ONLINE").agg({"Satisfaction": ["mean", "count"]})

#  Evaluation of personnel and creation of new variables
df["New_Behavior"] = (df["On-board Service"] + df["In-flight Service"]) / 10

df.groupby("New_Behavior").agg({"Satisfaction": ["mean", "count"]})

df.head()

cat_cols,num_cols,cat_but_car = all_col_names(df)

"""# Data Encoding"""

from sklearn.preprocessing import LabelEncoder
def label_encoder(dataframe, binary_col):
    le = LabelEncoder()
    dataframe[binary_col] = le.fit_transform(dataframe[binary_col])
    return dataframe

binary_cols = [col for col in df.columns if df[col].dtype == "O" and df[col].nunique() == 2]
binary_cols

for col in binary_cols:
    df = label_encoder(df,col)

non_binary_cols = [col for col in df[cat_cols] if col not in binary_cols]
non_binary_cols

for col in non_binary_cols:
    df = label_encoder(df,col)

df

"""# Data scaling"""

# Standardise for numeric variables
sd = StandardScaler()
df[num_cols] = sd.fit_transform(df[num_cols])

"""
# Build Machine Learning Model"""

x = df.drop(['Satisfaction'],axis = 1)
y = df['Satisfaction']

"""## Split Data into Train And Test data sets"""

#
x_train,x_test,y_train,y_test = train_test_split(x,y,test_size = 0.2 , random_state = 42)

print(x_train.shape,y_train.shape)
print(x_test.shape,y_test.shape)

x_train.head(5)

x_train.tail(5)

x_train.isnull().sum()

"""# logisticRegression"""

lr=LogisticRegression()
lr.fit(x_train,y_train)

tr_pred=lr.predict(x_train)
val_pred=lr.predict(x_test)
ConfusionMatrixDisplay.from_predictions(y_train,tr_pred)
ConfusionMatrixDisplay.from_predictions(y_test,val_pred)

train_f1=f1_score(y_train,tr_pred)
val_f1=f1_score(y_test,val_pred)
print('Train f1 score -{}'.format(train_f1))
print('val f1 score -{}'.format(val_f1))

print('Accuracy Score: ',accuracy_score(y_test,val_pred))

print('Classification report - ',classification_report(y_test,val_pred))

# logisticRegression
lr=LogisticRegression(max_iter=500,random_state=42)
lr.fit(x_train,y_train)

"""# prediction and confusion matrix"""

tr_pred=lr.predict(x_train)
val_pred=lr.predict(x_test)
ConfusionMatrixDisplay.from_predictions(y_train,tr_pred)
ConfusionMatrixDisplay.from_predictions(y_test,val_pred)

"""# F1_SCORE"""

train_f1=f1_score(y_train,tr_pred)
val_f1=f1_score(y_test,val_pred)
print('Train f1 score -{}'.format(train_f1))
print('val f1 score -{}'.format(val_f1))

"""# Accuracy Score"""

print('Accuracy Score: ',accuracy_score(y_test,val_pred))

"""# Classification report"""

print('Classification report - ',classification_report(y_test,val_pred))

"""# feature_importances of logisticRegression"""

feature_importances = lr.coef_[0]

feature_names = lr.feature_names_in_

sorted_idx = np.argsort(np.abs(feature_importances))[::-1]

sorted_importances = [(feature_names[i], feature_importances[i]) for i in sorted_idx]

sorted_importances

lr = LogisticRegression(max_iter=1000, solver="newton-cg", class_weight={0:1.1, 1:3})

lr.fit(x_train, y_train)

"""# Prediction and confusion matrix"""

tr_pred=lr.predict(x_train)
val_pred=lr.predict(x_test)
ConfusionMatrixDisplay.from_predictions(y_train,tr_pred)
ConfusionMatrixDisplay.from_predictions(y_test,val_pred)

"""# F1_SCORE"""

train_f1=f1_score(y_train,tr_pred)
val_f1=f1_score(y_test,val_pred)
print('Train f1 score -{}'.format(train_f1))
print('val f1 score -{}'.format(val_f1))

"""# Accuracy Score"""

print('Accuracy Score: ',accuracy_score(y_test,val_pred))

"""
# Classification report"""

print('Classification report - ',classification_report(y_test,val_pred))

"""# KNN MODEL"""

###### K nearest neighbors ######

knn = KNeighborsClassifier(n_neighbors=2, weights="uniform", p=1)

knn.fit(x_train,y_train)

"""# Prediction and Confusion matrix"""

tr_pred=knn.predict(x_train)
val_pred=knn.predict(x_test)
ConfusionMatrixDisplay.from_predictions(y_train,tr_pred)
ConfusionMatrixDisplay.from_predictions(y_test,val_pred)

"""# F1_SCORE"""

train_f1=f1_score(y_train,tr_pred)
val_f1=f1_score(y_test,val_pred)
print('Train f1 score -{}'.format(train_f1))
print('val f1 score -{}'.format(val_f1))

"""# Accuracy Score"""

print('Accuracy Score: ',accuracy_score(y_test,val_pred))

"""# Classification report"""

print('Classification report - ',classification_report(y_test,val_pred))

"""# K nearest neighbors"""

# K nearest neighbors

knn = KNeighborsClassifier()

knn.fit(x_train,y_train)

"""# Prediction and Confusion matrix"""

tr_pred=knn.predict(x_train)
val_pred=knn.predict(x_test)
ConfusionMatrixDisplay.from_predictions(y_train,tr_pred)
ConfusionMatrixDisplay.from_predictions(y_test,val_pred)

"""# F1_SCORE"""

train_f1=f1_score(y_train,tr_pred)
val_f1=f1_score(y_test,val_pred)
print('Train f1 score -{}'.format(train_f1))
print('val f1 score -{}'.format(val_f1))

"""# Accuracy Score"""

print('Accuracy Score: ',accuracy_score(y_test,val_pred))

"""# Classification report"""

print('Classification report - ',classification_report(y_test,val_pred))

"""# Decision Tree with cart(gini)"""

Dt=DecisionTreeClassifier(random_state=1,max_depth=2)
Dt.fit(x_train,y_train)
train_score=Dt.score(x_train,y_train)
test_score=Dt.score(x_test,y_test)

"""# Prediction and Confusion matrix"""

tr_pred=Dt.predict(x_train)
val_pred=Dt.predict(x_test)
ConfusionMatrixDisplay.from_predictions(y_train,tr_pred)
ConfusionMatrixDisplay.from_predictions(y_test,val_pred)

"""# F1_SCORE"""

train_f1=f1_score(y_train,tr_pred)
val_f1=f1_score(y_test,val_pred)
print('Train f1 score -{}'.format(train_f1))
print('val f1 score -{}'.format(val_f1))

"""# Accuracy Score"""

print('Accuracy Score: ',accuracy_score(y_test,val_pred))

"""# Classification report"""

print('Classification report :',classification_report(y_test,val_pred))

"""# feature_importances DecisionTreeClassifier"""

feature_importances = Dt.feature_importances_

feature_names = Dt.feature_names_in_

sorted_idx = np.argsort(Dt.feature_importances_)[::-1]

sorted_importances = [(feature_names[i], feature_importances[i]) for i in sorted_idx]

sorted_importances

"""# Random Forest"""

rf=RandomForestClassifier()
rf.fit(x_train,y_train)

"""# Prediction and Confusion matrix"""

tr_pred=rf.predict(x_train)
val_pred=rf.predict(x_test)
ConfusionMatrixDisplay.from_predictions(y_train,tr_pred)
ConfusionMatrixDisplay.from_predictions(y_test,val_pred)

"""# F1_SCORE"""

train_f1 = f1_score(y_train,tr_pred)
val_f1 = f1_score(y_test,val_pred)

print("train F1 Score - {}".format(train_f1))
print("val F1 Score - {}".format(val_f1))

"""# Accuracy Score"""

print('Accuracy Score: ',accuracy_score(y_test,val_pred))

"""
# Classification report"""

print('Classification report :',classification_report(y_test,val_pred))

"""# Feature_importances **RandomForestClassifier**"""

feature_importances = rf.feature_importances_

feature_names = rf.feature_names_in_

sorted_idx = np.argsort(rf.feature_importances_)[::-1]

sorted_importances = [(feature_names[i], feature_importances[i]) for i in sorted_idx]

sorted_importances

# For rf is a trained RandomForest model
importances = rf.feature_importances_
feature_names = rf.feature_names_in_

# Create a DataFrame and sort by importance
sorted_importances = pd.DataFrame({'Feature': feature_names, 'Importance': importances}).sort_values(by='Importance', ascending=False)

# Plot
plt.figure(figsize=(10,12))
sns.barplot(x='Importance', y='Feature', data=sorted_importances)
plt.xticks(rotation=90)
plt.title("Feature Importance")
plt.show()

rf = RandomForestClassifier(max_depth=8,
                             n_estimators=1000,
                             class_weight={0:5, 1:0.6},
                             min_samples_split=50,
                             min_samples_leaf=7)

rf.fit(x_train, y_train)

"""# Prediction and Confusion matrix"""

tr_pred=rf.predict(x_train)
val_pred=rf.predict(x_test)
ConfusionMatrixDisplay.from_predictions(y_train,tr_pred)
ConfusionMatrixDisplay.from_predictions(y_test,val_pred)

"""# F1-SCORE

"""

train_f1 = f1_score(y_train,tr_pred)
val_f1 = f1_score(y_test,val_pred)

print("train F1 Score - {}".format(train_f1))
print("val F1 Score - {}".format(val_f1))

"""# Accuracy Score"""

print('Accuracy Score: ',accuracy_score(y_test,val_pred))

"""# Classification report"""

print('Classification report :',classification_report(y_test,val_pred))

"""# SVM Model"""

from sklearn.svm import SVC

svm=SVC()
svm.fit(x_train,y_train)

"""# Prediction and ConfusionMatrixDisplay"""

tr_pred = svm.predict(x_train)
val_pred = svm.predict(x_test)
ConfusionMatrixDisplay.from_predictions(y_train,tr_pred)
ConfusionMatrixDisplay.from_predictions(y_test,val_pred)

"""# F1-Score"""

train_f1 = f1_score(y_train,tr_pred)
val_f1 = f1_score(y_test,val_pred)

print("train F1 Score - {}".format(train_f1))
print("val F1 Score - {}".format(val_f1))

"""# Accuracy Score"""

# Accuracy Score
print('Accuracy Score: ',accuracy_score(y_test,val_pred))

"""# Classification report"""

print('Classification report :',classification_report(y_test,val_pred))

svm=SVC(class_weight={0:1.2,1:1},C=0.99,degree=6,random_state=42)
svm.fit(x_train,y_train)

tr_pred = svm.predict(x_train)
val_pred = svm.predict(x_test)
ConfusionMatrixDisplay.from_predictions(y_train,tr_pred)
ConfusionMatrixDisplay.from_predictions(y_test,val_pred)

train_f1 = f1_score(y_train,tr_pred)
val_f1 = f1_score(y_test,val_pred)

print("train F1 Score - {}".format(train_f1))
print("val F1 Score - {}".format(val_f1))

print('Accuracy Score: ',accuracy_score(y_test,val_pred))

print('Classification report :',classification_report(y_test,val_pred))

"""# Model Comparison"""

# Model names and their accuracy scores
models = ['Logistic Regression', 'Decision Tree', 'Random Forest', 'SVM']
accuracy = [0.87, 0.86, 0.96, 0.94]
colors = ['blue', 'green', 'red', 'purple']

# Create bar chart
plt.figure(figsize=(8, 6))
bars = plt.bar(models, accuracy, color=colors)

# Add labels on top of the bars
for bar, acc in zip(bars, accuracy):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f'{acc:.2f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

# Labels and title
plt.xlabel('Machine Learning Models', fontsize=12)
plt.ylabel('Accuracy Score', fontsize=12)
plt.title('Model Comparison - Accuracy', fontsize=14, fontweight='bold')

# Rotate x-axis labels for better visibility
plt.xticks(rotation=360)
plt.show()

"""# HyperParameter Tuning
# GridsearchCV
"""

from sklearn.model_selection import GridSearchCV

rf = RandomForestClassifier(random_state=42)

params_grid = {
     "n_estimators":[150,200],
     "max_depth": [4,None],
     "min_samples_split":[4,5],
     "max_features":["sqrt",7],
     "n_jobs": [-1],
     "class_weight": [{0:5,1:3}, {0:1.2, 1:0.9}, {0:5, 1:1.2}]
 }
grid_search_cv = GridSearchCV(
     estimator=rf,
     param_grid=params_grid,
     scoring='f1',
     cv=5,
     return_train_score=True
 )

grid_search_cv.fit(x_train, y_train)

results_df = pd.DataFrame({
     'Parameters': grid_search_cv.cv_results_['params'],
     'MeanTrainScore': grid_search_cv.cv_results_['mean_train_score'],
     'MeanTestScore': grid_search_cv.cv_results_['mean_test_score']})

results_df

"""# RandomForestClassifier"""

rf = RandomForestClassifier(max_depth=None,
                             n_estimators=200,
                             max_features = 7,
                             class_weight={0:5, 1:1.2},
                             min_samples_split=4)

rf.fit(x_train, y_train)

"""# Prediction and Confusion matrix"""

tr_pred=rf.predict(x_train)
val_pred=rf.predict(x_test)
ConfusionMatrixDisplay.from_predictions(y_train,tr_pred)
ConfusionMatrixDisplay.from_predictions(y_test,val_pred)

"""# F1_score"""

train_f1 = f1_score(y_train,tr_pred)
val_f1 = f1_score(y_test,val_pred)

print("train F1 Score - {}".format(train_f1))
print("val F1 Score - {}".format(val_f1))

"""# Accuracy Score"""

print('Accuracy Score: ',accuracy_score(y_test,val_pred))

"""# Classification report"""

print('Classification report :',classification_report(y_test,val_pred))

"""# Feature_importances RandomForestClassifier"""

feature_importances = rf.feature_importances_

feature_names = rf.feature_names_in_

sorted_idx = np.argsort(rf.feature_importances_)[::-1]

sorted_importances = [(feature_names[i], feature_importances[i]) for i in sorted_idx]

sorted_importances

feature_importances = rf.feature_importances_
feature_names = rf.feature_names_in_

# Convert feature importances to percentage
feature_importances_percent = (feature_importances / np.sum(feature_importances)) * 100

sorted_idx = np.argsort(feature_importances)[::-1]

# Extract sorted feature importance with percentage
sorted_importances = [(feature_names[i], feature_importances_percent[i]) for i in sorted_idx]

# Print the results
for name, importance in sorted_importances:
    print(f"{name}: {importance:.2f}%")

# For rf is a trained RandomForest model
importances = rf.feature_importances_
feature_names = rf.feature_names_in_

# Create a DataFrame and sort by importance
sorted_importances = pd.DataFrame({'Feature': feature_names, 'Importance': importances}).sort_values(by='Importance', ascending=False)

# Plot
plt.figure(figsize=(10,12))
sns.barplot(x='Importance', y='Feature', data=sorted_importances)
plt.xticks(rotation=90)
plt.title("Feature Importance")
plt.show()

"""# Best Model is RandomForestClassifier
      With Accuracy Score:  0.9614417832582405
## best traning and Validation F1_score :
                train F1 Score - 0.9948098570971378
                val F1 Score - 0.9535826434484728


 A precision score of 0.95 for class 0 and 0.98 for class 1 indicates that 95% and 98% of the predicted positive instances for each class were correct, respectively


 A recall score of 0.98 for class 0 and 0.93 for class 1 indicates that 98% and 93% of the actual positive instances for each class were correctly classified, respectively

# feature_importances


 In this case "In-flight Wifi Service" has a highest importance sclore(15.57%)  indicating that it contributes the most to the models predictions,the feature with lower importance score are less influential. for instance ,"new_cus_Gender"/ "Gender" with (0.11%) , suggesting it has minimal impact on the models predictions.

* short Distance passenger have higher returning rate of with New_Distance with
                   mean and count


     Long Distance	  0.644437 /	29885


     Short Distance	 0.341691	/ 75539


  however the passenger in short distance flight are more dissatisfied with the
  flight service compared to long distance.


* Business class passenger are more satisfied with the flight service whereas economy class passenger are highly dissatisfied followed by Economy Plus class passenger. Further, business class passenger are more loyal than other class passengers.


* in-flight wifi service has the most significant impact on satisfaction, closely followed by Online boarding, class and in-flight entertainment. Similarly, demographic factors such as Seat Comfort and Type of Travel,Check-in Service also have significant influence on satisfaction levels. Therefore, airlines should tailor their services to target these specific customer demographics.

Business class passengers have higher satisfaction and loyalty, so the airline should maintain and promote the quality of premium class offerings. This includes ensuring comfortable seats, exclusive amenities, and personalized service.
"""