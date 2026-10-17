import requests
import pandas as pd
import plotly.express as px
import streamlit as st
from math import erfc, sqrt


st.set_page_config(
    page_title="Australia and USA Homicide Analysis",
    page_icon="📊",
    layout="wide"
)

st.title("Homicide Data Analysis: Australia and USA")
st.caption("Homicide trends, firearm involvement and statistical testing")


#  RESEARCH QUESTION AND OBJECTIVES

with st.expander("Research question and objectives", expanded=False):
    st.markdown("""
    **Research question**

    How have homicide rates changed in Australia, and how have
    US homicide estimates and weapon involvement changed over time?

    **Objectives**

    1. Examine Australia's intentional homicide rate.
    2. Analyze US homicide offense counts and rates.
    3. Examine firearm involvement and other weapon categories.
    4. Test the change in the US firearm proportion between 2022 and 2024.
    5. Compare overlapping annual rates while recognizing differences
       between the two data sources.
    """)


# LOAD DATA

@st.cache_data(ttl=3600)
def load_australia():
    url = (
        "https://api.worldbank.org/v2/country/AUS/"
        "indicator/VC.IHR.PSRC.P5"
        "?date=1990:2026&format=json&per_page=10000"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    if len(data) < 2 or data[1] is None:
        return pd.DataFrame()

    df = pd.json_normalize(data[1])

    df = df.rename(columns={
        "countryiso3code": "country_code",
        "date": "Year",
        "value": "Indicator_Value",
        "indicator.id": "Indicator_id",
        "indicator.value": "Indicator_name",
        "country.value": "Country_name"
    })

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Indicator_Value"] = pd.to_numeric(
        df["Indicator_Value"], errors="coerce"
    )

    df = df.dropna(
        subset=["Year", "Indicator_Value"]
    ).copy()

    df["Year"] = df["Year"].astype(int)

    return df.sort_values("Year")


@st.cache_data(ttl=3600)
def load_usa():
    url = (
        "https://api.ojp.gov/bjsdataset/v1/"
        "x3sz-eb6y.json?$limit=10000"
    )

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    return pd.DataFrame(response.json())


try:
    df_australia = load_australia()
    df_nibrs = load_usa()

except Exception as error:
    st.error(f"Unable to load data: {error}")
    st.stop()


if df_australia.empty or df_nibrs.empty:
    st.error("One or both datasets returned no records.")
    st.stop()


# CLEAN US DATA

us_homicide = df_nibrs[
    df_nibrs["indicator_name"].eq(
        "Murder and Non-negligent Manslaughter"
    )
].copy()

us_homicide["Year"] = pd.to_numeric(
    us_homicide["time_series_start_year"],
    errors="coerce"
)

for col in [
    "estimate",
    "estimate_standard_error",
    "estimate_lower_bound",
    "estimate_upper_bound"
]:
    if col in us_homicide.columns:
        us_homicide[col] = pd.to_numeric(
            us_homicide[col], errors="coerce"
        )

us_homicide = us_homicide.dropna(
    subset=["Year", "estimate"]
).copy()

us_homicide["Year"] = us_homicide["Year"].astype(int)

# Keep national estimates where available.
if "estimate_geographic_location" in us_homicide.columns:
    us_homicide = us_homicide[
        us_homicide["estimate_geographic_location"] == "National"
    ].copy()

# Prefer final estimates where the source identifies them.
if "estimates_version" in us_homicide.columns:
    final_rows = us_homicide[
        us_homicide["estimates_version"] == "final"
    ]

    if not final_rows.empty:
        us_homicide = final_rows.copy()


# PREPARE US COUNTS AND RATES

us_counts = us_homicide[
    (us_homicide["estimate_type"] == "count")
    & (us_homicide["estimate_domain_1"] == "Offense count")
].copy()

us_rates = us_homicide[
    (us_homicide["estimate_type"] == "rate")
    & (
        us_homicide["estimate_domain_1"]
        == "Offense rate (per 100k total pop)"
    )
].copy()


