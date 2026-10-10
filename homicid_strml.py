import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.title("National Incident-Based Reporting System (NIBRS)")

st.markdown("Get the NIBRS data")

nibrs_url = "https://api.ojp.gov/bjsdataset/v1/x3sz-eb6y.json?$limit=10000"

response = requests.get(nibrs_url)


if response.status_code == 200:

    data = response.json()

    df_nibrs = pd.DataFrame(data)

    st.subheader("NIBRS Data")
    st.dataframe(df_nibrs.head(5))

else:

    st.error(
        f"Failed to load data. Status code: {response.status_code}"
    )

    st.stop()


st.caption("Cleaning the data: removing unnecessary columns")

columns_to_keep = [
    "estimate",
    "indicator_name",
    "estimate_type",
    "estimate_domain_1",
    "estimate_domain_2",
    "population_estimate",
    "time_series_start_year"

]

st.caption("subsetting the dataframe first")

df_nibrs_clean = df_nibrs[columns_to_keep].copy()
numeric_cols = ["population_estimate","time_series_start_year"]
for col in numeric_cols:
    if col in df_nibrs_clean.columns:

        st.caption(
            f"Converting {col} to int, filling NaN values with 0"
            )
        df_nibrs_clean[col] = pd.to_numeric(df_nibrs_clean[col],errors="coerce").fillna(0).astype(int)

st.caption("clean nibrs data")

st.dataframe(df_nibrs_clean.head(5))


st.caption("Look at the different indicators")


st.subheader("Crime Indicators")

st.write(
    "Number of unique indicators:",
    df_nibrs_clean["indicator_name"].unique()
)

indicator_counts = (
    df_nibrs_clean["indicator_name"]
    .value_counts()
    .reset_index()
)
st.write(indicator_counts)

indicator_counts.columns = ["Indicator", "Count"]

st.dataframe(indicator_counts)


st.write("=" * 20)
st.caption("Select homicide records")

st.subheader("Murder and Non-negligent Manslaughter")

df_homicide = df_nibrs_clean[
    df_nibrs_clean["indicator_name"]
    == "Murder and Non-negligent Manslaughter"
].copy()

st.write("Homicide records:", df_homicide.shape[0])

st.dataframe(df_homicide)

st.markdown("Homicide estimates")

st.subheader("Homicide Estimates")

st.caption("\nConvert estimate to number")

df_homicide["estimate"] = pd.to_numeric(
    df_homicide["estimate"],
    errors="coerce"
)

st.caption("\nRemove rows where estimate is missing")
df_homicide = df_homicide.dropna(
    subset=["estimate"]
)

st.caption("Homicide by year")

yearly_homicide = (
    df_homicide
    .groupby("time_series_start_year", as_index=False)["estimate"]
    .sum()
)

yearly_homicide = yearly_homicide.sort_values(
    "time_series_start_year"
)

st.dataframe(yearly_homicide)

st.caption("Creating graphs")

fig = px.bar(
    yearly_homicide,
    x="time_series_start_year",
    y="estimate",
    title="Murder and Non-negligent Manslaughter Estimates by Year",
    labels={
        "time_series_start_year": "Year",
        "estimate": "Estimated Number of Incidents"
    }
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.markdown("scatter plots")

fig = px.scatter(
    yearly_homicide,
    x="time_series_start_year",
    y="estimate",
    title="Murder and Non-negligent Manslaughter Estimates by Year",
    labels={
        "time_series_start_year": "Year",
        "estimate": "Estimated Number of Incidents"
    }
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# st.write(df_nibrs.columns.to_list())

def validate_nibrs_data(df_nibrs):
    errors = []

    # check required columns presence
    expected_col = ["estimate",
        "indicator_name",
        "estimate_type",
        "estimate_domain_1",
        "estimate_domain_2",
        "population_estimate",
        "time_series_start_year"]