
import requests
import pandas as pd
import plotly.express as px
from scipy.stats import norm
import matplotlib.pyplot as plt
import numpy as np

# Retrieve NIBRS data
nibrs_url = "https://api.ojp.gov/bjsdataset/v1/x3sz-eb6y.json?$limit=10000"

response = requests.get(nibrs_url, timeout=30)
response.raise_for_status()

data = response.json()
df_nibrs = pd.DataFrame(data)

print("NIBRS Data")
print(df_nibrs.head())

# Keep necessary columns
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

df_nibrs_clean = df_nibrs[columns_to_keep].copy()

# Convert numeric columns
numeric_cols = [
    "population_estimate",
    "time_series_start_year"
]

for col in numeric_cols:
    df_nibrs_clean[col] = (
        pd.to_numeric(df_nibrs_clean[col], errors="coerce")
        .fillna(0)
        .astype(int)
    )

print("\nClean NIBRS Data")
print(df_nibrs_clean.head())

# Examine indicators
print("\nUnique indicators:")
print(df_nibrs_clean["indicator_name"].unique())

indicator_counts = (
    df_nibrs_clean["indicator_name"]
    .value_counts()
    .rename_axis("Indicator")
    .reset_index(name="Count")
)

print("\nIndicator counts:")
print(indicator_counts)

# Select homicide records
df_homicide = df_nibrs_clean[
    df_nibrs_clean["indicator_name"]
    == "Murder and Non-negligent Manslaughter"
].copy()

print("\nHomicide records:", df_homicide.shape[0])

# Convert estimates to numeric
df_homicide["estimate"] = pd.to_numeric(
    df_homicide["estimate"],
    errors="coerce"
)

df_homicide = df_homicide.dropna(
    subset=["estimate"]
)

# Calculate yearly estimates
yearly_homicide = (
    df_homicide
    .groupby("time_series_start_year", as_index=False)["estimate"]
    .sum()
    .sort_values("time_series_start_year")
)

print("\nYearly homicide estimates:")
print(yearly_homicide.to_string(index=False))


# Bar chart
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

fig.show()

# Scatter plot
fig = px.scatter(
    yearly_homicide,
    x="time_series_start_year",
    y="estimate",
    title="Homicide Estimates by Year",
    labels={
        "time_series_start_year": "Year",
        "estimate": "Estimated Number of Incidents"
    }
)

fig.show()


# Select firearm percentage estimates
firearm_data = df_homicide[
    df_homicide["estimate_domain_1"]
    .astype(str).str.strip().str.lower()
    .eq("weapon involved")
    &
    df_homicide["estimate_domain_2"]
    .astype(str).str.strip().str.lower()
    .eq("firearms")
    &
    df_homicide["estimate_type"]
    .astype(str).str.contains(
        "percentage|percent",
        case=False,
        na=False
    )
].copy()

# Convert numeric columns
firearm_data["time_series_start_year"] = pd.to_numeric(
    firearm_data["time_series_start_year"],
    errors="coerce"
)

firearm_data["estimate"] = pd.to_numeric(
    firearm_data["estimate"],
    errors="coerce"
)

se_col = "estimate_standard_error"

firearm_data[se_col] = pd.to_numeric(
    firearm_data[se_col],
    errors="coerce"
)

# Compare 2022 and 2024
comparison = firearm_data[
    firearm_data["time_series_start_year"].isin([2022, 2024])
].dropna(subset=["estimate", se_col])

print("\nFirearm percentage estimates:")
print(
    comparison[
        ["time_series_start_year", "estimate", se_col]
    ].sort_values("time_series_start_year")
)

counts = comparison["time_series_start_year"].value_counts()

if counts.get(2022, 0) != 1 or counts.get(2024, 0) != 1:
    print("Cannot test: expected exactly one valid estimate per year.")

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

    se_difference = (se_2022**2 + se_2024**2) ** 0.5

    if se_difference <= 0:
        print("The combined standard error must be positive.")

    else:
        z_stat = (p_2024 - p_2022) / se_difference
        p_value = 2 * norm.sf(abs(z_stat))
        alpha = 0.05

        print("\nHypothesis Test Results")
        print(f"Z-statistic: {z_stat:.3f}")
        print(f"P-value: {p_value:.6f}")
        print(f"Significance level: {alpha}")

        if p_value < alpha:
            print(
                "Reject H0: the difference is statistically "
                "significant at the 5% level, subject to "
                "the test assumptions."
            )
        else:
            print(
                "Fail to reject H0: there is insufficient evidence "
                "of a statistically significant difference."
            )

