from typing import Tuple

# ---------------------------
# Utility Functions
# ---------------------------

def convert_to_24hr(hour: int, period: str) -> int:
    if period.upper() == "PM" and hour != 12:
        return hour + 12
    if period.upper() == "AM" and hour == 12:
        return 0
    return hour


def parse_time_slot(slot: str) -> Tuple[str, int, int]:
    # Example: "Tue 2-5 PM"
    day, time_range, period = slot.split()

    start_str, end_str = time_range.split("-")
    start = convert_to_24hr(int(start_str), period)
    end = convert_to_24hr(int(end_str), period)

    return day, start, end


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
# User Input
# ---------------------------

def get_user_input():
    candidate_input = []
    interviewer_input = {}

    print("\n=== ENTER SCHEDULING DETAILS ===\n")

    # Candidate
    c = input("Enter candidate availability (comma-separated, e.g., Mon 2-5 PM, Tue 3-6 PM): ")
    candidate_input.append(c)

    # Interviewers
    n = int(input("Enter number of interviewers: "))

    for i in range(n):
        print(f"\n--- Interviewer {i+1} ---")
        name = input("Enter interviewer name: ")
        availability = input(f"Enter availability for {name} (e.g., Mon 3-6 PM): ")
        interviewer_input[name] = [availability]

    return candidate_input, interviewer_input


# ---------------------------
# Main Function
# ---------------------------

def main():
    candidate_input, interviewer_input = get_user_input()

    # ---------------------------
    # Parse Candidate Input (MULTI-DAY)
    # ---------------------------
    candidate_list = []
    for entry in candidate_input:
        candidate_list.extend([s.strip() for s in entry.split(",")])

    candidate_slots = []
    invalid_slots = []

    for slot in candidate_list:
        try:
            parsed = parse_time_slot(slot)
            candidate_slots.append(parsed)
        except:
            invalid_slots.append(slot)

    if invalid_slots:
        print(f"\n Invalid candidate input: {', '.join(invalid_slots)}")
        return

    if not candidate_slots:
        print("\n No valid candidate availability provided")
        return

    # ---------------------------
    # Parse Interviewer Input
    # ---------------------------
    interviewer_slots = {}

    for name, slots in interviewer_input.items():
        parsed_list = []
        for s in slots:
            try:
                parsed = parse_time_slot(s)
                parsed_list.append(parsed)
            except:
                continue

        if parsed_list:
            interviewer_slots[name] = parsed_list

    # ---------------------------
    # Core Logic
    # ---------------------------
    overlaps = find_overlaps(candidate_slots, interviewer_slots)
    merged_slots = merge_slots(overlaps)
    ranked = rank_slots(merged_slots)
    top_slots = ranked[:3]

    # ---------------------------
    # Handle No Results
    # ---------------------------
    if not top_slots:
        print("\n NO COMMON TIME SLOTS FOUND")
        print("Reason: No overlapping availability.")
        print("Suggestion: Adjust availability.")
        return

    # ---------------------------
    # Output
    # ---------------------------
    print("\n" + "="*50)
    print(" TOP INTERVIEW SLOTS")
    print("="*50 + "\n")

    for idx, slot in enumerate(top_slots, 1):
        start = format_time(slot["start"])
        end = format_time(slot["end"])

        conflicts = generate_conflicts(interviewer_slots, slot)

        print(f" Option {idx}")
        print(f" Time: {slot['day']} {start} - {end}")
        print(f" Available: {', '.join(slot['available'])}")
        print(f" Conflicts: {', '.join(conflicts) if conflicts else 'None'}")
        print("-" * 50)

    # ---------------------------
    # Final Recommendation
    # ---------------------------
    best = top_slots[0]
    start = format_time(best["start"])
    end = format_time(best["end"])

    print("\n" + "="*50)
    print(" FINAL RECOMMENDATION")
    print("="*50 + "\n")

    print(f"Best Slot: {best['day']} {start} - {end}")
    print(f" Interviewers Available: {', '.join(best['available'])}")
    print(f" Reason: Highest overlap with {len(best['available'])} interviewer(s)")


# ---------------------------
# Run Program
# ---------------------------

if __name__ == "__main__":
    main()