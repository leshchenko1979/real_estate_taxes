import streamlit as st
import pandas as pd

st.set_page_config(page_title="Расчет налогов при флиппинге / редевелопменте")

st.header("Расчет налогов при флиппинге / редевелопменте")
st.caption(
    "Простой калькулятор для расчета оптимального варианта налогообложения по сделкам флиппинга / редевелопмента."
)

st.subheader("Параметры проекта")
st.caption(
    "Укажите цену покупки объекта, расходы, долю подтвержденных расходов и цену продажи объекта."
)

col1, col2, col3 = st.columns(3)
with col1:
    purchase = st.number_input("Цена покупки", min_value=7_000_000, step=100_000)
with col2:
    expenses = st.number_input("Расходы", value=1_000_000, step=100_000)
    confirmed_share = st.slider(
        "Процент расходов, подтвержденный чеками", value=50, max_value=100, step=10
    )
with col3:
    sale = st.number_input("Продажа", min_value=10_000_000, step=100_000)

if sale < purchase + expenses:
    st.error("Стоимость продажи должна быть больше суммы покупки и расходов")
    st.stop()

st.caption(
    f"Наценка: {sale / purchase * 100 :.0f}%, маржинальность: {(purchase + expenses) / sale * 100 :.0f}%."
)

regimes = {
    "НДФЛ вторичка": {
        "base": sale - purchase,
        "default_rate": 13,
    },
    "НДФЛ первичка": {
        "base": sale - purchase - expenses * confirmed_share / 100,
        "default_rate": 13,
    },
    "УСН доходы минус расходы": {
        "base": sale - purchase - expenses * confirmed_share / 100,
        "default_rate": 15,
    },
    "УСН доходы": {
        "base": sale,
        "default_rate": 6,
    },
}

st.subheader("Ставки налогов")
st.caption("Введите ставки УСН для вашего региона.")

for regime_name, regime in regimes.items():
    USN = regime_name.find("УСН") >= 0
    regime["rate"] = (
        st.slider(regime_name, value=regime["default_rate"], min_value=0, max_value=20)
        if USN
        else regime["default_rate"]
    )
    regime["tax"] = regime["base"] * regime["rate"] / 100 + sale * (0.01 if USN else 0)
    regime["profit"] = sale - purchase - expenses - regime["tax"]

st.subheader("Расчет налогов и чистой прибыли")


df: pd.DataFrame = (
    pd.DataFrame(regimes)
    .T.drop(columns={"default_rate"})
    .astype("int")
    .rename(
        columns={
            "base": "Налоговая база",
            "rate": "Ставка налога",
            "tax": "Налог*",
            "profit": "Чистая прибыль",
        }
    )
)


st.dataframe(df.style.format(thousands=" "), use_container_width=True)
st.caption("*Рачет налога на УСН включает 1% социальных взносов.")
st.bar_chart(df, y="Налог*", use_container_width=True)


st.write('Еще больше полезного на канале "Инвестиции в редевелопмент": https://t.me/flipping_invest')
