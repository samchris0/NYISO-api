import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from schemas.load_real_time_integrated import LoadRealTimeIntegratedQuery, LoadRealTimeIntegratedValidation
from scrape.load_real_time_integrated import scrape_load_real_time_integrated
from models.load_real_time_integrated import LoadRealTimeIntegratedModel
from utils.find_missing_dates import find_missing_dates

class LoadRealTimeIntegrated(Resource):

    def get(Self):
        query_params = request.args.to_dict()
        try:
            validated = LoadRealTimeIntegratedQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Check if the date range is in the database
        missingDates = find_missing_dates(start, end, LoadRealTimeIntegratedModel)

        # Scrape missing data
        if missingDates:
            scrape_load_real_time_integrated(missingDates)

        # Retrieve all data in between start and end from database
        query = db.session.query(LoadRealTimeIntegratedModel).filter(LoadRealTimeIntegratedModel.timestamp.between(start, end))

        if validated.get('name'):
            query = query.filter(LoadRealTimeIntegratedModel.name.in_(validated['name']))

        results = query.all()
    
        # Serialize data
        json_data = LoadRealTimeIntegratedValidation(many=True).dump(results)

        return jsonify(json_data)
