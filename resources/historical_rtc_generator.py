import logging
import datetime
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from schemas.historical_rtc_generator import HistoricalRTCGeneratorQuery, HistoricalRTCGeneratorValidation
from scrape.historical_rtc_generator import scrape_historical_rtc_generator
from models.historical_rtc_generator import HistoricalRTCGeneratorModel
from utils.find_missing_dates import find_missing_dates

logger = logging.getLogger(__name__)

class HistoricalRTCGenerator(Resource):
    
    def get(Self):
        query_params = request.args.to_dict()
        try:
            validated = HistoricalRTCGeneratorQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Check if the date range is in the database
        missingDates = find_missing_dates(start, end, HistoricalRTCGeneratorModel)
        
        # Scrape missing data
        if missingDates:
            scrape_historical_rtc_generator(missingDates)
        
        # Retrieve all data in between start and end from database
        query = db.session.query(HistoricalRTCGeneratorModel).filter(HistoricalRTCGeneratorModel.timestamp.between(start, end))

        if validated.get('ptid'):
            query = query.filter(HistoricalRTCGeneratorModel.ptid.in_(validated['ptid']))

        results = query.all()
    
        # Serialize data
        json_data = HistoricalRTCGeneratorValidation(many=True).dump(results)

        return jsonify(json_data)
        