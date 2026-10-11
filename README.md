US Homicide Data Analysis Using Python and Streamlit
Project Overview

This project explores homicide related data from the United States using Python and interactive data visualizations. It demonstrates a practical data analysis workflow, from retrieving data through an API to cleaning, filtering, aggregating, and visualizing crime estimates.
The application is built with Streamlit, allowing users to explore the available data and examine yearly patterns in murder and non-negligent manslaughter estimates.

Research Background

Homicide is a serious public safety concern. Analysing homicide-related data can help researchers, law enforcement agencies, and policymakers better understand crime patterns and identify areas that may require further investigation.

This project uses publicly accessible data from the US Department of Justice's Office of Justice Programs to demonstrate how data analysis techniques can be applied to crime-related information.

Research Question

How do estimates of murder and non-negligent manslaughter change over the years represented in the dataset?

Research Hypotheses
Null hypothesis (H₀): There is no statistically significant change in homicide estimates over the period examined.
Alternative hypothesis (H₁): There is a statistically significant change in homicide estimates over the period examined.

The current application uses descriptive analysis and visualizations to explore patterns over time. A suitable statistical test would be needed to determine whether any observed changes are statistically significant.

Data Source

The project retrieves data from the US Department of Justice's Office of Justice Programs API.

API endpoint:
https://api.ojp.gov/bjsdataset/v1/x3sz-eb6y.json?$limit=10000

The dataset contains indicator-based estimates, including the indicator Murder and Non-negligent Manslaughter. The project also references the National Incident-Based Reporting System (NIBRS), which collects detailed information about crime incidents reported by participating law enforcement agencies.

Official NIBRS information:
https://bjs.ojp.gov/data-collection/national-incident-based-reporting-system-nibrs

The analysis is limited to the records and variables returned by the selected API endpoint. The dataset's coverage, definitions, and estimate types should be considered when interpreting results.

Tools and Technologies
Python — programming and data processing
Requests — retrieving data from the API
Pandas — data cleaning, filtering, grouping, and aggregation
Plotly Express — interactive charts
Streamlit — interactive data application
Git and GitHub — version control and project hosting

Data Analysis Workflow
Data collection: Retrieve JSON data from the Department of Justice API using Requests.
Data exploration: Convert the response into a pandas DataFrame and inspect the returned records.
Data cleaning: Select relevant columns and convert numeric fields into appropriate data types.
Indicator analysis: Identify available crime indicators and examine their record counts.
Homicide filtering: Select records classified as murder and non-negligent manslaughter.
Data preparation: Convert estimates to numeric values and remove rows with missing estimates.
Yearly aggregation: Group the available homicide estimates by year.
Visualization: Use Plotly to display yearly estimates in bar and scatter charts.
Interpretation: Examine patterns while considering data limitations and the research question.
Visualizations

The application currently includes:

A bar chart showing murder and non-negligent manslaughter estimates by year.
A scatter plot showing the distribution of yearly estimates.
Data tables displaying the retrieved records, cleaned data, indicator counts, and filtered homicide records.

These visualizations support exploratory analysis. They do not, on their own, establish causation or statistical significance.

Installation and Setup
Prerequisites

Install Python and Git on your computer.

1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd aus_homicides

Replace <YOUR_GITHUB_REPOSITORY_URL> with your repository's actual GitHub URL.

2. Create a virtual environment

On Windows:

python -m venv .venv

Activate it in Git Bash:

source .venv/Scripts/activate
3. Install the dependencies
python -m pip install streamlit requests pandas plotly
4. Run the application
streamlit run homicid_strml.py

Streamlit will provide a local URL where you can open the application in your browser.

Limitations
The analysis is restricted to the records returned by the selected API endpoint.
The available data may not represent every homicide in the United States.
The meaning of each estimate and its reporting coverage must be verified before interpreting totals.
Summing estimates across records may be inappropriate if records represent overlapping groups or different estimate categories.
Missing observations and changes in reporting coverage can affect comparisons over time.
Statistical significance cannot be established from charts alone.
Future Improvements
Add statistical tests appropriate to the structure and meaning of the data.
Improve data validation and handling of API errors.
Add filters for years and available estimate categories.
Include trend lines and additional exploratory visualizations.
Add automated tests and a reproducible dependency file.
Deploy the application online so other users can interact with the analysis.
Conclusion

This project demonstrates the application of Python based data analysis to publicly accessible US crime data. It combines API integration, data cleaning, exploratory analysis, and interactive visualization in a Streamlit application.

The project also provides a foundation for further research into homicide trends, with conclusions to be guided by the data definitions, appropriate statistical methods, and limitations of the available records.

Author

Data Analysis Project

Developed as a practical project to strengthen skills in Python, data cleaning, exploratory data analysis, visualization, and communicating analytical findings.