import streamlit as st
import pandas as pd
from datetime import datetime

if "unlocked_days" not in st.session_state:
    st.session_state.unlocked_days = set()

if "unlocked_all" not in st.session_state:
    st.session_state.unlocked_all = False

params = st.query_params

# only load ONCE
if "loaded_from_url" not in st.session_state:

    if "days" in params:
        days_param = params["days"]

        if isinstance(days_param, list):
            days_param = days_param[0]

        st.session_state.unlocked_days = set(map(int, days_param.split(",")))

    if "all" in params:
        st.session_state.unlocked_all = params["all"] == "1"

    st.session_state.loaded_from_url = True

# --------------------------------------------------
# 1. BASE DAILY RULE DATA
# --------------------------------------------------

data = [
    {
        "day": "Monday",
        "element": "Water",
        "wear_colors": ["black", "navy", "deep blue"],
        "avoid_colors": ["red", "orange"],
        "primary_stone": "obsidian",
        "primary_jewelry_type": "bracelet",
        "support_stone_1": "moonstone",
        "support_jewelry_type_1": "necklace",
        "support_stone_2": "hematite",
        "support_jewelry_type_2": "bracelet",
        "favored_metals": ["silver"],
        "avoid_metals": ["gold"],
        "daily_theme": "Intuition and grounding",
        "explanation": "Water energy supports introspection and emotional clarity. Favor grounding stones and calming tones."
    },
    {
        "day": "Tuesday",
        "element": "Fire",
        "wear_colors": ["red", "burgundy"],
        "avoid_colors": ["black", "blue"],
        "primary_stone": "garnet",
        "primary_jewelry_type": "necklace",
        "support_stone_1": "citrine",
        "support_jewelry_type_1": "bracelet",
        "support_stone_2": "carnelian",
        "support_jewelry_type_2": "earrings",
        "favored_metals": ["gold"],
        "avoid_metals": ["silver"],
        "daily_theme": "Action and confidence",
        "explanation": "Fire energy boosts courage and movement. Ideal for decision-making and leadership."
    },
    {
        "day": "Wednesday",
        "element": "Wood",
        "wear_colors": ["green", "teal"],
        "avoid_colors": ["white", "gray"],
        "primary_stone": "jade",
        "primary_jewelry_type": "bracelet",
        "support_stone_1": "aventurine",
        "support_jewelry_type_1": "necklace",
        "support_stone_2": "peridot",
        "support_jewelry_type_2": "earrings",
        "favored_metals": ["silver"],
        "avoid_metals": ["heavy gold"],
        "daily_theme": "Growth and expansion",
        "explanation": "Wood energy supports growth, creativity, and forward movement."
    },
    {
        "day": "Thursday",
        "element": "Wood",
        "wear_colors": ["emerald", "green"],
        "avoid_colors": ["black"],
        "primary_stone": "emerald",
        "primary_jewelry_type": "necklace",
        "support_stone_1": "jade",
        "support_jewelry_type_1": "bracelet",
        "support_stone_2": "malachite",
        "support_jewelry_type_2": "earrings",
        "favored_metals": ["gold"],
        "avoid_metals": ["silver"],
        "daily_theme": "Expansion and influence",
        "explanation": "Strong growth energy, ideal for communication and influence."
    },
    {
        "day": "Friday",
        "element": "Metal",
        "wear_colors": ["white", "gold"],
        "avoid_colors": ["green"],
        "primary_stone": "diamond",
        "primary_jewelry_type": "necklace",
        "support_stone_1": "clear quartz",
        "support_jewelry_type_1": "bracelet",
        "support_stone_2": "pyrite",
        "support_jewelry_type_2": "earrings",
        "favored_metals": ["gold"],
        "avoid_metals": ["wood materials"],
        "daily_theme": "Refinement and attraction",
        "explanation": "Metal energy enhances clarity, beauty, and attraction."
    },
    {
        "day": "Saturday",
        "element": "Earth",
        "wear_colors": ["brown", "beige", "earth tones"],
        "avoid_colors": ["neon colors"],
        "primary_stone": "smoky quartz",
        "primary_jewelry_type": "bracelet",
        "support_stone_1": "jasper",
        "support_jewelry_type_1": "necklace",
        "support_stone_2": "onyx",
        "support_jewelry_type_2": "ring",
        "favored_metals": ["bronze"],
        "avoid_metals": ["silver"],
        "daily_theme": "Stability and grounding",
        "explanation": "Earth energy supports restoration, balance, and physical grounding."
    },
    {
        "day": "Sunday",
        "element": "Fire",
        "wear_colors": ["gold", "orange", "warm tones"],
        "avoid_colors": ["dark gray"],
        "primary_stone": "sunstone",
        "primary_jewelry_type": "necklace",
        "support_stone_1": "amber",
        "support_jewelry_type_1": "bracelet",
        "support_stone_2": "citrine",
        "support_jewelry_type_2": "earrings",
        "favored_metals": ["gold"],
        "avoid_metals": ["heavy metals"],
        "daily_theme": "Vitality and expression",
        "explanation": "Fire energy enhances visibility, joy, and outward expression."
    }
]

