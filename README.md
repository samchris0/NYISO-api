# __New York Independent System Operator (NYISO) rest-API__

This is a publicly available API to integrate NYISO data into your workflow. You may download this repository and host it locally or virtually for your use.

# __0. Start-Up__
### Prerequisites:

To use this API locally you must have PostgreSQL installed on your device.

### Instructions:

1. Download and save the NYISO-api repository to your local files
2. Create a .env file and create the following variables

    PG_USER= \**PostgreSQL Username*\*

    PG_PASSWORD= \**PostgreSQL Password*\*

    PG_HOST= ex: localhost 

    PG_PORT= ex: 5432

    PG_DATABASE= ex: nyiso_db

    DATABASE_URL= ex: postgresql+psycopg2://*PG_USER*:*PG_PASSWORD*@localhost:5432/nyiso_db

3. Run the script and begin querying

   `python main.py`

# __1. End Points, Parameters, and Returns__

## Ancillary Services

<details>

<summary>Day Ahead</summary>
<br />
Endpoint:

*'/ancillary-services/day-ahead'*

Parameters:

| Name  | Description | Example |
| --- | --- | --- |
| start  | Datetime, inclusive lower limit of query range, must be after 11/18/1999 and before current time | "2005-6-6 9:15:00" |
| end  | Datetime, inclusive upper limit of query range, must be after 11/18/1999 and before current time | "2012-12-21 0:00" |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Bus |
| ptid | Integer | ID of Bus |
| spinning_reserve_10min | Float | Price of 10 Minute Spinning Reserve |
| non_sync_reserve_10min | Float | Price of 10 Minute Non-Synchronous Reserve |
| operating_reserve_30min | Float | Price of 30 Minute Operating Reserve |
| regulation_capacity | Float | Price of Regulation Capacity | 

Notes:

Ancillary services data reporting changes several times in the historical records. Earliest ancillary data is reported across the whole state and is given a name NYISO and does not have a ptid. For all data, ancillary services data has been standardized to a long output format. 

</details>

<details>

<summary>Real-Time</summary>
<br />

Endpoint:

*'/ancillary-services/real-time'*

Parameters:

| Name  | Description | Example |
| --- | --- | --- |
| start  | Datetime, inclusive lower limit of query range, must be after 11/18/1999 and before current time | "2005-6-6 9:15:00" |
| end  | Datetime, inclusive upper limit of query range, must be after 11/18/1999 and before current time | "2012-12-21 0:00" |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Bus |
| ptid | Integer | ID of Bus |
| spinning_reserve_10min | Float | Price of 10 Minute Spinning Reserve |
| non_sync_reserve_10min | Float | Price of 10 Minute Non-Synchronous Reserve |
| operating_reserve_30min | Float | Price of 30 Minute Operating Reserve |
| regulation_capacity | Float | Price of Regulation Capacity | 
| regulation_movement | Float | Price of Regulation Movement | 

Notes:

Ancillary services data reporting changes several times in the historical records. Earliest ancillary data is reported across the whole state and is given a name NYISO and does not have a ptid. For all data, ancillary services data has been standardized to a long output format. 

</details>

## Historical Real-Time Commitment

<details>

<summary>Ancillary</summary>
<br />

Endpoint:

*'/historical-rtc/ancillary'*

Parameters:

| Name  | Description | Example |
| --- | --- | --- |
| start | Datetime, inclusive lower limit of query range, must be after 11/18/1999 and before current time | "2005-6-6 9:15:00" |
| end | Datetime, inclusive upper limit of query range, must be after 11/18/1999 and before current time | "2012-12-21 0:00" |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Bus |
| ptid | Integer | ID of Bus |
| spinning_reserve_10min | Float | Price of 10 Minute Spinning Reserve |
| non_sync_reserve_10min | Float | Price of 10 Minute Non-Synchronous Reserve |
| operating_reserve_30min | Float | Price of 30 Minute Operating Reserve |
| regulation_capacity | Float | Price of Regulation Capacity | 
| regulation_movement | Float | Price of Regulation Movement | 

Notes:

Ancillary services data reporting changes several times in the historical records. Earliest ancillary data is reported across the whole state and is given a name NYISO and does not have a ptid. For all data, ancillary services data has been standardized to a long output format. 

</details>