# Remove duplicate years from the specific national series.
# If duplicates remain, inspect the source records before interpreting.
us_counts = us_counts.drop_duplicates("Year")
us_rates = us_rates.drop_duplicates("Year")


# FIREARM PERCENTAGES AND WEAPON CATEGORIES

firearm_share = us_homicide[
    (us_homicide["estimate_type"] == "percentage")
    & (us_homicide["estimate_domain_1"] == "Weapon involved")
    & (us_homicide["estimate_domain_2"] == "Firearms")
].copy()

firearm_share = firearm_share.drop_duplicates("Year")


# All weapon-involvement percentage categories.
weapon_share = us_homicide[
    (us_homicide["estimate_type"] == "percentage")
    & (us_homicide["estimate_domain_1"] == "Weapon involved")
    & (~us_homicide["estimate_domain_2"].isin(["Yes", "No"]))
].copy()


# Remove repeated year/category combinations.
weapon_share = weapon_share.drop_duplicates(
    ["Year", "estimate_domain_2"]
)


# joins

aus_join = df_australia[
    ["Year", "Indicator_Value"]
].rename(columns={
    "Indicator_Value": "Australia_Homicide_Rate"
}).copy()

us_join = us_rates[
    ["Year", "estimate", "population_estimate", "agency_counts"]
].rename(columns={
    "estimate": "US_NIBRS_Offense_Rate"
}).copy()

if (
    aus_join["Year"].duplicated().any()
    or us_join["Year"].duplicated().any()
):
    st.error(
        "Duplicate years detected. Inspect the source records "
        "before creating the comparison."
    )
    st.stop()

df_comparison = pd.merge(
    aus_join,
    us_join,
    on="Year",
    how="inner",
    validate="one_to_one"
)


# FILTERS

st.sidebar.header("Dashboard filters")

country_view = st.sidebar.selectbox(
    "Country",
    ["Both countries", "USA", "Australia"]
)

aus_min = int(df_australia["Year"].min())
aus_max = int(df_australia["Year"].max())

aus_years = st.sidebar.slider(
    "Australia: year range",
    min_value=aus_min,
    max_value=aus_max,
    value=(aus_min, aus_max)
)

if not us_homicide.empty:
    us_min = int(us_homicide["Year"].min())
    us_max = int(us_homicide["Year"].max())

    if us_min < us_max:
        us_years = st.sidebar.slider(
            "USA: year range",
            min_value=us_min,
            max_value=us_max,
            value=(us_min, us_max)
        )
    else:
        us_years = (us_min, us_max)
else:
    us_years = (2022, 2024)


# Apply filters independently.
df_aus_view = df_australia[
    df_australia["Year"].between(*aus_years)
].copy()

us_counts_view = us_counts[
    us_counts["Year"].between(*us_years)
].copy()

us_rates_view = us_rates[
    us_rates["Year"].between(*us_years)
].copy()

firearm_view = firearm_share[
    firearm_share["Year"].between(*us_years)
].copy()

weapon_view = weapon_share[
    weapon_share["Year"].between(*us_years)
].copy()


# AUSTRALIA DASHBOARD

if country_view in ["Both countries", "Australia"]:

    st.header("Australia")

    if not df_aus_view.empty:

        first = df_aus_view.iloc[0]
        last = df_aus_view.iloc[-1]

        if first["Indicator_Value"] != 0:
            change_pct = (
                (last["Indicator_Value"] - first["Indicator_Value"])
                / first["Indicator_Value"]
            ) * 100
        else:
            change_pct = float("nan")

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "First selected rate",
            f"{first['Indicator_Value']:.2f}"
        )

        c2.metric(
            "Latest selected rate",
            f"{last['Indicator_Value']:.2f}"
        )

        c3.metric(
            "Change across selected period",
            f"{change_pct:.2f}%"
        )

        fig_aus = px.line(
            df_aus_view,
            x="Year",
            y="Indicator_Value",
            markers=True,
            title="Intentional homicide rate",
            labels={
                "Year": "Year",
                "Indicator_Value": "Rate per 100,000 people"
            }
        )

        st.plotly_chart(fig_aus, use_container_width=True)

        st.caption(
            "Source: World Bank. Rate per 100,000 people."
        )

    else:
        st.info("No Australian observations in this period.")


