"""Defines trends calculations for stations"""
import logging

import faust


logger = logging.getLogger(__name__)


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


# TODO: Define a Faust Stream that ingests data from the Kafka Connect stations topic and
#   places it into a new topic with only the necessary information.
app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")
topic = app.topic("postgres_conn_stations", value_type=Station)
out_topic = app.topic("stations.table", partitions=1)
table = app.Table(
    "transformed_station",
    default=TransformedStation,
    partitions=1,
    changelog_topic=out_topic,
)


#
#
# TODO: Using Faust, transform input `Station` records into `TransformedStation` records. Note that
# "line" is the color of the station. So if the `Station` record has the field `red` set to true,
# then you would set the `line` of the `TransformedStation` record to the string `"red"`
@app.agent(topic)
async def transform_stats(stations):
    async for s in stations:
        # Situation : Red
        if s.red is True:
            line = 'red'
        # Situation : Blue
        elif s.blue is True:
            line = 'blue'
         # Situation : Green
        elif s.green is True:
            line = 'green'
        # Other situations
        else:
            line = 'Null or other values'
        
        # Declare the command related to "TransformedStation"
         table[s.station_id] = TransformedStation(
            station_id=s.station_id,
            station_name=s.station_name,
            order=s.order,
            line=line
        )

if __name__ == "__main__":
    app.main()
