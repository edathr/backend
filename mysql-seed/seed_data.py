# Define constants
import pandas as pd
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from mysql.connector import errorcode

KINDLE_REVIEW_SEED_FILE = "/app/mysql-seed/kindle_reviews_seed.csv"
HOST = "mysqldb"
USERNAME = "root"
PASSWORD = "root"
DATABASE = "50043db"
table_name = "historical_reviews"


def parse_dt(timestamp: int):
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


def parse_helpful(vector: str):
    p1, p2 = vector[1], vector[-2]

    return int(p1), int(p2)

i = 0

print("Seeding Data... ")
df = pd.read_csv(KINDLE_REVIEW_SEED_FILE)

for row in df.itertuples():
    i += 1
    if i == 1200:
        break

    review_id = row.id
    asin = row.asin
    helpful, total_helpful_rating = parse_helpful(row.helpful)
    review_rating = row.overall
    review_text = row.reviewText
    summary_text = row.summary
    reviewer_name = row.reviewerName
    reviewer_id = row.reviewerID
    date_time = parse_dt(row.unixReviewTime)
    unix_timestamp = row.unixReviewTime

    connection = mysql.connector.connect(host=HOST,
                                         database=DATABASE,
                                         user=USERNAME,
                                         password=PASSWORD)

    cursor = connection.cursor()


    try:
        mySql_insert_query = f"""INSERT INTO {table_name} (asin, helpful_rating, total_helpful_rating, review_rating,
        review_text, summary_text, username, reviewer_id, date_time, unix_timestamp) 
                            VALUES (%s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s)"""

        insertion_tuple = (asin, helpful, total_helpful_rating, review_rating,
                           review_text, summary_text, reviewer_name, reviewer_id, str(date_time), unix_timestamp)
        cursor.execute(mySql_insert_query, insertion_tuple)
        connection.commit()
        # print("Record inserted successfully into  table")


    except Exception as e:
        print("FAILED QUERY ", str(e))
        continue

print("Completed Seeding Data!")
