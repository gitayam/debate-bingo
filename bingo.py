import streamlit as st
import random
from datetime import datetime
# List of Bingo phrases
bingo_phrases = [
    "Trump attacks Harris's race", "Trump calls someone a 'Nasty Woman'", "Harris laughs",
    "Trump quotes 'Sir Sir'", "Trump quotes 'tears in their eyes'", "Trump references fake news",
    "Harris talks about education", "Trump mentions immigration", "Both candidates discuss jobs",
    "Kamala Harris mentions healthcare", "Trump makes a controversial statement", "Harris mentions 'progress'",
    "Trump blames media", "Kamala Harris praises Biden", "Trump interrupts Harris", "Both candidates discuss military",
    "Harris uses a statistic", "Trump mentions taxes", "Kamala Harris talks about equality",
    "Both candidates discuss crime", "Trump talks about the border wall", "Harris mentions social justice",
    "Both candidates discuss foreign policy", "Kamala Harris mentions infrastructure", "Trump criticizes opponents",
    "Trump mentions taxes", "Harris makes a personal story", "Trump claims 'everyone wanted Roe v Wade overturned'",
    "Harris calls Trump a 'Felon'", "Harris dodges her role in the Biden Administration",
    "Harris enhances her role in the Biden Administration", "Trump calls Harris by the wrong name",
    "Harris thanks Biden", "Trump physically approaches Harris", "Moderator can't stop Trump from talking",
    "Trump makes a face gesture", "Harris has a memorable one-liner", "Trump mentions his business empire",
    "Harris gives a thumbs up", "Trump talks about the 'deep state'", "Harris brings up her VP role",
    "Trump gives a lengthy anecdote", "Harris uses a catchphrase", "Trump talks about 'fake polls'",
    "Harris mentions 'the American people'", "Trump makes a grand gesture", "Harris mentions 'unity' with a specific example",
    "Trump says 'Believe me!'", "Harris makes a historical reference", "Trump jokes about his age", "Harris uses a metaphor",
    "Trump talks about his family", "Harris mentions a past debate moment", "Trump talks about his 'greatest achievements'",
    "Harris mentions a recent news event", "Trump says 'it’s going to be huge!'", "Harris shares a personal anecdote",
    "Trump repeats a campaign slogan", "Harris gives a heartfelt response", "Trump tries to redirect the question",
    "Harris responds with a humorous comment", "Either candidate gets visibly frustrated",
    "Either candidate uses a hand gesture for emphasis", "Either candidate references a past debate",
    "Either candidate talks about their upbringing", "Either candidate gives a detailed policy explanation",
    "Either candidate makes a surprising claim", "Either candidate receives a question they dislike",
    "Either candidate directly addresses the other", "Trump is Calm, Cool, and Collected", "Harris is Calm, Cool, and Collected",
    "Jan 6th is mentioned", "Either candidate mentions the 2020 election", "Either candidate mentions the Crypocurrency",
    "Either candidate mentions the Stock Market", "Either candidate mentions the Economy", "Either candidate mentions the Pandemic",
    "Either candidate mentions the Environment", "Either candidate mentions the Supreme Court", "Either candidate mentions the Military",
    "Trump mentions the Border Wall", "Harris mentions the Border Wall", "Either candidate mentions the Middle Class",
    "Recession is mentioned", "Inflation is mentioned", "Russia is mentioned", "Project Veritas is mentioned",
    "Hunter Biden is mentioned", "Either candidate mentions the FBI", "Either candidate mentions the CIA",
    "Project 2025 is mentioned", "Either candidate mentions the 25th Amendment", "Either candidate mentions the 2nd Amendment",
    "Windmills are killing birds", "Tarrifs are Good", "Tarrifs are Bad", "Either candidate mentions the 1st Amendment",
    "School Shootings are mentioned", "Either candidate mentions the 14th Amendment", "Either candidate mentions the 13th Amendment",
]

# Shuffle and select unique phrases based on the grid size
def generate_bingo_card(grid_size):
    if grid_size == 3:
        selected_phrases = random.sample(bingo_phrases, 8)  # 8 phrases, center is free space
        selected_phrases.insert(4, "Free space")
    else:
        selected_phrases = random.sample(bingo_phrases, 24)  # 24 phrases, center is free space
        selected_phrases.insert(12, "Free space")
    return selected_phrases

