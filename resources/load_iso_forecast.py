import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from schemas.load_iso_forecast import LoadISOForecastQuery, LoadISOForecastValidation
from scrape.load_iso_forecast import scrape_load_iso_forecast
from models.load_iso_forecast import LoadISOForecastModel
from utils.find_missing_dates import find_missing_dates

class LoadISOForecast(Resource):

    def get(Self):
        query_params = request.args.to_dict()
        try:
            validated = LoadISOForecastQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Check if the date range is in the database
        missingDates = find_missing_dates(start, end, LoadISOForecastModel)

        # Scrape missing data
        if missingDates:
            scrape_load_iso_forecast(missingDates)

        # Retrieve all data in between start and end from database
        query = db.session.query(LoadISOForecastModel).filter(LoadISOForecastModel.timestamp.between(start, end))

        if validated.get('name'):
            query = query.filter(LoadISOForecastModel.name.in_(validated['name']))

        results = query.all()
    
        # Serialize data
        json_data = LoadISOForecastValidation(many=True).dump(results)

        return jsonify(json_data)
