import pandas as pd


def find_highest_risk(df):
    df['total_risk'] = df['earthquake_risk'] + df['flood_risk']
    highest_risk_row = df.loc[df['total_risk'].idxmax()]
    highest_risk_data = {
        'total_risk': highest_risk_row['total_risk'],
        'earthquake_risk': highest_risk_row['earthquake_risk'],
        'flood_risk': highest_risk_row['flood_risk'],
        'name': highest_risk_row['name']
    }
    return highest_risk_data


def find_dominant_risk_type(df, risk_columns):
    avg_risks = {}
    for risk in risk_columns:
        avg_risks[risk] = df[risk].mean()
    dominant_risk = max(avg_risks, key=avg_risks.get)
    avg_risk_value = avg_risks[dominant_risk]
    dominant_risk_data = {
        'dominant_risk': dominant_risk,
        'avg_risk_value': avg_risk_value
    }
    return dominant_risk_data