# Retrieve Australian intentional homicide data
url = (
    "https://api.worldbank.org/v2/country/AUS/"
    "indicator/VC.IHR.PSRC.P5"
    "?date=1990%3A2026&format=json&per_page=10000"
)

response = requests.get(url, timeout=30)
response.raise_for_status()

data = response.json()

if len(data) < 2 or data[1] is None:
    raise ValueError("No World Bank records were returned.")

# Convert JSON records into a DataFrame
df = pd.json_normalize(data[1])

# Rename columns
df_clean = df.rename(columns={
    "countryiso3code": "country_code",
    "date": "Year",
    "value": "Indicator_Value",
    "unit": "Unit",
    "indicator.id": "Indicator_id",
    "indicator.value": "Indicator_name",
    "country.value": "Country_name"
}).copy()

# Keep required columns
columns_to_keep = [
    "country_code",
    "Country_name",
    "Year",
    "Indicator_id",
    "Indicator_name",
    "Indicator_Value",
    "Unit"
]

df_clean = df_clean[columns_to_keep].copy()

# Convert data types
df_clean["Year"] = pd.to_numeric(
    df_clean["Year"], errors="coerce"
)

df_clean["Indicator_Value"] = pd.to_numeric(
    df_clean["Indicator_Value"], errors="coerce"
)

# Remove missing observations and sort by year
df_australia = (
    df_clean
    .dropna(subset=["Year", "Indicator_Value"])
    .copy()
)

df_australia["Year"] = df_australia["Year"].astype(int)

df_australia = (
    df_australia
    .sort_values("Year")
    .reset_index(drop=True)
)

# Inspect the dataset
print("\nAustralian Homicide Data")
print("Dataset shape:", df_australia.shape)

print("\nColumn data types:")
print(df_australia.dtypes)

print("\nYear range:")
print(
    df_australia["Year"].min(),
    "to",
    df_australia["Year"].max()
)

print("\nSummary statistics:")
print(df_australia["Indicator_Value"].describe())

print("\nClean dataset:")
print(df_australia.to_string(index=False))


print("\nUS dataset shape:")
print(df_nibrs.shape)

print("\nAvailable columns:")
print(df_nibrs.columns.tolist())

print("\nAvailable indicators:")
print(df_nibrs["indicator_name"].dropna().unique())

print("\nEstimate types:")
print(df_nibrs["estimate_type"].dropna().unique())

print("\nYears available:")
print(
    df_nibrs["time_series_start_year"]
    .dropna()
    .unique()
)

df_australia = df_australia.sort_values("Year").copy()

df_australia["Annual_Change"] = (
    df_australia["Indicator_Value"].diff()
)

df_australia["Annual_Percent_Change"] = (
    df_australia["Indicator_Value"].pct_change() * 100
)

# Compare the first and last available years
first = df_australia.iloc[0]
last = df_australia.iloc[-1]

absolute_change = (
    last["Indicator_Value"] - first["Indicator_Value"]
)

percentage_change = (
    absolute_change / first["Indicator_Value"] * 100
)

# Find the highest and lowest rates
highest = df_australia.loc[
    df_australia["Indicator_Value"].idxmax()
]

lowest = df_australia.loc[
    df_australia["Indicator_Value"].idxmin()
]

print(f"First year: {first['Year']}")
print(f"First rate: {first['Indicator_Value']:.3f}")

print(f"\nLast year: {last['Year']}")
print(f"Last rate: {last['Indicator_Value']:.3f}")

print(f"\nAbsolute change: {absolute_change:.3f}")
print(f"Percentage change: {percentage_change:.2f}%")

print(
    f"\nHighest rate: {highest['Indicator_Value']:.3f}"
    f" in {highest['Year']}"
)

print(
    f"Lowest rate: {lowest['Indicator_Value']:.3f}"
    f" in {lowest['Year']}"
)

print("\nLatest annual changes:")
print(
    df_australia[
        ["Year", "Indicator_Value",
         "Annual_Change", "Annual_Percent_Change"]
    ].tail(10).round(3)
)


# Select the US homicide indicator
us_homicide = df_nibrs[
    df_nibrs["indicator_name"].eq(
        "Murder and Non-negligent Manslaughter"
    )
].copy()

# Examine rate estimates only
us_homicide_rates = us_homicide[
    us_homicide["estimate_type"].eq("rate")
].copy()

