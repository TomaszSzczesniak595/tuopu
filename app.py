
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Ustawienia strony
st.set_page_config(layout="wide", page_title="Dashboard jakościowy")

# Styl (ciemny/jasny)
theme = st.sidebar.radio("🎨 Wybierz motyw", ["Jasny", "Ciemny"])
if theme == "Ciemny":
    st.markdown("<style>body { background-color: #1e1e1e; color: white; }</style>", unsafe_allow_html=True)

# Wczytanie danych
df = pd.read_excel("Statystyki bez zastrzeżeń (6).xlsx", sheet_name="SheetJS")
df["Czas działania"] = pd.to_datetime(df["Czas działania"])

# Sidebar - filtry
st.sidebar.header("🔍 Filtry")
start_date = st.sidebar.date_input("Data początkowa", df["Czas działania"].min().date())
end_date = st.sidebar.date_input("Data końcowa", df["Czas działania"].max().date())
operators = st.sidebar.multiselect("Operatorzy", df["Operator"].unique(), default=list(df["Operator"].unique()))
locations = st.sidebar.multiselect("Lokalizacje wad (wady1)", df["Lokalizacja wady1"].dropna().unique())

# Filtrowanie danych
filtered_df = df[
    (df["Czas działania"].dt.date >= start_date) &
    (df["Czas działania"].dt.date <= end_date) &
    (df["Operator"].isin(operators))
]
if locations:
    filtered_df = filtered_df[filtered_df["Lokalizacja wady1"].isin(locations)]

# Statystyki
total = filtered_df.shape[0]
defects = filtered_df[filtered_df["Typ wady1"] != "-"]
defect_count = defects.shape[0]
fpy = ((total - defect_count) / total) * 100 if total > 0 else 0

# Statystyki wyświetlane
st.markdown("## 📊 Dashboard jakościowy")
col1, col2, col3 = st.columns(3)
col1.metric("📄 Łączna liczba testów", total)
col2.metric("❌ Liczba wad (Typ wady1)", defect_count)
col3.metric("✅ FPY", f"{fpy:.2f}%")

# Wykres trendu FPY
st.subheader("📈 Trend FPY w czasie")
fpy_trend = filtered_df.copy()
fpy_trend["Data"] = fpy_trend["Czas działania"].dt.date
fpy_daily = fpy_trend.groupby("Data").apply(lambda x: ((x.shape[0] - (x["Typ wady1"] != "-").sum()) / x.shape[0]) * 100).reset_index(name="FPY")
st.line_chart(fpy_daily.set_index("Data"))

# Wykres liczby wad w czasie
st.subheader("📉 Liczba wad dziennie")
defects_by_day = defects.copy()
defects_by_day["Data"] = defects_by_day["Czas działania"].dt.date
daily_defects = defects_by_day.groupby("Data").size()
st.bar_chart(daily_defects)

# Top 10 typów wad
st.subheader("📌 Top 10 najczęstszych typów wad (Typ wady1)")
top_defects = filtered_df["Typ wady1"].value_counts()
top_defects = top_defects[top_defects.index != '-'].head(10)
st.bar_chart(top_defects)

# Pareto Chart
st.subheader("📊 Pareto - Typy wad (Typ wady1)")
pareto_data = filtered_df["Typ wady1"].value_counts()
pareto_data = pareto_data[pareto_data.index != '-']
pareto_df = pd.DataFrame({
    "Wady": pareto_data.index,
    "Liczba": pareto_data.values,
    "Kumulatywny %": pareto_data.cumsum() / pareto_data.sum() * 100
})
fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()
ax1.bar(pareto_df["Wady"], pareto_df["Liczba"], color="skyblue")
ax2.plot(pareto_df["Wady"], pareto_df["Kumulatywny %"], color="red", marker="o")
ax1.set_ylabel("Liczba")
ax2.set_ylabel("Kumulatywny %")
ax2.set_ylim(0, 110)
plt.xticks(rotation=45, ha='right')
st.pyplot(fig)

# Najczęstsze lokalizacje wad
st.subheader("📍 Najczęstsze lokalizacje wad")
loc_counts = filtered_df["Lokalizacja wady1"].value_counts().head(10)
st.bar_chart(loc_counts)

# Eksport
st.subheader("📤 Eksport danych")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Pobierz dane (CSV)", data=csv, file_name="filtrowane_dane.csv", mime='text/csv')

# Dane surowe
with st.expander("🔎 Podgląd danych"):
    st.dataframe(filtered_df)
