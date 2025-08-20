from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models.bingo import BingoPhrase


# Debate bingo phrases from the original app
BINGO_PHRASES = [
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
    "Harris mentions a recent news event", "Trump says 'it's going to be huge!'", "Harris shares a personal anecdote",
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


def init_db() -> None:
    """Initialize the database with tables and initial data."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if phrases already exist
        existing_count = db.query(BingoPhrase).count()
        
        if existing_count == 0:
            print("Initializing database with bingo phrases...")
            
            # Add all bingo phrases
            for phrase_text in BINGO_PHRASES:
                phrase = BingoPhrase(text=phrase_text, category="debate")
                db.add(phrase)
            
            db.commit()
            print(f"Added {len(BINGO_PHRASES)} bingo phrases to the database.")
        else:
            print(f"Database already initialized with {existing_count} phrases.")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()