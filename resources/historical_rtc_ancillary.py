import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from schemas.historical_rtc_ancillary import HistoricalRTCAncillaryQuery, HistoricalRTCAncillaryValidation
from scrape.historical_rtc_ancillary import scrape_historical_rtc_ancillary
from models.historical_rtc_ancillary import HistoricalRTCAncillaryModel
from utils.find_missing_dates import find_missing_dates


"""
Variables returned:
timestamp
name	
ptid	
10 Min Spinning Reserve ($/MWHr): Spinning Reserve – Power suppliers that are synchronized to the NYS power system	
10 Min Non-Synchronous Reserve ($/MWHr): Non-Synchronized Reserve – Power thatcan be started and synchronized to the NYS Power System
30 Min Operating Reserve ($/MWHr): Can be started, synchronized, and change output level or reduce demand within 30 minutes	
NYCA Regulation Capacity ($/MWHr): 
"""

logger = logging.getLogger(__name__)

class HistoricalRTCAncillary(Resource):

    def get(Self):
        query_params = request.args.to_dict()

        try:
            validated = HistoricalRTCAncillaryQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Check if the date range is in the database
        missingDates = find_missing_dates(start, end, HistoricalRTCAncillaryModel)

        # Scrape missing data
        if missingDates:
            scrape_historical_rtc_ancillary(missingDates)

        # Retrieve all data in between start and end from database
        results = (
                    db.session.query(HistoricalRTCAncillaryModel)
                    .filter(HistoricalRTCAncillaryModel.timestamp.between(start, end))
                    .all()
                )
        
        logger.info(results)

        # Serialize data
        json_data = HistoricalRTCAncillaryValidation(many=True).dump(results)

        return jsonify(json_data)