import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from schemas.day_ahead_lbmp_generator import DayAheadLBMPGeneratorQuery, DayAheadLBMPGeneratorValidation
from scrape.day_ahead_lbmp_generator import scrape_day_ahead_lbmp_generator 
from models.day_ahead_lbmp_generator import DayAheadLBMPGeneratorModel
from utils.find_missing_dates import find_missing_dates

"""
Variables returned:
timestamp 
ptid
name
lbmp: The locational based marginal price for a given time and location
marginal_cost_losses: Extra energy (and cost) required to produce to counteract transmission loss
marginal_cost_congestion: Added cost due to transmission constraints
"""

logger = logging.getLogger(__name__)

class DayAheadLBMPGenerator(Resource):

    def get(Self):
        query_params = request.args.to_dict()
        try:
            validated = DayAheadLBMPGeneratorQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Check if the date range is in the database
        missingDates = find_missing_dates(start, end, DayAheadLBMPGeneratorModel)

        # Scrape missing data
        if missingDates:
            scrape_day_ahead_lbmp_generator(missingDates)

        # Retrieve all data in between start and end from database
        query = db.session.query(DayAheadLBMPGeneratorModel).filter(DayAheadLBMPGeneratorModel.timestamp.between(start, end))

        if validated.get('ptid'):
            query = query.filter(DayAheadLBMPGeneratorModel.ptid.in_(validated['ptid']))
        
        results = query.all()
    
        # Serialize data
        json_data = DayAheadLBMPGeneratorValidation(many=True).dump(results)

        return jsonify(json_data)