df_rules = pd.DataFrame(data)

# --------------------------------------------------
# 2. PROFILE LOGIC
# --------------------------------------------------

def get_birth_year_group(birth_year: int) -> str:
    if birth_year <= 1979:
        return "grounding"
    elif birth_year <= 1989:
        return "growth"
    else:
        return "expression"

def get_cycle_modifier(cycle_toggle: bool) -> dict:
    if cycle_toggle:
        return {
            "theme_addon": "Restoration and energetic conservation",
            "avoid_extra": ["bright red"],
            "favor_extra_stone": "moonstone",
            "favor_extra_jewelry": "bracelet"
        }
    return {
        "theme_addon": "",
        "avoid_extra": [],
        "favor_extra_stone": None,
        "favor_extra_jewelry": None
    }

def generate_daily_card(profile: dict, rules_df: pd.DataFrame, date_value=None) -> dict:
    if date_value is None:
        today_name = datetime.now().strftime("%A")
        today_date = datetime.now().strftime("%Y-%m-%d")
    else:
        dt = pd.to_datetime(date_value)
        today_name = dt.strftime("%A")
        today_date = dt.strftime("%Y-%m-%d")

    match = rules_df[rules_df["day"] == today_name]

    if match.empty:
        raise ValueError(f"No rule found for day: {today_name}")

    row = match.iloc[0].to_dict()

    birth_group = get_birth_year_group(profile["birth_year"])
    cycle_mod = get_cycle_modifier(profile["cycle_toggle"])

    wear_colors = list(row["wear_colors"])
    avoid_colors = list(row["avoid_colors"]) + cycle_mod["avoid_extra"]

    support_stones = [
        {
            "stone": row["support_stone_1"],
            "jewelry_type": row["support_jewelry_type_1"]
        },
        {
            "stone": row["support_stone_2"],
            "jewelry_type": row["support_jewelry_type_2"]
        }
    ]

    if cycle_mod["favor_extra_stone"]:
        support_stones.append({
            "stone": cycle_mod["favor_extra_stone"],
            "jewelry_type": cycle_mod["favor_extra_jewelry"]
        })

    if birth_group == "grounding":
        wear_colors = wear_colors + ["earth brown"]
    elif birth_group == "growth":
        wear_colors = wear_colors + ["soft green"]
    else:
        wear_colors = wear_colors + ["lavender"]

    wear_colors = wear_colors[:3]
    avoid_colors = avoid_colors[:2]

    theme = row["daily_theme"]
    if cycle_mod["theme_addon"]:
        theme = f"{theme} + {cycle_mod['theme_addon']}"

    explanation = (
        f"{row['explanation']} "
        f"For this profile, the birth-year group is '{birth_group}', which shifts the recommendation emphasis. "
        f"Current location bucket: {profile['current_location_bucket']}."
    )

    return {
        "name": profile["name"],
        "date": today_date,
        "day": today_name,
        "birth_year_group": birth_group,
        "wear_colors": wear_colors,
        "avoid_colors": avoid_colors,
        "primary_stone": row["primary_stone"],
        "primary_jewelry_type": row["primary_jewelry_type"],
        "support_stones": support_stones,
        "favored_metals": row["favored_metals"],
        "avoid_metals": row["avoid_metals"],
        "daily_theme": theme,
        "explanation": explanation
    }

