# Finding_Pets

## Background

The purpose of the project will be to help expediate the adoption of pets. A recurrent neural network will be used to predict the amount of time dogs spend waiting to be adopted based on several characteristics (e.g., age, breed, size, vaccination status). Data will be obtained from PetFinder's API for dogs that have been adopted in the past year. The results of machine learning model will then be used to predict when dogs currently available for adoption will be adopted. The topic was selected because I am a dog lover and believe all pets deserve a loving home. The data is also readily available and extensive. The primary question is 'what factors influence how quickly a dog is adopted'. The analysis will focus on adoptions near my hometown, Eau Claire, WI.

I will be working on this project independently to maximize the learning experience.

## Database

Static data will be stored using PostgreSQL. This data includes a table of all organizations in Wisconsin and a table of all pets adopted. The two tables will be joined in PostgreSQL and then imported into pandas for the machine learning model. The table of organizations will also be joined with a table of unadopted pets to predict when the pets will be adopted and I may also plot their locations on a map.
