import streamlit as st
import pandas as pd
import plotly.express as px

st.title('Pokemon')

@st.cache
def load_data():
    return pd.read_csv("data/Pokemon_Gen_1-8.csv"), pd.read_csv("data/chart.csv")

with st.spinner('Loading data...'):
    pokemons, types = load_data()


placeholder = "Select task..."
tasks = ["Visualize", "Find Best Pokemon for combat"]
task = st.sidebar.selectbox(f"Tasks ({len(tasks)})", [placeholder] + tasks)

DEFAULT_PLOTLY_COLORS=['rgb(31, 119, 180)', 'rgb(255, 127, 14)',
                       'rgb(44, 160, 44)', 'rgb(214, 39, 40)',
                       'rgb(148, 103, 189)', 'rgb(140, 86, 75)',
                       'rgb(227, 119, 194)', 'rgb(127, 127, 127)',
                       'rgb(188, 189, 34)', 'rgb(23, 190, 207)',
                       'lightgreen', 'lightseagreen', 'lightsteelblue', 'lime']

if task == "Visualize":
    for i, c in enumerate(pokemons.drop(["#", "Name"], axis=1).columns.values):
        st.text(c)
        if c in ["Type 1", "Type 2"]:
            fig = px.histogram(pokemons, x=c, color="Generation")
        else:
            fig = px.histogram(pokemons, x=c, color_discrete_sequence=[DEFAULT_PLOTLY_COLORS[i]])
        st.plotly_chart(fig)
elif task == "Find Best Pokemon for combat":
    selected = st.multiselect(
        'What pokemons are in your team ?',
        pokemons.Name
    )
    if len(selected) > 6:
        st.error("your team cannot exceed 6")
    team = pokemons[pokemons.Name.isin(selected)]
    team_types = list(set(team["Type 1"].values).union(set(team["Type 2"].dropna().values)))
    st.write(f"Your team has types...")
    st.write(team_types)

    opponent = st.selectbox(
        'Who are you fighting against ?',
        pokemons.Name
    )
    opponent_type_1 = pokemons[pokemons.Name == opponent]["Type 1"]
    opponent_weaknesses_type_1 = types[opponent_type_1].values
    opponent_type_2 = pokemons[pokemons.Name == opponent]["Type 2"]
    if len(opponent_type_2.dropna()) > 0:
        st.write(f"{opponent} is of type {opponent_type_1.values[0]} and {opponent_type_2.values[0]}. His weaknesses are...")
        opponent_weaknesses_type_2 = types[opponent_type_2].values
        weaknesses_power = list(map(lambda x,y: float(x*y), opponent_weaknesses_type_1, opponent_weaknesses_type_2))
    else:
        st.write(f"{opponent} is of type {opponent_type_1.values[0]}. His weaknesses are...")
        weaknesses_power = list(opponent_weaknesses_type_1)

    weaknesses = pd.DataFrame(data={"Attacking Type": types.Attacking, "Weakness": weaknesses_power})
    sweet_spot = weaknesses.sort_values(by="Weakness", ascending=False)[weaknesses.Weakness > 1]["Attacking Type"]

    st.write(list(sweet_spot.values))

    if len(set(team["Type 1"]).union(set(team["Type 2"])).intersection(set(sweet_spot))) > 0:
        chosen = set()
        preference = []
        for typ in sweet_spot:
            for row in team[(team["Type 1"] == typ) | (team["Type 2"] == typ)].sort_values(by="Total", ascending=False).itertuples():
                if row.Name in chosen:
                    continue
                chosen.add(row.Name)
                preference.append(row.Name)
        st.write("Use in preference...")
        st.write(preference)
    else:
        st.warning("No best choice in your team. Fly you fool!")

