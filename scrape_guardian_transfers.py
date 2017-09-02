import urllib2
import json
import pandas as pd
import datetime
from pandas.io.json import json_normalize

# Grab the data
req =  urllib2.Request("https://interactive.guim.co.uk/docsdata/1YJQzO5Ngc6LSydUaidGNKQi6Zi3Ipi-Q3E59-v2fjgc.json")
read_data = urllib2.urlopen(req)
data = read_data.read()
guardian = json.loads(data)

# Get just the transfers data, and turn it into a DataFrame
transfers = pd.DataFrame.from_records(guardian['sheets']['Transfers'])

# Change data types/rename on various fields
transfers = transfers.rename(columns = {'id - do not change':'id'})
transfers['price_pounds'] = pd.to_numeric(transfers.price_pounds)
transfers['price_euros'] = pd.to_numeric(transfers.price_euros)
transfers['date'] = pd.to_datetime(transfers.date)
transfers['timestamp'] = pd.to_datetime(transfers.timestamp)

transfers_csv = transfers[['player_name',
'new_club',
'new_league',
'previous_club',
'previous_league',
'price_euros',
'price_pounds',
'timestamp',
'transfer_type']]

today = datetime.datetime.now().date().strftime("%Y-%m-%d")
# Save all data to csv
transfers_csv.to_csv("guardian_all_transfers_" + today + ".csv",encoding="utf-8")

#### Various other spreadsheets####


# List of the top five leagues to help with filtering
top_five = ['Premier League','Ligue 1','Serie A', 'Bundesliga','La Liga']

# Number of outgoing players by club
club_outgoings = (transfers.loc[transfers.previous_league.isin(top_five)]
                                                .groupby(['previous_club','previous_league'])
                                                .id.nunique())
club_outgoings = pd.DataFrame(club_outgoings).rename(columns = {"id":"count"})
club_outgoings.to_csv("club_outgoings.csv",encoding="utf-8")

# Number of incoming players by club
club_incomings = (transfers.loc[transfers.new_league.isin(top_five)]
                                                .groupby(['new_club','new_league'])
                                                .id.nunique())
club_incomings = pd.DataFrame(club_incomings).rename(columns = {"id":"count"})
club_incomings.to_csv("club_incomings.csv",encoding="utf-8")

# Money out on new players
spending_by_club_in = (transfers.loc[transfers.new_league.isin(top_five)]
                                                .groupby(['new_club','new_league'])
                                                .price_pounds.agg(['sum','count']))

spending_by_club_in = pd.DataFrame(spending_by_club_in).reset_index()
spending_by_club_in = spending_by_club_in.rename(columns = {"sum":"total_spent","count":"num_players"})
spending_by_club_in = spending_by_club_in.loc[spending_by_club_in.num_players > 0]

spending_by_club_in.to_csv("club_spending_in.csv",encoding="utf-8")

# Money in from old players

spending_by_club_out = (transfers.loc[transfers.previous_league.isin(top_five)]
                                                .groupby(['previous_club','previous_league'])
                                                .price_pounds.agg(['sum','count']))

spending_by_club_out = pd.DataFrame(spending_by_club_out).reset_index()
spending_by_club_out = spending_by_club_out.rename(columns = {"sum":"total_spent","count":"num_players"})
spending_by_club_out = spending_by_club_out.loc[spending_by_club_out.num_players > 0]

spending_by_club_out.to_csv("club_spending_out.csv",encoding="utf-8")
