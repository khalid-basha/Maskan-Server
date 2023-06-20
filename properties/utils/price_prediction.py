import os

import pandas as pd
import numpy as np
import joblib
import sklearn

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_FILES_DIR = os.path.join(BASE_DIR, 'utils')
# load saved models
encoder = joblib.load(os.path.join(MODEL_FILES_DIR, 'encoder.sav'))
ohe = joblib.load(os.path.join(MODEL_FILES_DIR, 'ohe.sav'))
scaler = joblib.load(os.path.join(MODEL_FILES_DIR, 'scaler.sav'))
regressor = joblib.load(os.path.join(MODEL_FILES_DIR, 'regressor.sav'))

# def predict_property_price(record):
#     # convert record dict to df
#     house_record = pd.DataFrame().append(record, ignore_index=True)
#
#     # encoding type column
#     house_record['type'] = encoder.transform(house_record['type'])
#
#     # ohe-ing city column
#     encoded_cities = ohe.transform(house_record[['city']]).toarray()
#     encoded_cities_df = pd.DataFrame(encoded_cities, columns=list(ohe.categories_[0]))
#
#     house_record = pd.concat([house_record, encoded_cities_df], axis=1).drop(columns=['city'])
#
#     # scaling area column
#     house_record[['area']] = scaler.transform(house_record[['area']])
#
#     # predict price in log scale
#     house_record = poly_features.transform(house_record)
#     y_predicted = lr_poly.predict(np.array(house_record))
#
#     return {'predicted_price': y_predicted[0]}


def predict_property_price(record):
    # convert record dict to df
    house_record = pd.DataFrame().append(record, ignore_index=True)

    # encoding type column
    house_record['type'] = encoder.transform(house_record['type'])

    # ohe-ing city column
    encoded_cities = ohe.transform(house_record[['city']]).toarray()
    encoded_cities_df = pd.DataFrame(encoded_cities, columns=list(ohe.categories_[0]))

    house_record = pd.concat([house_record, encoded_cities_df], axis=1).drop(columns=['city'])

    # scaling area column
    house_record[['area']] = scaler.transform(house_record[['area']])

    # predict price in log scale
    y_predicted = regressor.predict(house_record)

    return {'predicted_price': y_predicted[0]}
