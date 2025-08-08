import logging
import datetime
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from schemas.historical_rtc_zonal import HistoricalRTCZonalQuery, HistoricalRTCZonalValidation
from scrape.historical_rtc_zonal import scrape_historical_rtc_zonal
from models.historical_rtc_zonal import HistoricalRTCZonalModel
from utils.find_missing_dates import find_missing_dates

logger = logging.getLogger(__name__)

class HistoricalRTCZonal(Resource):
    
    def get(Self):
        query_params = request.args.to_dict()
        try:
            validated = HistoricalRTCZonalQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Check if the date range is in the database
        missingDates = find_missing_dates(start, end, HistoricalRTCZonalModel)

        # Scrape missing data
        if missingDates:
            scrape_historical_rtc_zonal(missingDates)
        
        # Retrieve all data in between start and end from database
        query = db.session.query(HistoricalRTCZonalModel).filter(HistoricalRTCZonalModel.timestamp.between(start, end))

        if validated.get('ptid'):
            query = query.filter(HistoricalRTCZonalModel.ptid.in_(validated['ptid']))

        results = query.all()
    
        # Serialize data
        json_data = HistoricalRTCZonalValidation(many=True).dump(results)
        
        return jsonify(json_data)
        