def generate_weekly_cards(profile, rules_df):
    today = datetime.now()
    weekly_cards = []

    for i in range(7):
        day_date = today + pd.Timedelta(days=i)
        card = generate_daily_card(profile, rules_df, date_value=day_date)
        card["locked"] = i >= 7  # placeholder for future paid gating
        weekly_cards.append(card)

    return weekly_cards

# --------------------------------------------------
# 3. STREAMLIT UI
# --------------------------------------------------

st.set_page_config(page_title="Belle App V1", layout="centered")

st.title("Belle App V1")
st.subheader("Ancient wisdom, modern structure")

name = st.text_input("What would you like to be called?", value="Elizabeth")
birth_year = st.number_input("Birth year", min_value=1900, max_value=2100, value=1977, step=1)

birth_location_bucket = st.selectbox(
    "Birth location (rough)",
    ["south_us_north_mexico", "mexico_city", "northern_mexico", "southern_mexico", "us_general"]
)

current_location_bucket = st.selectbox(
    "Current location (rough)",
    ["mexico_city", "south_us_north_mexico", "northern_mexico", "southern_mexico", "us_general"]
)

cycle_toggle = st.toggle("Monthly cycle / lower-energy mode", value=False)

user_profile = {
    "name": name,
    "birth_year": int(birth_year),
    "birth_location_bucket": birth_location_bucket,
    "current_location_bucket": current_location_bucket,
    "cycle_toggle": cycle_toggle
}

# INIT
if "generated" not in st.session_state:
    st.session_state.generated = False

# BUTTON
if st.button("Generate My Belle Card"):
    st.session_state.generated = True

# DISPLAY (persistent)
if st.session_state.generated:

    card = generate_daily_card(user_profile, df_rules)

    st.markdown("---")
    st.header(f"{card['name']}'s Daily Card")
    st.write(f"**Date:** {card['date']} ({card['day']})")
    st.write(f"**Theme:** {card['daily_theme']}")
    st.write(f"**Wear Colors:** {', '.join(card['wear_colors'])}")
    st.write(f"**Avoid Colors:** {', '.join(card['avoid_colors'])}")
    st.write(f"**Primary Jewelry:** {card['primary_stone']} ({card['primary_jewelry_type']})")

    st.write("**Support Jewelry:**")
    for item in card["support_stones"]:
        st.write(f"- {item['stone']} ({item['jewelry_type']})")

    st.write(f"**Favored Metals:** {', '.join(card['favored_metals'])}")
    st.write(f"**Avoid Metals:** {', '.join(card['avoid_metals'])}")
    st.write(f"**Explanation:** {card['explanation']}")

    st.markdown("---")
    st.subheader("Your 7-Day Timeline")

    weekly_cards = generate_weekly_cards(user_profile, df_rules)

    selected_day = st.radio(
        "Choose your day",
        options=list(range(1, 8)),
        horizontal=True
    )

    for i, weekly_card in enumerate(weekly_cards):
        with st.container():

            is_unlocked = (
               st.session_state.unlocked_all
                or i in st.session_state.unlocked_days
                or i == selected_day - 1
            )

            st.write(f"**Day {i+1}: {weekly_card['date']} ({weekly_card['day']})**")

            if is_unlocked:
               st.write(f"Wear: {', '.join(weekly_card['wear_colors'])}")
               st.write(f"Primary: {weekly_card['primary_stone']} ({weekly_card['primary_jewelry_type']})")
               st.write(f"Theme: {weekly_card['daily_theme']}")

            else:
               st.markdown(
                    """
                   <div style="
                       opacity: 0.5;
                        padding: 12px;
                       border-radius: 12px;
                       border: 1px solid #444;
                        margin-top: 10px;
                   ">
                       🔒 Unlock This Week’s Possibilities ✨
                    </div>
                   """,
                    unsafe_allow_html=True
               )
               unlock_clicked = st.button(f"✨ Unlock Day {i+1}", key=f"unlock_{i}")

               if unlock_clicked:
                   st.session_state.unlocked_days.add(i)

                   st.session_state.unlocked_all = False

                   st.query_params["days"] = ",".join(map(str, st.session_state.unlocked_days))

    st.markdown("---")
    st.markdown("## ✨ Unlock Your Full Week")

    unlock_all = st.button("✨ Reveal My Full Alignment", key="unlock_all")

    if unlock_all:
       st.session_state.unlocked_all = True
       st.query_params["all"] = "1"