# USA DASHBOARD

if country_view in ["Both countries", "USA"]:

    st.header("USA: NIBRS homicide analysis")

    if not us_counts_view.empty:

        latest_count = us_counts_view.sort_values("Year").iloc[-1]

        c1, c2 = st.columns(2)

        c1.metric(
            "Latest estimated homicide count",
            f"{latest_count['estimate']:,.0f}"
        )

        c2.metric(
            "Year",
            f"{int(latest_count['Year'])}"
        )

        fig_counts = px.line(
            us_counts_view.sort_values("Year"),
            x="Year",
            y="estimate",
            markers=True,
            title="Estimated homicide offenses",
            labels={
                "Year": "Year",
                "estimate": "Estimated offenses"
            }
        )

        st.plotly_chart(fig_counts, use_container_width=True)

    else:
        st.info("No national homicide count estimates found.")

    if not us_rates_view.empty:

        fig_rates = px.line(
            us_rates_view.sort_values("Year"),
            x="Year",
            y="estimate",
            markers=True,
            title="Estimated homicide offense rate",
            labels={
                "Year": "Year",
                "estimate": "Rate per 100,000 people"
            }
        )

        st.plotly_chart(fig_rates, use_container_width=True)

    # FIREARM PROPORTION
    st.subheader("Firearm involvement")

    if not firearm_view.empty:

        fig_firearm = px.line(
            firearm_view.sort_values("Year"),
            x="Year",
            y="estimate",
            markers=True,
            title="Proportion of homicide offenses involving firearms",
            labels={
                "Year": "Year",
                "estimate": "Percentage (%)"
            }
        )

        st.plotly_chart(fig_firearm, use_container_width=True)

        st.dataframe(
            firearm_view[
                [
                    "Year",
                    "estimate",
                    "estimate_standard_error",
                    "estimate_lower_bound",
                    "estimate_upper_bound"
                ]
            ].sort_values("Year"),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No firearm percentage records found.")

    # OTHER WEAPON CATEGORIES
    st.subheader("Weapon involvement by category")

    if not weapon_view.empty:

        fig_weapons = px.bar(
            weapon_view.sort_values("Year"),
            x="Year",
            y="estimate",
            color="estimate_domain_2",
            barmode="group",
            title="Homicide weapon categories",
            labels={
                "Year": "Year",
                "estimate": "Percentage (%)",
                "estimate_domain_2": "Weapon category"
            }
        )

        st.plotly_chart(fig_weapons, use_container_width=True)

    else:
        st.info("No additional weapon percentage categories found.")


# PRELIMINARY Z-TEST: 2022 VS 2024

if country_view in ["Both countries", "USA"]:

    st.subheader("Statistical test: firearm proportion")

    test_data = firearm_share[
        firearm_share["Year"].isin([2022, 2024])
    ].copy()

    test_data = test_data.drop_duplicates("Year")
    test_data = test_data.set_index("Year")

    if (
        2022 in test_data.index
        and 2024 in test_data.index
        and "estimate_standard_error" in test_data.columns
    ):

        p_2022 = test_data.loc[2022, "estimate"]
        p_2024 = test_data.loc[2024, "estimate"]

        se_2022 = test_data.loc[
            2022, "estimate_standard_error"
        ]

        se_2024 = test_data.loc[
            2024, "estimate_standard_error"
        ]

        if (
            pd.notna(se_2022)
            and pd.notna(se_2024)
            and se_2022 > 0
            and se_2024 > 0
        ):

            difference = p_2024 - p_2022

            # Preliminary independent-estimates approximation.
            se_difference = sqrt(se_2022**2 + se_2024**2)

            z_stat = difference / se_difference

            # Two-sided normal-approximation p-value.
            p_value = erfc(abs(z_stat) / sqrt(2))

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Z-statistic",
                f"{z_stat:.3f}"
            )

            c2.metric(
                "Standard error of difference",
                f"{se_difference:.4f}"
            )

            c3.metric(
                "P-value",
                f"{p_value:.6g}"
            )

            st.write(
                f"2022 firearm proportion: **{p_2022:.2f}%**"
            )

            st.write(
                f"2024 firearm proportion: **{p_2024:.2f}%**"
            )

            st.write(
                f"Change: **{difference:.2f} percentage points**"
            )

            if p_value < 0.05:
                st.success(
                    "The preliminary test indicates a statistically "
                    "significant difference at the 5% level."
                )
            else:
                st.info(
                    "The preliminary test does not show a statistically "
                    "significant difference at the 5% level."
                )

            st.caption(
                "Important: This is an independent-estimates "
                "approximation. Confirm the appropriate NIBRS "
                "variance and covariance method before reporting "
                "this as a definitive hypothesis test."
            )

        else:
            st.warning(
                "Valid positive standard errors are needed for the test."
            )

    else:
        st.warning(
            "The 2022 and 2024 firearm estimates and their standard "
            "errors must both be available to calculate this test."
        )


