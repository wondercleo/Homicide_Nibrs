import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.title("National Incident-Based Reporting System (NIBRS)")

st.markdown("""
## Research Background and Hypothesis

### 1. Introduction

Homicide is a serious public safety issue in the United States.
Understanding patterns in homicide offenses can help researchers,
law enforcement agencies, and policymakers identify changes in
crime trends and develop evidence informed prevention strategies.

This project uses Python and Streamlit to explore homicide-related
data from the National Incident-Based Reporting System (NIBRS).
The analysis focuses on examining available estimates, identifying
patterns over time, and exploring the contribution of firearms to
homicide offenses.

### 2. Data Source

The data for this project are retrieved from the United States
Department of Justice's Office of Justice Programs data API:

https://api.ojp.gov/bjsdataset/v1/x3sz-eb6y.json?$limit=10000

The project uses the National Incident-Based Reporting System
(NIBRS), a crime-reporting system associated with the FBI's
Uniform Crime Reporting Program. NIBRS collects detailed
information about crime incidents reported by participating
law enforcement agencies.

Official information about NIBRS is available from the Bureau
of Justice Statistics (BJS):

https://bjs.ojp.gov/data-collection/national-incident-based-reporting-system-nibrs

The data are retrieved programmatically using the Python
requests library and processed using pandas. The available
records and variables determine which comparisons can be made.

### 3. Research Question

How does the estimated share of homicide offenses involving
firearms change over time in the United States?

### 4. Research Hypothesis

**Null Hypothesis (H0):** There is no statistically significant
change in the estimated share of homicide offenses involving
firearms over the period examined.

**Alternative Hypothesis (H1):** There is a statistically
significant change in the estimated share of homicide offenses
involving firearms over the period examined.

These hypotheses will be evaluated using the available data.
The direction and strength of any observed trend must be
determined from the analysis rather than assumed in advance.

### 5. Methodology

The project follows a data-analysis workflow:

1. Data collection: Retrieve the available records from the
   Department of Justice API using requests.
2. Data preparation: Convert the returned JSON records into
   a pandas DataFrame and inspect the available columns.
3. Data cleaning: Check data types, missing values, and the
   availability of the variables required for the analysis.
4. Exploratory analysis: Examine estimates across years and
   identify patterns or unusual changes.
5. Visualization: Use Plotly to create interactive charts
   showing changes over time.
6. Interpretation: Explain what the results indicate in
   relation to the research question and hypothesis.

### 6. Interpretation and Limitations

The charts describe patterns in the data available through
the selected API endpoint. An observed increase or decrease
does not, by itself, establish that one factor caused another.

The analysis must also consider the coverage of participating
law enforcement agencies, missing observations, the definition
of each indicator, and whether the values represent counts,
percentages, or statistical estimates.

A visual trend alone is not sufficient to establish statistical
significance. A suitable statistical test would be required
to formally evaluate the hypotheses.

### 7. Conclusion

This project demonstrates how publicly accessible US crime
data can be retrieved, prepared, analysed, and presented
using Python, pandas, Plotly, and Streamlit.

The final conclusion will be based on the observed results
and any appropriate statistical tests. The evidence will
determine whether the findings support rejecting the null
hypothesis or whether there is insufficient evidence to do so.
""")

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