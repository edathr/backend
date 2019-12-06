### This folder contain scripts that will not be invoked at runtime

1. Scripts are contained in this repository so that I may import models conveniently.
2. To reduce build time when deploying or doing a docker compose, this will be inside my `.gitignore`


#### Aggregate num_ratings and total_rating 
- Write a script to parse historical_reviews using SqlAlchemy models 
- Save it into a csv file so that I may keep reusing it 
- In the future, when reviews are added, I will just do an increment on MongoDB


