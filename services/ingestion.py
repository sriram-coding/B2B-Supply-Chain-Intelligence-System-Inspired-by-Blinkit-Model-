import pandas as pd
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_employees():
    path = os.path.join(DATA_DIR, "employees.csv")
    return pd.read_csv(path)


def load_vendors():
    path = os.path.join(DATA_DIR, "vendors.csv")
    return pd.read_csv(path)


def load_logistics():
    path = os.path.join(DATA_DIR, "logistics.json")
    with open(path, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data)


def load_contracts():
    path = os.path.join(DATA_DIR, "contracts.csv")
    return pd.read_csv(path)


def load_all():
    return {
        "employees": load_employees(),
        "vendors": load_vendors(),
        "logistics": load_logistics(),
        "contracts": load_contracts(),
    }
