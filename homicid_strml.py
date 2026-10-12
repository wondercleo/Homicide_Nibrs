import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from scipy.stats import norm

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
    "estimate_standard_error",
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
        "estimate_standard_error",
        "estimate_type",
        "estimate_domain_1",
        "estimate_domain_2",
        "population_estimate",
        "time_series_start_year"]


st.caption("doing a statistical test")
st.caption("a statistical text, a suitable test depends on whether the dataset provides actual counts," \
"sample sizes, standard errors, or confidence intervals.")

# 1. Select the firearm percentage estimates
firearm_data = df_homicide[
    df_homicide["estimate_domain_1"].astype(str).str.strip().str.lower().eq("weapon involved")
    & df_homicide["estimate_domain_2"].astype(str).str.strip().str.lower().eq("firearms")
    & df_homicide["estimate_type"].astype(str).str.contains(
        "percentage|percent", case=False, na=False
    )
].copy()

# 2. Convert the required columns to numeric
firearm_data["time_series_start_year"] = pd.to_numeric(
    firearm_data["time_series_start_year"], errors="coerce"
)
firearm_data["estimate"] = pd.to_numeric(
    firearm_data["estimate"], errors="coerce"
)

# Check whether the dataset contains a standard-error column
se_col = "estimate_standard_error"

st.subheader("Check data for the statistical test")

if se_col not in firearm_data.columns:
    st.error(
        "A standard-error column was not found. "
        "Inspect df_homicide.columns before choosing the test."
    )
else:
    firearm_data[se_col] = pd.to_numeric(
        firearm_data[se_col], errors="coerce"
    )

    # 3. Keep only the years we want to compare
    comparison = firearm_data[
        firearm_data["time_series_start_year"].isin([2022, 2024])
    ].dropna(subset=["estimate", se_col])

    st.dataframe(
        comparison[
            ["time_series_start_year", "estimate", se_col]
        ].sort_values("time_series_start_year")
    )

    # 4. Test only if there is exactly one valid estimate per year
    counts = comparison["time_series_start_year"].value_counts()

    if counts.get(2022, 0) != 1 or counts.get(2024, 0) != 1:
        st.warning(
            "There must be exactly one valid firearm percentage estimate "
            "for each year. Check the filtered rows before testing."
        )
    else:
        row_2022 = comparison[
            comparison["time_series_start_year"] == 2022
        ].iloc[0]

        row_2024 = comparison[
            comparison["time_series_start_year"] == 2024
        ].iloc[0]

        p_2022 = row_2022["estimate"]
        p_2024 = row_2024["estimate"]
        se_2022 = row_2022[se_col]
        se_2024 = row_2024[se_col]

        # Standard error of the difference between two estimates
        se_difference = (se_2022**2 + se_2024**2) ** 0.5

        if se_difference <= 0:
            st.error("The combined standard error must be greater than zero.")
        else:
            # Two-sided z-test
            z_stat = (p_2024 - p_2022) / se_difference
            p_value = 2 * norm.sf(abs(z_stat))

            alpha = 0.05

            st.subheader("Hypothesis test results")
            st.metric("Z-statistic", f"{z_stat:.3f}")
            st.metric("P-value", f"{p_value:.4f}")
            st.write(f"Significance level: {alpha}")

            if p_value < alpha:
                st.success(
                    "Reject H₀: the difference is statistically significant "
                    "at the 5% level, subject to the test assumptions."
                )
            else:
                st.info(
                    "Fail to reject H₀: the available evidence does not show "
                    "a statistically significant difference at the 5% level."
                )