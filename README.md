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

<summary>Day-Ahead</summary>
<br />
Endpoint:

*'/ancillary-services/day-ahead'*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2012-12-21 0:00" | Yes |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Node |
| ptid | Integer | ID of Node |
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

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2012-12-21 0:00" | Yes |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Node |
| ptid | Integer | ID of Node |
| spinning_reserve_10min | Float | Price of 10 Minute Spinning Reserve |
| non_sync_reserve_10min | Float | Price of 10 Minute Non-Synchronous Reserve |
| operating_reserve_30min | Float | Price of 30 Minute Operating Reserve |
| regulation_capacity | Float | Price of Regulation Capacity | 
| regulation_movement | Float | Price of Regulation Movement | 

Notes:

Ancillary services data reporting changes several times in the historical records. Earliest ancillary data is reported across the whole state and is given a name NYISO and does not have a ptid. For all data, ancillary services data has been standardized to a long output format. 

</details>

## Locational Based Marginal Pricing

### Day-Ahead

<details>

<summary>Generator Price</summary>
<br />

Endpoint:

*'/lbmp/day-ahead/generator'*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2012-12-21 0:00" | Yes |
| ptid | Integer | Point indentification of node | 323608 | No |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Node |
| ptid | Integer | ID of Node |
| lbmp | Float | Locational Based Marginal Price (LBMP) |
| marginal_cost_losses | Float | Loss Component of LBMP |
| marginal_cost_congestion | Float | Congestion Component of LBMP |
    
</details>

<details>

<summary>Zonal Price</summary>
<br />

Endpoint:

*'/lbmp/day-ahead/zonal'*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2012-12-21 0:00" | Yes |
| ptid | Integer | Point indentification of node | 323608 | No |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Node |
| ptid | Integer | ID of Node |
| lbmp | Float | Locational Based Marginal Price (LBMP) |
| marginal_cost_losses | Float | Loss Component of LBMP |
| marginal_cost_congestion | Float | Congestion Component of LBMP |

</details>

### Real-Time

<details>

<summary>Generator Price</summary>
<br />

Endpoint:

*'/lbmp/real-tim/generator'*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2012-12-21 0:00" | Yes |
| ptid | Integer | Point indentification of node | 323608 | No |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Node |
| ptid | Integer | ID of Node |
| lbmp | Float | Locational Based Marginal Price (LBMP) |
| marginal_cost_losses | Float | Loss Component of LBMP |
| marginal_cost_congestion | Float | Congestion Component of LBMP |
    
</details>

<details>

<summary>Zonal Price</summary>
<br />

Endpoint:

*'/lbmp/real-time/zonal'*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2012-12-21 0:00" | Yes |
| ptid | Integer | Point indentification of node | 323608 | No |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Node |
| ptid | Integer | ID of Node |
| lbmp | Float | Locational Based Marginal Price (LBMP) |
| marginal_cost_losses | Float | Loss Component of LBMP |
| marginal_cost_congestion | Float | Congestion Component of LBMP |

</details>

### Real-Time Weighted

<details>

<summary>Generator Price</summary>
<br />

Endpoint:

*'/lbmp/real-time-wt/generator'*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2012-12-21 0:00" | Yes |
| ptid | Integer | Point indentification of node | 323608 | No |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Node |
| ptid | Integer | ID of Node |
| lbmp | Float | Locational Based Marginal Price (LBMP) |
| marginal_cost_losses | Float | Loss Component of LBMP |
| marginal_cost_congestion | Float | Congestion Component of LBMP |
    
</details>

<details>

<summary>Zonal Price</summary>
<br />

Endpoint:

*'/lbmp/real-time-wt/zonal'*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2012-12-21 0:00" | Yes |
| ptid | Integer | Point indentification of node | 323608 | No |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Node |
| ptid | Integer | ID of Node |
| lbmp | Float | Locational Based Marginal Price (LBMP) |
| marginal_cost_losses | Float | Loss Component of LBMP |
| marginal_cost_congestion | Float | Congestion Component of LBMP |

</details>

## Load

### Forecast

<details>

<summary>Zonal Bids</summary>
<br />

Endpoint:

