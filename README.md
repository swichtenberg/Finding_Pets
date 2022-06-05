# Hot Dogs and Cold Dogs

## Background
The purpose of the project was to predict how long dogs around the United States are available for adoption before finding a forever home. The project evaluates a dataset of already adopted dogs (2018-2022) with a machine learning model and applies the model to dogs currently available for adoption. The topic was selected to help bring awareness to 'less desirable' dogs who are available for adoption and help them find homes more quickly. The availability of large amounts of adoption data also contributed to the selection of the topic.

### Data Sources
The primary source of data used in the analysis was Petfinder. Petfinder is the largest online pet adoption website serving North America. According to Petfinder.com, users can browse pets from their network of over 11,500 shelters. Petfinder provides a free Application Programming Interface (API) to access the Petfinder database which contains information about hundreds of thousands of pets currently available for adoption and those already adopted. In addition to the Petfinder API, population data for all municipalities in the United States was gathered from the United States Census Bureau (census.gov).

### Questions and Initial Investigation
The project aims to identify which features have the greatest impact on the duration a dog remains available for adoption and to predict how long currently available dogs will need a temporary home. Exploration of Petfinder data revealed the availability of greater than 50 features for each pet currently available for adoption or already adopted. These features included, but were not limited to, species, breed, age, color, temprement, health status, location, dates, and images. These features provided more than enough opportunity to identify those that contribute to adoption status; however, the human population of each dog location was also believed to be an important feature.

### Technology
Python was used to import and clean the data. Microsof Excel was also used to clean and export a limited amount of data. Python and the scikit-learn library were also used to analyze the data with a Random Forest Classifier model. PostgreSQL was used to store the data and Flask and Tableau were used to visualize the data.

## Analysis

### Data Collection
The Petfinder API allows users to call 'animals' to return a list of animal based on query parameters (e.g., type, breed, size, gender, age, color, status). Petfinder limits the number of results per query and the number of queriess per day per user. As a result, a total of twelve queries were used to obtain pet adoption information for each state in the midwest (below). The queries gather pet adoptions from January 1, 2018 to May 1, 2022.

![api_call](https://user-images.githubusercontent.com/96216947/170718619-2dedfb5a-ecc0-4236-b432-4da7c35c676c.PNG)

A csv file was also obtained from the United Status Census Bureau and quickly cleaned in Microsoft Excel.

### Database
The data collected from the Petfinder API totaled greater than 150,000 lines. Given the length of time necessary to collect the data, the raw data was exported to PostgreSQL for future use. The script used for export from Jupyter Notebook is below. The spreadsheet containing populations was directly uploaded to PostgreSQL.

![data_export](https://user-images.githubusercontent.com/96216947/170719519-53ec2fb3-f827-4900-822b-fb2be93b58e6.PNG)

### Data Cleaning
The list of adopted dogs contained an assortment of data (e.g., integers, booleans, strings, dictionaries). The initial cleaning of the data included renaming the columns and combining the city and state into a single column prior to exporting back into PostgreSQL. Once uploaded to the database, select columns from the dog adoptions table were joined with the populations table. The resulting table included the following columns: age, gender, size, status_changed_at (datetime), published_at (datetime), breeds_primary, breeds_mixed, breeds_unknown, spayed_neutered, house_trained, special_needs, shots_current, location, population. All of these features were believed to be important to an owner selecting a dog for adoption. The table was then imported back into Jupyter Notebook for additional cleaning and encoding. Cleaning tasks included encoding boolean values, gender, size (e.g. large, small), and age (e.g., baby, adult). Initially, the breeds column was encoded to include 15 breeds and an 'other' group, but initial analysis revealed the breed is not a significant feature. Instead, a column was added to identify whether the dog was part or full pitbull. The status_changed_at column was subtracted from the published_at column to determine the length of time the dog was available for adoption and the values were bucketed into 'greater than one week' and 'less than one week'. More buckets were created initially; however, the model was found to be quite inaccurate. In addition, the population column was bucketed.

### Machine Learning
The cleaned and encoded data was split to X and y features with duration (i.e., less than one week (0), greater than one week (1)) as the y feature using train_test_split. The train_test_split was completed on 150,700 rows of data. The encoded and split data was then passed through a Random Forest Classifier (n_estimators=128). Results from the training and testing of the model are displayed below. The model achieved an accuracy of 68% although the f1 score of the two classifications differed greatly. The f1 score of the 0 classification (i.e., adopted in less thane one week) was relatively high at 0.80, but the f1 score of the 1 classification (i.e., greater than one week) was relatively low at 0.27. These results suggest the model had a difficult time predicting which dogs were adopted in more than one week. The model was also saved using pickle.dump.

![confusion_matrix](https://user-images.githubusercontent.com/96216947/170724888-2c6d7a2f-cf1d-44f6-a532-1c4ef02e0901.PNG)

A benefit of the Random Forest model is that the results are easy to interpret and the modeling took only a few minutes. On the other hand, the dataset included images of each dog which could have been processed using another machine learning model such as a neural network.

Prior to finalizing the Random Forest Classifier model, a neural network model was used with with little success. The original project aimed to predict the duration of dog availability to the day but this proved difficult and inaccurate. The project was them simplified to a classification problem and aimed to predict whether a dog would be available for greater than one week or less than one week. With this change it seemed more appropriate to use a Random Forest Classifier model.

## Results

### Implementation and Visualization
The final piece of the project was to use the model to predict how long pets currently available for adoption will find a forever home. After importing the model, users are prompted to enter the characteristics they desire in a dog along with their state. These responses prompt and API call which returns a list of currently available dog which meet the criteria. The resulting dataframe is then cleaned and encoded in the same was as the static data and passed through the model to make predictions. The predictions are then merged with the original dataframe that was returned from the query and coordinates for each dog's location is calculated. The most desireable and least desireable dogs are identified and a map of their locations and key features are displayed for the user. I do not plan to create a dashboard, per se, but a map will be displayed with locations of dogs available for adoption. If additional visual elements are required, I will use Tableau to summarize the static data from which the model was created.

### Future Analysis
The project prested above focused on the adoption of dogs. Future projects may included completing similar analysese for different species species (e.g., cats, birds, reptiles). In addition, data retrieved from PetFinder included adoptions since 2018. With adoptions drastically increasing during the COVID-19 pandemic, it is likely many external factors not included in the analysis influenced that data. A more detailed future analysis may include data from all adoptions nationwide over the past one year to minimize some of the effects of time and behavioral and/or societal changes. Looking back, I would have completed this analysis rather than only adoptions in the midwest; however, limitations of the PetFinder API would have made this challenging. In addition, I would have liked to have invested additional time to try and create a model that was able to predict the duration of adoption at a finer scale rather than greater than one week or less than one week.

## Presentation
https://docs.google.com/presentation/d/1vGYFK7Ut38aAgXL294WOICA2HJpwQkASm87Oc57s_Qs/edit?usp=sharing

## Tableau Dashboard
https://public.tableau.com/views/BootcampPetfinderProject/AdoptionsDashboard?:language=en-US&:display_count=n&:origin=viz_share_link
