import logging
import datetime
from datetime import timedelta

from flask import request, jsonify
from flask_restful import Resource
from marshmallow import ValidationError

from nyiso_api.extensions import db
from nyiso_api.schemas.historical_rtc_generator import HistoricalRTCGeneratorQuery, HistoricalRTCGeneratorValidation
from nyiso_api.scrape.historical_rtc_generator import scrape_historical_rtc_generator
from nyiso_api.models.historical_rtc_generator import HistoricalRTCGeneratorModel
from nyiso_api.utils.get_date_range import get_date_range

logger = logging.getLogger(__name__)

class HistoricalRTCGenerator(Resource):

    def post(self):
        payload = request.get_json() or {}

        try:
            validated = HistoricalRTCGeneratorQuery(
                only=("start", "end")
            ).load(payload)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        scrape_historical_rtc_generator(
            get_date_range(validated["start"], validated["end"])
        )
        return {"message": "Historical RTC generator data ingested"}, 200
    
    def get(self):
        query_params = request.args.to_dict()
        query_params["ptid"] = request.args.getlist("ptid")
        try:
            validated = HistoricalRTCGeneratorQuery().load(query_params)
        except ValidationError as err:
            return {"errors": err.messages}, 400
        
        start = validated['start']
        end = validated['end']

        # Retrieve all data in between start and end from database
        query = db.session.query(HistoricalRTCGeneratorModel).filter(HistoricalRTCGeneratorModel.timestamp.between(start, end))

        if validated.get('ptid'):
            query = query.filter(HistoricalRTCGeneratorModel.ptid.in_(validated['ptid']))

        results = query.order_by(
            HistoricalRTCGeneratorModel.timestamp,
            HistoricalRTCGeneratorModel.ptid,
        ).all()
    
        # Serialize data
        json_data = HistoricalRTCGeneratorValidation(many=True).dump(results)

        return jsonify(json_data)