# Convert year and estimates to numeric
us_homicide_rates["Year"] = pd.to_numeric(
    us_homicide_rates["time_series_start_year"],
    errors="coerce"
)

us_homicide_rates["estimate"] = pd.to_numeric(
    us_homicide_rates["estimate"],
    errors="coerce"
)

# Inspect the records before deciding how to join
columns_to_inspect = [
    "Year",
    "indicator_name",
    "estimate_type",
    "estimate",
    "estimate_geographic_location",
    "estimate_domain_1",
    "estimate_domain_2",
    "population_estimate",
    "agency_counts"
]

print("US homicide indicator rows:", len(us_homicide))
print("US homicide rate rows:", len(us_homicide_rates))

print(
    us_homicide_rates[columns_to_inspect]
    .sort_values("Year")
    .to_string(index=False)
)

import matplotlib.pyplot as plt
import numpy as np

x = df_australia["Year"].to_numpy()
y = df_australia["Indicator_Value"].to_numpy()

# Fit a straight line to the annual observations
slope, intercept = np.polyfit(x, y, 1)

df_australia["Trend"] = slope * x + intercept

print(f"Annual linear trend: {slope:.4f}")
print(f"Average yearly change: {slope:.4f} per 100,000 people")

plt.figure(figsize=(12, 6))

plt.plot(
    x, y,
    marker="o",
    label="Observed homicide rate"
)

plt.plot(
    x, df_australia["Trend"],
    linestyle="--",
    label="Linear trend"
)

plt.title("Australia: Intentional Homicide Rate, 1990–2023")
plt.xlabel("Year")
plt.ylabel("Homicides per 100,000 people")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()


us_homicide = df_nibrs[
    df_nibrs["indicator_name"].eq(
        "Murder and Non-negligent Manslaughter"
    )
].copy()

print("Rows:", len(us_homicide))

print("\nEstimate types:")
print(us_homicide["estimate_type"].value_counts())

print("\nGeographic locations:")
print(
    us_homicide["estimate_geographic_location"]
    .value_counts()
    .head(10)
)

print("\nRate records:")
print(
    us_homicide.loc[
        us_homicide["estimate_type"].eq("rate"),
        [
            "time_series_start_year",
            "estimate",
            "estimate_domain_1",
            "estimate_domain_2",
            "population_estimate",
            "agency_counts"
        ]
    ].head(15).to_string(index=False)
)


# 1. Prepare Australia's homicide-rate data
df_aus_join = df_australia[
    ["Year", "Indicator_Value"]
].copy()

df_aus_join = df_aus_join.rename(columns={
    "Indicator_Value": "Australia_Homicide_Rate"
})

# Keep only years overlapping with the US data
df_aus_join = df_aus_join[
    df_aus_join["Year"].isin([2022, 2023])
]

# 2. Prepare US NIBRS homicide-rate data
df_us_join = df_nibrs[
    (
        df_nibrs["indicator_name"]
        == "Murder and Non-negligent Manslaughter"
    )
    & (df_nibrs["estimate_type"] == "rate")
    & (
        df_nibrs["estimate_domain_1"]
        == "Offense rate (per 100k total pop)"
    )
].copy()

df_us_join["Year"] = pd.to_numeric(
    df_us_join["time_series_start_year"],
    errors="coerce"
)

df_us_join["estimate"] = pd.to_numeric(
    df_us_join["estimate"],
    errors="coerce"
)

df_us_join = df_us_join.rename(columns={
    "estimate": "US_NIBRS_Offense_Rate"
})

df_us_join = df_us_join[
    [
        "Year",
        "US_NIBRS_Offense_Rate",
        "population_estimate",
        "agency_counts"
    ]
]

df_us_join = df_us_join.dropna(
    subset=["Year", "US_NIBRS_Offense_Rate"]
)

df_us_join["Year"] = df_us_join["Year"].astype(int)

# 3. Check for duplicate years before joining
if df_aus_join["Year"].duplicated().any():
    raise ValueError("Australia has duplicate years.")

if df_us_join["Year"].duplicated().any():
    raise ValueError("US NIBRS has duplicate years.")

# 4. Join on Year
df_comparison = pd.merge(
    df_aus_join,
    df_us_join,
    on="Year",
    how="inner",
    validate="one_to_one"
)

# 5. Inspect the joined dataset
print("Joined dataset:")
print(df_comparison.to_string(index=False))

print("\nDataset shape:", df_comparison.shape)
