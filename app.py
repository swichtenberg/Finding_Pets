# Import dependencies
import pandas as pd
import numpy as np
import pickle
from sqlalchemy import create_engine
from config import my_password
from sklearn.preprocessing import StandardScaler
import petpy as pt
import geopy as gp
import gmaps
from config import petfinder_api_key
from config import petfinder_secret
from config import gkey
from geopy.geocoders import Nominatim
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index(): 
    featureList = pd.read_csv("features.csv").to_dict("records")


    prediction = '' 
    if request.method == "POST":

        values = []
        for f in featureList: 
            name = f["Name"]
            f["Value"] = str(request.form[name])
            values.append(f["Value"])
        
        # Prompt the user for dog input
        age = values[0]
        gender = values[1]
        location = values[2]

        # Initiate petpy
        pf = pt.Petfinder(key=petfinder_api_key, secret=petfinder_secret)


        # Make API call to obtain DataFrame of adoptable dogs in Wisconsin
        adoptable_dogs = pf.animals(animal_type='dog', status='adoptable', age=age, gender=gender, location=location, results_per_page=100, pages=300, return_df=True)


        # Rename columns
        adoptable_dogs = adoptable_dogs.rename(columns={"breeds.primary":"breeds_primary", "breeds.secondary":"breeds_secondary", "breeds.mixed":"breeds_mixed", "breeds.unknown":"breeds_unknown", "colors.primary":"colors_primary", "colors.secondary":"colors_secondary", "colors.tertiary":"colors_tertiary", "attributes.spayed_neutered":"spayed_neutered", "attributes.house_trained":"house_trained", "attributes.declawed":"declawed", "attributes.special_needs":"special_needs", "attributes.shots_current":"shots_current", "environment.children":"environment_children", "environment.dogs":"environment_dogs", "environment.cats":"environment_cats",
                                                        "primary_photo_cropped.small":"photo_small", "primary_photo_cropped.medium":"photo_medium", "primary_photo_cropped.large":"photo_large", "primary_photo_cropped.full":"photo_full", "contact.email":"email", "contact.phone":"phone", "contact.address.address1": "address_1", "contact.address.address2":"address_2", "contact.address.city":"city", "contact.address.state":"state", "contact.address.postcode":"postcode", "contact.address.country":"country"})


        testing_dogs=adoptable_dogs[['id', 'age', 'gender', 'size', 'breeds_primary', 'breeds_mixed', 'breeds_unknown', 'spayed_neutered', 'house_trained', 
                                    'special_needs', 'shots_current', 'city', 'state']]


        # Create location column with City, State
        testing_dogs['location'] = testing_dogs['city'] + ', ' + testing_dogs['state']
        testing_dogs = testing_dogs.drop(['city', 'state'], axis=1)


        # Read dog adoptions DataFrame from PostgreSQL
        db_string = f"postgresql://postgres:{my_password}@127.0.0.1:5432/PetFindingDB"
        engine = create_engine(db_string)
        populations_df = pd.read_sql("select * from \"populations\"", con=engine)

        testing_dogs=testing_dogs.merge(populations_df, left_on='location', right_on='city')
        testing_dogs = testing_dogs.drop(['city', 'location'], axis=1)


        # Drop any rows with NaN values and confirm they have been dropped
        testing_dogs=testing_dogs.dropna(how='any')

        # Make copy of adoptions_df and encode boolean values
        encoded_df = testing_dogs.copy()
        testing_dogs[['breeds_mixed', 'breeds_unknown', 'spayed_neutered','house_trained', 'special_needs', 'shots_current']] = encoded_df[['breeds_mixed', 'breeds_unknown', 'spayed_neutered','house_trained', 'special_needs', 'shots_current']].astype(int)
        encoded_df.head()

        # Make copy of adoptions_df and encode boolean values
        encoded_df = testing_dogs.copy()
        testing_dogs[['breeds_mixed', 'breeds_unknown', 'spayed_neutered','house_trained', 'special_needs', 'shots_current']] = encoded_df[['breeds_mixed', 'breeds_unknown', 'spayed_neutered','house_trained', 'special_needs', 'shots_current']].astype(int)

        # Encode gender column
        encoded_df['gender'] = encoded_df['gender'].replace(['Female', 'Male'], [0,1])

        # Encode age and size columns
        encoded_df = pd.get_dummies(encoded_df, columns=['age', 'size'])

        encoded_df['breed_pitbull'] = np.where(encoded_df['breeds_primary'] == 'Pit Bull Terrier', 1, 0)
        encoded_df = encoded_df.drop(columns=["breeds_primary"])


        def bucketPopulation(row):
            if row['population'] > 0 and row['population'] <= 10000:
                return '0 to 10,000'
            elif row['population'] > 10000 and row['population'] <= 50000:
                return '10,000 to 50,000'
            elif row['population'] > 50000 and row['population'] <= 100000:
                return '50,000 to 100,000'
            return 'greater than 100,000'

        encoded_df['bucketed_population'] = encoded_df.apply(lambda row: bucketPopulation(row), axis=1)
        encoded_df.drop('population', axis=1, inplace=True)

        # Encode age and size columns
        encoded_df = pd.get_dummies(encoded_df, columns=['bucketed_population'])

        # Read dog adoptions DataFrame from PostgreSQL
        db_string = f"postgresql://postgres:{my_password}@127.0.0.1:5432/PetFindingDB"
        engine = create_engine(db_string)
        standard_format = pd.read_sql("select * from \"standard_format\"", con=engine)

        # Merge current dogs for adoption with the test data to get the same number of columns for model
        encoded_df = pd.DataFrame.merge(encoded_df, standard_format, how='outer')

        # Drop the test data
        encoded_df = encoded_df[encoded_df['id'].notna()]

        encoded_df = encoded_df.fillna(0)
        encoded_df = encoded_df.drop(['index', 'duration'], axis=1)

        # Creating a StandardScaler instance.
        scaler = StandardScaler()


        # Create features
        X_test = encoded_df.drop(columns='id')
        dog_ids = encoded_df['id']
        X_scaler = scaler.fit(X_test)
        X_test_scaled = X_scaler.transform(X_test)

        #Load model
        loaded_model = pickle.load(open('finalized_model.sav', 'rb'))

        # Making predictions using the testing data.
        predictions = loaded_model.predict(X_test_scaled)
        predictions

        predictions_df = pd.DataFrame.from_dict(dog_ids)
        predictions_df['duration'] = predictions

        predictions_df['duration'].value_counts()

        # Merge current dogs for adoption with the test data to get the same number of columns for model
        viz_df = pd.DataFrame.merge(adoptable_dogs, predictions_df, how='left')

        cold_dogs=viz_df.loc[viz_df['duration'] == 1]
        hot_dogs= viz_df.loc[viz_df['duration'] == 0]

        geolocator = Nominatim(user_agent='http')

        cold_dogs['location'] = viz_df['city'] + ', ' + viz_df['state']
        # cold_dogs = cold_dogs.drop(['city', 'state'], axis=1)
        hot_dogs['location'] = viz_df['city'] + ', ' + viz_df['state']
        # hot_dogs = cold_dogs.drop(['city', 'state'], axis=1)

        cold_dogs[['lat', 'lon']] = cold_dogs['location'].apply(geolocator.geocode).apply(lambda x: pd.Series([x.latitude, x.longitude], index=['lat', 'lon']))
        hot_dogs[['lat', 'lon']] = hot_dogs['location'].apply(geolocator.geocode).apply(lambda x: pd.Series([x.latitude, x.longitude], index=['lat', 'lon']))

        # Configure gmaps to use your Google API key.
        gmaps.configure(api_key=gkey)

        # 9. Using the template add city name, the country code, the weather description and maximum temperature for the city.
        info_box_template = """
        <dl>
        <dt>Name</dt><dd>{name}</dd>
        <dt>Age</dt><dd>{age}</dd>
        <dt>URL</dt><dd>{url}</dd>
        <dt>Location</dt><dd>{location}</dd>
        </dl>
        """

        # 10a. Get the data from each row and add it to the formatting template and store the data in a list.
        cold_dog_info = [info_box_template.format(**row) for index, row in cold_dogs.iterrows()]
        hot_dog_info = [info_box_template.format(**row) for index, row in hot_dogs.iterrows()]

        # 10b. Get the latitude and longitude from each row and store in a new DataFrame.
        cold_locations = cold_dogs[["lat", "lon"]]
        hot_locations = hot_dogs[["lat", "lon"]]

        # 11a. Add a marker layer for each city to the map. 
        cold_fig = gmaps.figure(center=(30.0, 31.0), zoom_level=1.5)
        marker_layer = gmaps.marker_layer(cold_locations, info_box_content=cold_dog_info)
        cold_fig.add_layer(marker_layer)
        embed_minimal_html('templates/cold_export.html', views=[cold_fig])

        # 11a. Add a marker layer for each city to the map. 
        hot_fig = gmaps.figure(center=(30.0, 31.0), zoom_level=1.5)
        marker_layer = gmaps.marker_layer(hot_locations, info_box_content=hot_dog_info)
        hot_fig.add_layer(marker_layer)
        embed_minimal_html('templates/hot_export.html', views=[hot_fig])


    return render_template("index.html", featureList=featureList, prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)
