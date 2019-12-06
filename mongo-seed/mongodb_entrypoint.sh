#!/usr/bin/env bash
echo "INSERTING DATA INTO MONGO DATABASE NOW"
#mongoimport --db=$DATABASE --collection=$COLLECTION --file=$FILEPATH --drop
mongoimport --host=mongodb --db=50043db --collection=kindle_metadata2 --file=./processed_metadata.json --drop
echo "Done inserting data in to mongodb"