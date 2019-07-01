import quandl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

with open("quandl.key", "r") as f:
    quandl.ApiConfig.api_key = f.read()

source_dataset = {
    "Europe & Central Asia" : "WORLDBANK/ECS_EP_PMP_SGAS_CD",
    "Consumer Index for All Urban Consumers" : "FRED/CUUR0000SETB01"}

data = quandl\
    .DataSet(source_dataset["Consumer Index for All Urban Consumers"])\
    .data(params={"start_date": "2016-01-01"})# blocks shortly - async maybe
with open("data", "w") as f:
    for date, value in zip(data.index, data["Value"]):
        f.write(f"{date},{value}\n")