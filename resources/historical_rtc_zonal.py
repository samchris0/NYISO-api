import logging
import datetime
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from nyiso_api.extensions import db
from nyiso_api.schemas.historical_rtc_zonal import HistoricalRTCZonalQuery, HistoricalRTCZonalValidation
from nyiso_api.scrape.historical_rtc_zonal import scrape_historical_rtc_zonal
from nyiso_api.models.historical_rtc_zonal import HistoricalRTCZonalModel
from nyiso_api.utils.get_date_range import get_date_range

logger = logging.getLogger(__name__)

class HistoricalRTCZonal(Resource):

    def post(self):
        payload = request.get_json() or {}

        try:
            validated = HistoricalRTCZonalQuery(
                only=("start", "end")
            ).load(payload)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        scrape_historical_rtc_zonal(
            get_date_range(validated["start"], validated["end"])
        )
        return {"message": "Historical RTC zonal data ingested"}, 200
    
    def get(self):
        query_params = request.args.to_dict()
        query_params["ptid"] = request.args.getlist("ptid")
        try:
            validated = HistoricalRTCZonalQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Retrieve all data in between start and end from database
        query = db.session.query(HistoricalRTCZonalModel).filter(HistoricalRTCZonalModel.timestamp.between(start, end))

        if validated.get('ptid'):
            query = query.filter(HistoricalRTCZonalModel.ptid.in_(validated['ptid']))

        results = query.order_by(
            HistoricalRTCZonalModel.timestamp,
            HistoricalRTCZonalModel.ptid,
        ).all()
    
        # Serialize data
        json_data = HistoricalRTCZonalValidation(many=True).dump(results)
        
        return jsonify(json_data)