*/load/forecast/zonal-bid*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2012-12-21 0:00" | Yes |
| ptid | Integer | Point indentification of node | 323608 | No |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Node |
| ptid | Integer | ID of Node |
| energy_bid_load | Float | MWh of physical load served in the DAM being bid as price takers |
| bilateral_load | Float | MWh of physical load served in the DAM via bilateral contracts |
| price_cap_load | Float | MWh of physical load served in the DAM being bid to be scheduled at or below a specific price |
| virtual_load | Float | MWh of non-physical load served in the DAM |
| virtual_supply | Float | MWh of non-physical negative load served in the DAM |

</details>

<details>

<summary>Load Forecast</summary>
<br />

Endpoint:

*/load/forecast/forecast*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2012-12-21 0:00" | Yes |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Zone |
| load | Float | Forecasted MWh of physical load for the given zone |

</details>

### Actual Load

<details>

<summary>Real-Time</summary>
<br />

Endpoint:

*/load/actual/real-time*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2012-12-21 0:00" | Yes |
| ptid | Integer | Point indentification of node | 323608 | No |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Zone |
| ptid | Integer | ID of Node |
| load | Float | MW of instantaneous physical load for the given zone |

</details>

<details>

<summary>Real-Time Integrated</summary>
<br />

Endpoint:

*/load/actual/integrated*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before current time | "2012-12-21 0:00" | Yes |
| ptid | Integer | Point indentification of node | 323608 | No |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Zone |
| ptid | Integer | ID of Node |
| integrated_load | Float | MW of physical load for the given zone integrated over the previous 5 minutes |

</details>

## Historical Real-Time Commitment

<details>

<summary>Ancillary Services</summary>
<br />

Endpoint:

*'/historical-rtc/ancillary'*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before 4/8/2014 17:15 | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before 4/8/2014 17:15 | "2012-12-21 0:00" | Yes |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Node |
| ptid | Integer | ID of Node |
| spinning_reserve_10min | Float | Price of 10 Minute Spinning Reserve |
| non_sync_reserve_10min | Float | Price of 10 Minute Non-Synchronous Reserve |
| operating_reserve_30min | Float | Price of 30 Minute Operating Reserve |
| regulation_capacity | Float | Price of Regulation Capacity | 
| regulation_movement | Float | Price of Regulation Movement | 

Notes:

Ancillary services data reporting changes several times in the historical records. Earliest ancillary data is reported across the whole state and is given a name NYISO and does not have a ptid. For all data, ancillary services data has been standardized to a long output format. 

</details>


<details>

<summary>Generator Price</summary>
<br />

Endpoint:

*'/historical-rtc/generator'*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before 4/8/2014 17:15 | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before 4/8/2014 17:15 | "2012-12-21 0:00" | Yes |
| ptid | Integer | Point indentification of node | 323608 | No |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Node |
| ptid | Integer | ID of Node |
| lbmp | Float | Locational Based Marginal Price (LBMP) |
| marginal_cost_losses | Float | Loss Component of LBMP |
| marginal_cost_congestion | Float | Congestion Component of LBMP |
    
</details>

<details>

<summary>Zonal Price</summary>
<br />

Endpoint:

*'/historical-rtc/zonal'*

Parameters:

| Name  | Type | Description | Example | Required |
| --- | --- | --- | --- | --- |
| start | String | Inclusive lower limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before 4/8/2014 17:15 | "2005-6-6 9:15:00" | Yes |
| end | String | Inclusive upper limit of query range in an ISO 8601 format, must be after 11/18/1999 00:00 and before 4/8/2014 17:15 | "2012-12-21 0:00" | Yes |
| ptid | Integer | Point indentification of node | 323608 | No |

Returns:

List of JSON Objects in the following format

| Name  | Type | Description |
| --- | --- | --- |
| timestamp | Datetime | Timestamp of Data Point
| name | String | Name of Node |
| ptid | Integer | ID of Node |
| lbmp | Float | Locational Based Marginal Price (LBMP) |
| marginal_cost_losses | Float | Loss Component of LBMP |
| marginal_cost_congestion | Float | Congestion Component of LBMP |

</details>

