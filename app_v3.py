
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AbroadWise | University Planner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Approximate exchange rates in INR
CURRENCY_RATES = {
    "EUR": 108.86,
    "GBP": 127.43,
    "USD": 96.38,
    "CAD": 67.66,
    "AUD": 68.90,
    "NZD": 59.50,
    "SEK": 10.20,
    "DKK": 14.55,
    "JPY": 0.67,
    "KRW": 0.069,
    "INR": 1.0
}

# ---------------- DESIGN ----------------

st.markdown("""
<style>
    .stApp {
        background-color: #F4F7FB;
        color: #172B4D;
    }

    [data-testid="stSidebar"] {
        background-color: #102A43;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    .hero {
        background: linear-gradient(120deg, #102A43, #176B87);
        padding: 30px;
        border-radius: 18px;
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        color: white;
        margin-bottom: 5px;
        font-size: 36px;
    }

    .hero p {
        color: #D9F3F5;
        font-size: 16px;
    }

    .section-heading {
        color: #102A43;
        font-size: 23px;
        font-weight: 700;
        margin-top: 24px;
        margin-bottom: 12px;
    }

    .metric-card {
        background: white;
        border: 1px solid #E0E7EF;
        border-radius: 14px;
        padding: 20px;
        min-height: 115px;
        box-shadow: 0 3px 12px rgba(16, 42, 67, 0.05);
    }

    .metric-label {
        color: #627D98;
        font-size: 14px;
        margin-bottom: 9px;
    }

    .metric-value {
        color: #102A43;
        font-size: 23px;
        font-weight: 700;
        overflow-wrap: anywhere;
    }

    .small-note {
        color: #627D98;
        font-size: 13px;
    }

    div.stButton > button {
        background-color: #087E8B;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 22px;
        font-weight: 600;
        width: 100%;
    }

    div.stButton > button:hover {
        background-color: #06636D;
        color: white;
        border: none;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #E0E7EF;
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)


def to_number(value):
    return pd.to_numeric(value, errors="coerce")


def calculate_tuition(tuition, tuition_type, duration):
    tuition_type = str(tuition_type).strip().lower()

    total_types = [
        "total programme",
        "total program",
        "full programme",
        "full program",
        "total course",
        "entire programme",
        "entire program"
    ]

    if any(word in tuition_type for word in total_types):
        return tuition

    return tuition * duration


def calculate_university_cost(row, travel, scholarship):
    currency = str(row["Currency"]).strip().upper()

    if currency not in CURRENCY_RATES:
        return None

    tuition = to_number(row["Tuition_Amount"])
    living = to_number(row["Living_Cost_Per_Year"])
    visa = to_number(row["Visa_Fee"])
    application = to_number(row["Application_Fee"])
    duration = to_number(row["Duration_Years"])

    values = [tuition, living, visa, application, duration]

    if any(pd.isna(value) for value in values):
        return None

    if duration <= 0 or min(tuition, living, visa, application) < 0:
        return None

    rate = CURRENCY_RATES[currency]

    tuition_inr = calculate_tuition(
        tuition, row["Tuition_Type"], duration
    ) * rate

    living_inr = living * duration * rate
    visa_inr = visa * rate
    application_inr = application * rate

    total_before_scholarship = (
        tuition_inr + living_inr + visa_inr
        + application_inr + travel
    )

    final_cost = max(0, total_before_scholarship - scholarship)

    return {
        "Country": str(row["Country"]),
        "University": str(row["University"]),
        "Programme": str(row["Programme"]),
        "Duration (years)": float(duration),
        "Tuition (INR)": round(tuition_inr),
        "Living cost (INR)": round(living_inr),
        "Visa fee (INR)": round(visa_inr),
        "Application fee (INR)": round(application_inr),
        "Travel (INR)": round(travel),
        "Scholarship (INR)": round(scholarship),
        "Estimated total (INR)": round(final_cost),
        "Source": str(row["Source"])
    }


def money(value):
    return f"₹{value:,.0f}"


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.markdown("# 🎓 AbroadWise")
    st.caption("YOUR STUDY ABROAD PLANNER")
    st.divider()

    st.markdown("### 🌍 Plan smarter")
    st.write(
        "Compare university costs, explore your budget, "
        "and make informed study-abroad decisions."
    )

    st.divider()
    st.markdown("**Features**")
    st.write("📚 University comparison")
    st.write("💰 Budget planning")
    st.write("📊 Cost breakdown")
    st.write("🎯 Affordability check")

    st.divider()
    st.caption("Estimates only. Verify costs with official sources.")


# ---------------- LOAD DATA ----------------

st.markdown("""
<div class="hero">
    <h1>Plan your future abroad ✈️</h1>
    <p>Compare universities. Understand the costs. Plan with confidence.</p>
</div>
""", unsafe_allow_html=True)

try:
    df = pd.read_csv("countries.csv")
except FileNotFoundError:
    st.error("countries.csv was not found in this project folder.")
    st.stop()

required_columns = [
    "Country", "University", "Programme", "Currency",
    "Duration_Years", "Tuition_Type", "Tuition_Amount",
    "Living_Cost_Per_Year", "Visa_Fee", "Application_Fee", "Source"
]

missing = [column for column in required_columns if column not in df.columns]

if missing:
    st.error("Missing CSV columns: " + ", ".join(missing))
    st.stop()

countries = sorted(df["Country"].dropna().astype(str).unique())

if len(countries) == 0:
    st.error("No countries were found in your dataset.")
    st.stop()


# ---------------- INPUTS ----------------


# ---------------- INPUTS ----------------

st.markdown(
    '<div class="section-heading">🌍 Compare universities worldwide</div>',
    unsafe_allow_html=True
)

countries = sorted(df["Country"].dropna().astype(str).unique())

selected_rows = []
slot_columns = st.columns(3)

for slot, column in enumerate(slot_columns, start=1):
    with column:
        st.markdown(f"#### University {slot}")

        chosen_country = st.selectbox(
            f"Country {slot}",
            countries,
            key=f"compare_country_{slot}"
        )

        options_df = df[
            df["Country"].astype(str) == chosen_country
        ].dropna(subset=["University", "Programme"]).copy()

        options_df["_label"] = (
            options_df["University"].astype(str)
            + " — "
            + options_df["Programme"].astype(str)
        )

        options_df = options_df.drop_duplicates(
            subset=["University", "Programme"]
        )

        labels = options_df["_label"].tolist()
        choices = ["— Skip this university —"] + labels

        chosen_label = st.selectbox(
            f"University and programme {slot}",
            choices,
            key=f"compare_university_{slot}"
        )

        if chosen_label != "— Skip this university —":
            chosen_row = options_df[
                options_df["_label"] == chosen_label
            ].iloc[0]

            selected_rows.append(
                (chosen_label, chosen_row)
            )

st.markdown(
    '<div class="section-heading">💰 Your budget plan</div>',
    unsafe_allow_html=True
)

budget_col, travel_col, scholarship_col = st.columns(3)

with budget_col:
    budget = st.number_input(
        "Total budget (INR)",
        min_value=0,
        value=1500000,
        step=50000
    )

with travel_col:
    travel = st.number_input(
        "Travel cost per university (INR)",
        min_value=0,
        value=50000,
        step=5000
    )

with scholarship_col:
    scholarship = st.number_input(
        "Scholarship per university (INR)",
        min_value=0,
        value=0,
        step=10000
    )

st.caption(
    "Travel and scholarship values are applied equally to each option. "
    "Exchange rates are approximate, not live."
)

compare_clicked = st.button(
    "✨ Compare Universities",
    use_container_width=True
)




# ---------------- RESULTS ----------------


# ---------------- RESULTS ----------------

if compare_clicked:
    if len(selected_rows) < 2:
        st.warning("Please select at least two universities.")
    else:
        results = []

        for label, row in selected_rows:
            result = calculate_university_cost(
                row, travel, scholarship
            )

            if result is None:
                st.warning(
                    f"Unable to calculate costs for {label}. "
                    "Please check the data in countries.csv."
                )
            else:
                result["University"] = str(row["University"])
                result["Programme"] = str(row["Programme"])
                result["Country"] = str(row["Country"])
                results.append(result)

        if results:
            results_df = pd.DataFrame(results)

            st.download_button(
                label="📥 Download Comparison Report",
                data=results_df.to_csv(index=False).encode("utf-8"),
                file_name="abroadwise_comparison.csv",
                mime="text/csv"
            )

            st.divider()
            st.markdown(
                '<div class="section-heading">📊 Your comparison</div>',
                unsafe_allow_html=True
            )

            cheapest = results_df.loc[
                results_df["Estimated total (INR)"].idxmin()
            ]

            c1, c2, c3 = st.columns(3)

            with c1:
                metric_card(
                    "Universities compared",
                    str(len(results_df))
                )

            with c2:
                metric_card(
                    "Lowest estimated cost",
                    money(cheapest["Estimated total (INR)"])
                )

            with c3:
                within_budget = sum(
                    results_df["Estimated total (INR)"] <= budget
                )
                metric_card(
                    "Within your budget",
                    f"{within_budget} of {len(results_df)}"
                )

            st.markdown(
                '<div class="section-heading">📋 Cost comparison</div>',
                unsafe_allow_html=True
            )

            display_columns = [
                "Country",
                "University",
                "Programme",
                "Duration (years)",
                "Tuition (INR)",
                "Living cost (INR)",
                "Visa fee (INR)",
                "Application fee (INR)",
                "Travel (INR)",
                "Scholarship (INR)",
                "Estimated total (INR)"
            ]

            st.dataframe(
                results_df[display_columns],
                use_container_width=True,
                hide_index=True
            )

            st.markdown(
                '<div class="section-heading">📈 Compare total costs</div>',
                unsafe_allow_html=True
            )

            chart_df = results_df[
                ["University", "Estimated total (INR)"]
            ].copy()

            chart_df["University"] = (
                chart_df["University"] + " (" +
                results_df["Country"] + ")"
            )

            st.bar_chart(
                chart_df.set_index("University")
            )

            st.markdown(
                '<div class="section-heading">🎯 Budget check</div>',
                unsafe_allow_html=True
            )

            for result in results:
                name = (
                    result["University"] + " — " +
                    result["Country"]
                )
                total = result["Estimated total (INR)"]
                difference = budget - total

                with st.container(border=True):
                    st.markdown(f"#### 🏛️ {name}")
                    st.write(f"Estimated total: **{money(total)}**")

                    if difference >= 0:
                        st.success(
                            f"Within budget — {money(difference)} remaining."
                        )
                    else:
                        st.warning(
                            f"Over budget by {money(-difference)}."
                        )

            st.markdown(
                '<div class="section-heading">🧾 Expense breakdown</div>',
                unsafe_allow_html=True
            )

            result_labels = [
                f'{r["University"]} — {r["Country"]}'
                for r in results
            ]

            chosen = st.selectbox(
                "Choose a university to inspect",
                result_labels,
                key="breakdown_university"
            )

            selected_result = results[result_labels.index(chosen)]

            expense_items = [
                ("Tuition", selected_result["Tuition (INR)"]),
                ("Living cost", selected_result["Living cost (INR)"]),
                ("Visa fee", selected_result["Visa fee (INR)"]),
                ("Application fee", selected_result["Application fee (INR)"]),
                ("Travel", selected_result["Travel (INR)"])
            ]

            expense_df = pd.DataFrame(
                expense_items,
                columns=["Expense", "Amount (INR)"]
            )

            st.bar_chart(expense_df.set_index("Expense"))

            with st.expander("📌 Data sources and assumptions"):
                st.write("Dataset source for each option:")
                for result in results:
                    st.write(
                        f'{result["University"]} ({result["Country"]}): '
                        f'{result["Source"]}'
                    )

                st.write(
                    "Tuition totals depend on the Tuition_Type field "
                    "in countries.csv."
                )
                st.write(
                    "Living costs are estimated per year and multiplied "
                    "by course duration."
                )
                st.write(
                    "Verify fees, exchange rates, and scholarship "
                    "eligibility using official sources."
                )

            st.caption(
                "AbroadWise provides planning estimates, not official "
                "university quotations."
            )

else:
    st.info(
        "Choose at least two universities, even from different countries, "
        "and click 'Compare Universities'."
    )
