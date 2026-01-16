import pandas as pd

def load_uidai_data():
    enrol = pd.read_csv("data/raw/enrol.csv")
    demo  = pd.read_csv("data/raw/demo_update.csv")
    bio   = pd.read_csv("data/raw/bio_update.csv")

    return enrol, demo, bio