# JOINED COMPARISON

if country_view == "Both countries":

    st.header("Joined Australia–USA comparison")

    if not df_comparison.empty:

        st.dataframe(
            df_comparison,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download joined comparison CSV",
            data=df_comparison.to_csv(index=False).encode("utf-8"),
            file_name="australia_usa_homicide_comparison.csv",
            mime="text/csv"
        )

        fig_comparison = px.line(
            df_comparison.sort_values("Year"),
            x="Year",
            y=[
                "Australia_Homicide_Rate",
                "US_NIBRS_Offense_Rate"
            ],
            markers=True,
            title="Overlapping annual homicide rates",
            labels={
                "value": "Rate per 100,000 people",
                "variable": "Country / source",
                "Year": "Year"
            }
        )

        st.plotly_chart(
            fig_comparison,
            use_container_width=True
        )

        st.caption(
            "The join remains an inner join by year. "
            "Similar units do not guarantee identical definitions "
            "or reporting coverage."
        )

    else:
        st.warning(
            "No overlapping years were found in the source records."
        )


# DOWNLOAD DATA

st.header("Download data")

if country_view in ["Both countries", "Australia"]:

    st.download_button(
        "Download Australian data",
        data=df_australia.to_csv(index=False).encode("utf-8"),
        file_name="australia_homicide_rates.csv",
        mime="text/csv"
    )

if country_view in ["Both countries", "USA"]:

    st.download_button(
        "Download US homicide data",
        data=us_homicide.to_csv(index=False).encode("utf-8"),
        file_name="us_nibrs_homicide_data.csv",
        mime="text/csv"
    )


# 13. METHODOLOGY

with st.expander("Methodology and limitations"):

    st.markdown("""
    - **Australia:** World Bank intentional homicide rate per 100,000.
    - **USA:** NIBRS estimates for Murder and Non-negligent Manslaughter.
    - **Weapons:** NIBRS estimates of weapon involvement by category.
    - **Join:** Existing inner join on year; only overlapping years remain.
    - **Statistical test:** Preliminary two-sided Z-test approximation
      comparing 2022 and 2024 firearm percentages.
    - **Limitation:** NIBRS estimates may require a specialized variance
      method. The preliminary Z-test should not be treated as definitive
      until its assumptions are verified.
    - **Coverage:** The API request is limited to 10,000 records.
      Confirm that the response includes all required years and categories.
    """)