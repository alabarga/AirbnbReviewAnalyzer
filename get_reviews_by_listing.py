import requests
import json
import io
import pymongo 
from contextlib import suppress

DEBUG = False
SAMPLE = 7762953 # Chris: 7762953, Gilda: 2056659
CLIENT = pymongo.MongoClient('localhost', 27017)

def get_reviews(listing_id, offset = 0):
    # Review
    # GET https://api.airbnb.com/v2/reviews

    try:
        response = requests.get(
            url="https://api.airbnb.com/v2/reviews",
            params={
                "client_id": "3092nxybyb0otqw18e8nh5nty",
                "locale": "en-US",
                "currency": "USD",
                "_format": "for_mobile_client",
                "_limit": "50",
                "_offset": str(offset),
                "_order": "language",
                "listing_id": str(listing_id), 
                "role": "all",
            },
        )

        if DEBUG:
            print('Response HTTP Status Code: {status_code}'.format(
                status_code=response.status_code))
            print('Response HTTP Response Body: {content}'.format(
                 content=response.content))

        return response.json()

    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def get_all_reviews(listing_id):
    resp = get_reviews(listing_id)
    reviews_count = resp['metadata']['reviews_count']
    reviews = resp['reviews']
    for offset in range(50, reviews_count, 50):
        new_resp = get_reviews(listing_id, offset)
        reviews.extend(new_resp['reviews'])
    def syncID(review):
        id_num = review['id']
        del review['id']
        review['_id'] = id_num
        return review
    reviews = list(map(syncID,reviews))
    return reviews

def insert_reviews(listing_id):
    data = get_all_reviews(listing_id)
    db = CLIENT.ara
    collection = db.reviews
    with suppress(Exception):
        collection.insert_many(data, ordered=False)
    if DEBUG:
        with open('data.json', 'w') as f:
           json.dump(data, f, indent = 4, separators = (',', ':'))

def main():
    insert_reviews(SAMPLE)

if __name__ == '__main__':
    main()