import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from schemas.day_ahead_ancillary_services import DayAheadAncillaryQuery, DayAheadAncillaryValidation
from scrape.day_ahead_ancillary_services import scrape_day_ahead_ancillary
from models.day_ahead_ancillary_services import DayAheadAncillaryModel
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

class DayAheadAncillary(Resource):

    def get(Self):
        query_params = request.args.to_dict()

        try:
            validated = DayAheadAncillaryQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Check if the date range is in the database
        missingDates = find_missing_dates(start, end, DayAheadAncillaryModel)

        # Scrape missing data
        if missingDates:
            scrape_day_ahead_ancillary(missingDates)

        # Retrieve all data in between start and end from database
        results = (
                    db.session.query(DayAheadAncillaryModel)
                    .filter(DayAheadAncillaryModel.timestamp.between(start, end))
                    .all()
                )
        
        logger.info(results)

        # Serialize data
        json_data = DayAheadAncillaryValidation(many=True).dump(results)

        return jsonify(json_data)