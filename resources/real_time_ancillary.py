import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from schemas.real_time_ancillary_services import RealTimeAncillaryQuery, RealTimeAncillaryValidation
from scrape.real_time_ancillary_services import scrape_real_time_ancillary
from models.real_time_ancillary_services import RealTimeAncillaryModel
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

class RealTimeAncillary(Resource):

    def get(Self):
        query_params = request.args.to_dict()

        try:
            validated = RealTimeAncillaryQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Check if the date range is in the database
        missingDates = find_missing_dates(start, end, RealTimeAncillaryModel)

        # Scrape missing data
        if missingDates:
            scrape_real_time_ancillary(missingDates)

        # Retrieve all data in between start and end from database
        results = (
                    db.session.query(RealTimeAncillaryModel)
                    .filter(RealTimeAncillaryModel.timestamp.between(start, end))
                    .all()
                )
        
        logger.info(results)

        # Serialize data
        json_data = RealTimeAncillaryValidation(many=True).dump(results)

        return jsonify(json_data)