import streamlit as st

# ---------------------------
# Utility Functions
# ---------------------------

def convert_to_24hr(hour: int, period: str) -> int:
    if period.upper() == "PM" and hour != 12:
        return hour + 12
    if period.upper() == "AM" and hour == 12:
        return 0
    return hour


def parse_time_slot(slot: str):
    try:
        day, time_range, period = slot.split()
        start_str, end_str = time_range.split("-")
        start = convert_to_24hr(int(start_str), period)
        end = convert_to_24hr(int(end_str), period)
        return day, start, end
    except:
        return None


def format_time(hour: int) -> str:
    period = "AM"
    if hour >= 12:
        period = "PM"
    hour = hour if hour <= 12 else hour - 12
    if hour == 0:
        hour = 12
    return f"{hour} {period}"


# ---------------------------
# Core Logic
# ---------------------------

def find_overlaps(candidate_slots, interviewer_slots):
    overlaps = []

    for c_day, c_start, c_end in candidate_slots:
        for hour in range(c_start, c_end):
            available = []

            for name, slots in interviewer_slots.items():
                for i_day, i_start, i_end in slots:
                    if c_day == i_day and i_start <= hour < i_end:
                        available.append(name)
                        break

            if available:
                overlaps.append({
                    "day": c_day,
                    "start": hour,
                    "end": hour + 1,
                    "available": available
                })

    return overlaps


def merge_slots(overlaps):
    merged = []

    for slot in overlaps:
        if not merged:
            merged.append(slot)
            continue

        last = merged[-1]

        if (
            last["day"] == slot["day"]
            and last["end"] == slot["start"]
            and last["available"] == slot["available"]
        ):
            last["end"] = slot["end"]
        else:
            merged.append(slot)

    return merged


def rank_slots(slots):
    return sorted(
        slots,
        key=lambda x: (len(x["available"]), x["end"] - x["start"]),
        reverse=True
    )


def generate_conflicts(interviewers, slot):
    conflicts = []
    for name, slots in interviewers.items():
        available = False
        for day, start, end in slots:
            if (
                day == slot["day"]
                and start <= slot["start"]
                and end >= slot["end"]
            ):
                available = True
        if not available:
            conflicts.append(name)
    return conflicts


# ---------------------------
# UI
# ---------------------------

st.set_page_config(page_title="Interview Scheduler", layout="centered")

# Title
st.markdown(
    "<h1 style='text-align: center;'>AI Interview Scheduling System</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center;'>Enter availability like: Mon 2-5 PM, Tue 3-6 PM</p>",
    unsafe_allow_html=True
)

# ---------------------------
# Sidebar
# ---------------------------

st.sidebar.title("📌 About This App")

st.sidebar.markdown("""
This AI-powered system helps schedule interviews efficiently.

Finds overlapping slots  
Ranks best interview times  
Highlights conflicts  

---

### 🧾 How to Use

1. Enter candidate availability  
2. Add interviewer details  
3. Click **Find Best Slots**

---
""")

st.sidebar.markdown("---")

# ---------------------------
# Inputs
# ---------------------------

candidate_input = st.text_input(
    "Candidate Availability (comma-separated)",
    placeholder="Mon 2-5 PM, Tue 3-6 PM"
)

num_interviewers = st.number_input(
    "Number of Interviewers",
    min_value=1,
    max_value=10,
    step=1
)

interviewer_data = {}

for i in range(int(num_interviewers)):
    st.subheader(f"Interviewer {i+1}")
    name = st.text_input(f"Name {i+1}", key=f"name_{i}")
    availability = st.text_input(f"Availability {i+1}", key=f"avail_{i}")

    if name and availability:
        interviewer_data[name] = [availability]

# ---------------------------
# Run Logic
# ---------------------------

if st.button("Find Best Slots"):

    if not candidate_input or not interviewer_data:
        st.error("Please enter all inputs")
        st.stop()

    # Candidate parsing
    candidate_list = [s.strip() for s in candidate_input.split(",")]

    candidate_slots = []
    invalid_slots = []

    for slot in candidate_list:
        parsed = parse_time_slot(slot)
        if parsed:
            candidate_slots.append(parsed)
        else:
            invalid_slots.append(slot)

    if invalid_slots:
        st.error(f"Invalid format: {', '.join(invalid_slots)}")
        st.stop()

    # Interviewer parsing
    interviewer_slots = {}

    for name, slots in interviewer_data.items():
        parsed_list = []
        for s in slots:
            parsed = parse_time_slot(s)
            if parsed:
                parsed_list.append(parsed)

        if parsed_list:
            interviewer_slots[name] = parsed_list

    # Processing
    overlaps = find_overlaps(candidate_slots, interviewer_slots)
    merged = merge_slots(overlaps)
    ranked = rank_slots(merged)
    top_slots = ranked[:3]

    # Output
    if not top_slots:
        st.error(" No common time slots found")
    else:
        st.success(" Top Interview Slots Found")

        for idx, slot in enumerate(top_slots, 1):
            start = format_time(slot["start"])
            end = format_time(slot["end"])
            conflicts = generate_conflicts(interviewer_slots, slot)

            st.markdown(f" Option {idx}")
            st.write(f" Time: {slot['day']} {start} - {end}")
            st.write(f" Available: {', '.join(slot['available'])}")
            st.write(f" Conflicts: {', '.join(conflicts) if conflicts else 'None'}")
            st.write("---")

        best = top_slots[0]
        start = format_time(best["start"])
        end = format_time(best["end"])

        st.markdown("##  Final Recommendation")
        st.write(f"Best Slot: {best['day']} {start} - {end}")
        st.write(f" Interviewers: {', '.join(best['available'])}")
        st.write(f" Reason: Highest overlap ({len(best['available'])} interviewers)")