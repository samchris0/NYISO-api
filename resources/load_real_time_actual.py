import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from schemas.load_real_time_actual import LoadRealTimeActualQuery, LoadRealTimeActualValidation
from scrape.load_real_time_actual import scrape_load_real_time_actual
from models.load_real_time_actual import LoadRealTimeActualModel
from utils.find_missing_dates import find_missing_dates

class LoadRealTimeActual(Resource):

    def get(Self):
        query_params = request.args.to_dict()
        try:
            validated = LoadRealTimeActualQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Check if the date range is in the database
        missingDates = find_missing_dates(start, end, LoadRealTimeActualModel)

        # Scrape missing data
        if missingDates:
            scrape_load_real_time_actual(missingDates)

        # Retrieve all data in between start and end from database
        query = db.session.query(LoadRealTimeActualModel).filter(LoadRealTimeActualModel.timestamp.between(start, end))

        if validated.get('name'):
            query = query.filter(LoadRealTimeActualModel.name.in_(validated['name']))

        results = query.all()
    
        # Serialize data
        json_data = LoadRealTimeActualValidation(many=True).dump(results)

        return jsonify(json_data)
