import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from schemas.real_time_wt_lbmp_zonal import RealTimeWT_LBMPZonalQuery, RealTimeWT_LBMPZonalValidation
from scrape.real_time_wt_lbmp_zonal import scrape_real_time_wt_lbmp_zonal 
from models.real_time_wt_lbmp_zonal import RealTimeWT_LBMPZonalModel
from utils.find_missing_dates import find_missing_dates

class RealTimeWeightedLBMPZonal(Resource):

    def get(Self):
        query_params = request.args.to_dict()
        try:
            validated = RealTimeWT_LBMPZonalQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Check if the date range is in the database
        missingDates = find_missing_dates(start, end, RealTimeWT_LBMPZonalModel)

        # Scrape missing data
        if missingDates:
            scrape_real_time_wt_lbmp_zonal(missingDates)

        # Retrieve all data in between start and end from database
        query = db.session.query(RealTimeWT_LBMPZonalModel).filter(RealTimeWT_LBMPZonalModel.timestamp.between(start, end))

        if validated.get('ptid'):
            query = query.filter(RealTimeWT_LBMPZonalModel.ptid.in_(validated['ptid']))

        results = query.all()
    
        # Serialize data
        json_data = RealTimeWT_LBMPZonalValidation(many=True).dump(results)

        return jsonify(json_data)
        return