import logging
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from schemas.load_bid_zonal import LoadBidZonalQuery, LoadBidZonalValidation
from scrape.load_bid_zonal import scrape_load_bid_zonal
from models.load_bid_zonal import LoadBidZonalModel
from utils.find_missing_dates import find_missing_dates

class LoadBidZonal(Resource):

    def get(Self):
        query_params = request.args.to_dict()
        try:
            validated = LoadBidZonalQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Check if the date range is in the database
        missingDates = find_missing_dates(start, end, LoadBidZonalModel)

        # Scrape missing data
        if missingDates:
            scrape_load_bid_zonal(missingDates)

        # Retrieve all data in between start and end from database
        query = db.session.query(LoadBidZonalModel).filter(LoadBidZonalModel.timestamp.between(start, end))

        if validated.get('ptid'):
            query = query.filter(LoadBidZonalModel.ptid.in_(validated['ptid']))

        results = query.all()
    
        # Serialize data
        json_data = LoadBidZonalValidation(many=True).dump(results)

        return jsonify(json_data)
        return