# Check if the user has completed a Bingo (full row, column, or diagonal)
def check_bingo(selected_indices, grid_size):
    if grid_size == 3:
        winning_combinations = [
            {0, 1, 2}, {3, 4, 5}, {6, 7, 8},  # rows
            {0, 3, 6}, {1, 4, 7}, {2, 5, 8},  # columns
            {0, 4, 8}, {2, 4, 6}  # diagonals
        ]
    else:
        winning_combinations = [
            {0, 1, 2, 3, 4}, {5, 6, 7, 8, 9}, {10, 11, 12, 13, 14}, {15, 16, 17, 18, 19}, {20, 21, 22, 23, 24},  # rows
            {0, 5, 10, 15, 20}, {1, 6, 11, 16, 21}, {2, 7, 12, 17, 22}, {3, 8, 13, 18, 23}, {4, 9, 14, 19, 24},  # columns
            {0, 6, 12, 18, 24}, {4, 8, 12, 16, 20}  # diagonals
        ]

    for combo in winning_combinations:
        if combo.issubset(selected_indices):
            return True
    return False

# Streamlit app
def main():
    # User selection for grid size
    grid_size = st.selectbox("Select Bingo Grid Size", [3, 5], index=0)

    # Add custom CSS for fixed square cells
    cell_size = '150px' if grid_size == 3 else '100px'  # Adjust for grid size
    st.markdown(f"""
        <style>
        .stCheckbox {{
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .bingo-cell {{
            display: inline-block;
            width: {cell_size};  /* Make width equal to height */
            height: {cell_size};  /* Make cells square */
            text-align: center;
            vertical-align: middle;
            font-size: 14px;
            border: 2px solid #ccc;
            margin: 5px;
            padding: 10px;
            line-height: {cell_size};  /* Center the text vertically */
            box-sizing: border-box;
        }}
        .bingo-header {{
            text-align: center;
            font-weight: bold;
            font-size: 18px;
        }}
        </style>
        """, unsafe_allow_html=True)

    st.title("Debate Bingo Card")

    # Generate Bingo card and store it in session state
    if "bingo_card" not in st.session_state or st.session_state.grid_size != grid_size:
        st.session_state.bingo_card = generate_bingo_card(grid_size)
        st.session_state.checked_items = []
        st.session_state.checked_indices = set()  # Track indices of checked items
        st.session_state.timeline = []
        st.session_state.bingo = False  # Bingo status
        st.session_state.grid_size = grid_size  # Track grid size

    # Display Bingo card in grid format
    bingo_card = st.session_state.bingo_card
    
    # Add "BINGO" header for 5x5 grid
    if grid_size == 5:
        st.write("<div class='bingo-header'>B&nbsp;&nbsp;&nbsp;&nbsp;I&nbsp;&nbsp;&nbsp;&nbsp;N&nbsp;&nbsp;&nbsp;&nbsp;G&nbsp;&nbsp;&nbsp;&nbsp;O</div>", unsafe_allow_html=True)

    cols = st.columns(grid_size)
    for idx, phrase in enumerate(bingo_card):
        with cols[idx % grid_size]:
            # Place checkboxes directly with no HTML formatting
            if st.checkbox(phrase, key=f"box_{idx}"):
                if phrase not in st.session_state.checked_items:
                    st.session_state.checked_items.append(phrase)
                    st.session_state.checked_indices.add(idx)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.timeline.append((phrase, timestamp))

    # Check for Bingo
    if check_bingo(st.session_state.checked_indices, grid_size):
        st.session_state.bingo = True

    # Show "BINGO!" message if Bingo is completed
    if st.session_state.bingo:
        st.subheader("🎉 BINGO! 🎉")

    # Show timeline of checked items
    st.subheader("Timeline of Checked Items")
    if st.session_state.timeline:
        for item, time in st.session_state.timeline:
            st.write(f"{time}: {item}")

    # Reset button
    if st.button("Reset Card"):
        st.session_state.bingo_card = generate_bingo_card(grid_size)
        st.session_state.checked_items = []
        st.session_state.checked_indices = set()
        st.session_state.timeline = []
        st.session_state.bingo = False

if __name__ == "__main__":
    main()