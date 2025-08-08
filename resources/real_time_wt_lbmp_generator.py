import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from schemas.real_time_wt_lbmp_generator import RealTimeWT_LBMPGeneratorQuery, RealTimeWT_LBMPGeneratorValidation
from scrape.real_time_wt_lbmp_generator import scrape_real_time_wt_lbmp_generator 
from models.real_time_wt_lbmp_generator import RealTimeWT_LBMPGeneratorModel
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

class RealTimeWeightedLBMPGenerator(Resource):

    def get(Self):
        query_params = request.args.to_dict()
        try:
            validated = RealTimeWT_LBMPGeneratorQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Check if the date range is in the database
        missingDates = find_missing_dates(start, end, RealTimeWT_LBMPGeneratorModel)

        # Scrape missing data
        if missingDates:
            scrape_real_time_wt_lbmp_generator(missingDates)

        # Retrieve all data in between start and end from database
        query = db.session.query(RealTimeWT_LBMPGeneratorModel).filter(RealTimeWT_LBMPGeneratorModel.timestamp.between(start, end))

        if validated.get('ptid'):
            query = query.filter(RealTimeWT_LBMPGeneratorModel.ptid.in_(validated['ptid']))

        results = query.all()
    
        # Serialize data
        json_data = RealTimeWT_LBMPGeneratorValidation(many=True).dump(results)

        return jsonify(json_data)