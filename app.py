
import streamlit as st
from datetime import datetime, timedelta, date
import hashlib
import uuid

# --- CONFIGURATION ---
STRIPE_WEEKLY_LINK = "https://buy.stripe.com/14A5kF1Inbxl5kw3Ak0Jq00"
STRIPE_YEARLY_LINK = "https://buy.stripe.com/5kQ5kF5YD30PdR2gn60Jq01"
STRIPE_BIRTH_CHART_LINK = "https://buy.stripe.com/eVqbJ3biXathdR28UE0Jq02"
ATLIER_COUPON_CODE = "BELLE50"

# --- MANUAL VERIFICATION ---
VALID_CODES = ["BELLE2026"]

# --- CORE LOGIC ---

def get_moon_phase():
    try:
        today = date.today()
        phase_idx = (today.day % 29)
        phases = ["New Moon","Waxing Crescent","First Quarter","Waxing Gibbous",
                  "Full Moon","Waning Gibbous","Last Quarter","Waning Crescent"]
        return phases[phase_idx // 3]
    except Exception:
        return "Unknown"

def get_chinese_zodiac(dob):
    if not dob:
        return {"animal": "Unknown", "element": "Unknown"}
    animals = ["Rat", "Ox", "Tiger", "Rabbit", "Dragon", "Snake", "Horse",
               "Goat", "Monkey", "Rooster", "Dog", "Pig"]
    stems = ["Wood", "Wood", "Fire", "Fire", "Earth", "Earth", "Metal", "Metal", "Water", "Water"]
    animal_idx = (dob.year - 1924) % 12
    stem_idx = (dob.year - 4) % 10
    return {"animal": animals[animal_idx], "element": stems[stem_idx]}

def validate_dob(year, month, day):
    current_year = date.today().year
    if not year:
        return False, "Birth Year is required."
    if year < 1900:
        return False, "Please enter a realistic birth year (after 1900)."
    if year > current_year - 18:
        return False, "You must be at least 18 years old."
    if month and not day:
        return False, "If you select a month, you must also select a day."
    if day and not month:
        return False, "If you select a day, you must also select a month."
    if month and day:
        try:
            date(year, month, day)
        except ValueError:
            return False, "Invalid date (e.g., February 31)."
    return True, None

def generate_daily_forecast(profile, moon_phase):
    try:
        day = datetime.now().strftime("%A")
        dob = profile.get("dob") if profile else None
        zodiac_info = get_chinese_zodiac(dob)
        zodiac_display = f"{zodiac_info['element']} {zodiac_info['animal']}" if zodiac_info['animal'] != "Unknown" else "General"
        base = {
            "colors_good": ["Gold", "White", "Emerald"],
            "colors_bad": ["Grey", "Black"],
            "stones": ["Citrine", "Jade"],
            "numbers": [3, 8],
            "metal": "Gold"
        }
        return {
            "day": day,
            "zodiac": zodiac_display,
            "moon_context": f"The {moon_phase} influences your energy today.",
            **base
        }
    except Exception:
        return {
            "day": datetime.now().strftime("%A"),
            "zodiac": "Unknown",
            "moon_context": "Unable to calculate.",
            "colors_good": ["Gold"],
            "colors_bad": ["Grey"],
            "stones": ["Citrine"],
            "numbers": [3],
            "metal": "Gold"
        }

# --- SESSION INIT ---

def init():
    defaults = {
        "user_profile": None,
        "subscription_status": "free",
        "sub_expiry": None,
        "coupon_used": False,
        "verified_payment": False,
        "profile_error": None,
        "device_id": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def check_subscription():
    try:
        expiry_str = st.session_state.get("sub_expiry")
        if not expiry_str:
            return False
        expiry = datetime.fromisoformat(expiry_str)
        if datetime.now() > expiry:
            st.session_state.subscription_status = "expired"
            return False
        return True
    except Exception:
        return False

def is_renewal_needed():
    try:
        if st.session_state.get("subscription_status") != "weekly":
            return False
        expiry_str = st.session_state.get("sub_expiry")
        if not expiry_str:
            return False
        expiry = datetime.fromisoformat(expiry_str)
        hours_left = (expiry - datetime.now()).total_seconds() / 3600
        return hours_left <= 24
    except Exception:
        return False

# --- UI ---

st.set_page_config(page_title="Belle", layout="centered")

init()

st.title("✨ Your Prosperity Timeline")

# --- SESSION WARNING ---
st.warning("⚠️ Your profile is stored in your browser session. Keep this tab open to maintain access.")

# --- FREE MOON ---
moon = get_moon_phase()
st.info(f"🌙 Current Moon Phase: **{moon}**")

# --- PROFILE ---
st.subheader("🔮 Your Cosmic Profile")

if not st.session_state.user_profile:
    st.markdown("Please create your profile to begin.")
    st.caption("*Year is required. Month and Day are optional.*")

    col1, col2 = st.columns(2)
    with col1:
        # ANTI-AUTOFILL: text_area instead of text_input
        # Browsers NEVER autofill textareas
        name = st.text_area("Your Identifier", placeholder="", height=68, key="belle_id", max_chars=50)

        # ANTI-AUTOFILL: slider instead of number_input
        # Browsers CANNOT autofill sliders
        current_year = date.today().year
        birth_year = st.slider("Birth Year (Required)", min_value=1900, max_value=current_year - 18, value=1990, key="belle_yr")

        col_sub1, col_sub2 = st.columns(2)
        with col_sub1:
            month_map = {None: None, "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
                         "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
            birth_month_str = st.selectbox("Month (Optional)", list(month_map.keys()), index=0, key="belle_mo")
            birth_month = month_map[birth_month_str]

        with col_sub2:
            birth_day = st.slider("Day (Optional)", min_value=1, max_value=31, value=1, key="belle_dy")

    with col2:
        time_birth = st.time_input("Time of Birth (Optional)", value=None, key="belle_tm")
        location = st.text_area("Place of Birth (Optional)", placeholder="", height=68, key="belle_loc", max_chars=100)

    if st.session_state.get("profile_error"):
        st.error(st.session_state.profile_error)

    if st.button("Create My Profile", type="primary", key="btn_create_profile"):
        error = None

        if not name or not name.strip():
            error = "Please enter your identifier"
        elif len(name.strip()) < 3 or not name.replace(" ", "").isalpha():
            error = "Identifier must be at least 3 letters, no symbols"

        if not error:
            # For the day slider, if no month selected, set day to None
            day_to_validate = birth_day if birth_month else None
            valid, date_err = validate_dob(birth_year, birth_month, day_to_validate)
            if not valid:
                error = date_err

        if error:
            st.session_state.profile_error = error
            st.rerun()
        else:
            try:
                m = birth_month if birth_month else 1
                d = birth_day if birth_month else 1
                dob_obj = date(birth_year, m, d)

                time_str = str(time_birth) if time_birth else "Unknown"
                device_id = st.session_state.get("device_id") or str(uuid.uuid4())

                hash_id = hashlib.sha256(
                    f"{name}{dob_obj}{time_str}{location}{device_id}".encode()
                ).hexdigest()

                st.session_state.user_profile = {
                    "name": name.strip(),
                    "dob": dob_obj,
                    "time": time_str,
                    "location": location.strip() if location else "Unknown",
                    "id": hash_id,
                    "device_id": device_id
                }
                st.session_state.profile_error = None
                st.success("Profile locked 🔒 Device bound.")
                st.rerun()
            except Exception as e:
                st.error(f"Error creating profile: {str(e)}")

else:
    profile = st.session_state.user_profile
    zodiac_info = get_chinese_zodiac(profile.get("dob"))

    st.markdown(f"**Name:** {profile.get('name', 'Unknown')}")
    st.markdown(f"**Zodiac:** {zodiac_info['element']} {zodiac_info['animal']}")
    st.markdown(f"**Born in:** {profile.get('location', 'N/A')}")
    st.caption("Your device is bound to this profile. Keep this tab open to maintain access.")

# --- PAYWALL ---
st.divider()
access = check_subscription()

if not access:
    if st.session_state.get("subscription_status") == "expired":
        st.error("⚠️ Your access expired. Renew to continue.")

    st.warning("🔒 Premium Locked")
    st.markdown("### Unlock your week")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"[💰 Weekly ($10 MXN)]({STRIPE_WEEKLY_LINK})", unsafe_allow_html=True)
    with col2:
        st.markdown(f"[💎 Yearly ($360 MXN)]({STRIPE_YEARLY_LINK})", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔐 Manual Verification")
    st.info("📧 **Step 1:** Pay using the links above.\n📩 **Step 2:** Email your receipt to **contact@belle-app.com** (or DM us).\n🔑 **Step 3:** We will send you a unique activation code.\n🔢 **Step 4:** Enter that code below to unlock.")

    col_plan, col_code = st.columns(2)
    with col_plan:
        plan_choice = st.selectbox("Which plan did you purchase?", ["Weekly", "Yearly"], key="belle_plan")
    with col_code:
        code_input = st.text_input("Enter Activation Code", type="password", key="belle_code")

    if st.button("Activate Access", type="primary", key="btn_activate"):
        if code_input in VALID_CODES:
            try:
                st.session_state.subscription_status = plan_choice.lower()
                if plan_choice == "Weekly":
                    st.session_state.sub_expiry = (datetime.now() + timedelta(days=7)).isoformat()
                else:
                    st.session_state.sub_expiry = (datetime.now() + timedelta(days=365)).isoformat()
                st.session_state.verified_payment = True
                st.success("Access granted ✨")
                st.rerun()
            except Exception as e:
                st.error(f"Error verifying payment: {str(e)}")
        else:
            st.error("❌ Invalid code. Please check your email for your unique activation code.")
            st.info("💡 Codes are issued manually after payment verification. Please email your receipt if you haven't received one.")

else:
    st.success("✨ Access Active")

    if is_renewal_needed():
        st.warning("⚠️ Your weekly subscription expires in less than 24 hours! Renew now.")
        st.markdown(f"[💰 Renew Weekly]({STRIPE_WEEKLY_LINK})", unsafe_allow_html=True)

    try:
        forecast = generate_daily_forecast(st.session_state.user_profile, moon)

        st.subheader(f"🌟 {forecast['day']} Forecast")
        st.markdown(f"**Zodiac:** {forecast['zodiac']}")
        st.markdown(forecast["moon_context"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**🎨 Good Colors**")
            for c in forecast.get("colors_good", []):
                st.write(f"- {c}")

        with col2:
            st.markdown("**🚫 Avoid**")
            for c in forecast.get("colors_bad", []):
                st.write(f"- {c}")

        with col3:
            st.markdown("**💎 Stones & Metal**")
            for s in forecast.get("stones", []):
                st.write(f"- {s}")
            st.write(f"**Metal:** {forecast.get('metal', 'Gold')}")
            st.write(f"**Lucky Numbers:** {', '.join(map(str, forecast.get('numbers', [])))}")
    except Exception as e:
        st.error(f"Error displaying forecast: {str(e)}")

    # --- JEWELRY DIRECTORY & COUPON ---
    st.divider()
    st.subheader("📿 Jewelry Atelier")

    owned = st.multiselect("I own:", ["Bracelet", "Necklace", "Ring", "Earrings"], key="belle_jewelry")

    if owned:
        st.markdown("### ✨ Suggested Pieces")

        if not st.session_state.get("coupon_used"):
            st.success(f"🎉 **Coupon Available!** Use code **{ATLIER_COUPON_CODE}** for 50% off one Atelier piece this week.")
            if st.button("Claim Coupon", key="btn_claim_coupon"):
                st.session_state.coupon_used = True
                st.rerun()
        else:
            st.info("You've used your weekly coupon. A new one arrives next week!")

        if "Bracelet" in owned:
            st.markdown("#### Recommended Bracelet")
            st.image("https://placehold.co/200x200?text=Moonstone+Bracelet", width=150)
            st.markdown("[Shop Atelier](https://your-atelier-link.com)")

        if "Necklace" in owned:
            st.markdown("#### Recommended Necklace")
            st.image("https://placehold.co/200x200?text=Jade+Necklace", width=150)
            st.markdown("[Shop Atelier](https://your-atelier-link.com)")

    # --- BIRTH CHART ---
    st.divider()
    st.subheader("📜 Full Birth Chart")
    st.write("Your complete natal chart with planetary positions and ancient wisdom analysis.")
    st.markdown(f"[🔓 Unlock Full Chart ($100 MXN)]({STRIPE_BIRTH_CHART_LINK})", unsafe_allow_html=True)

# --- FOOTER ---
st.divider()
st.caption("Belle v14 | Secure & Private")
