import streamlit as st
import pandas as pd
import os
import io
import base64
from datetime import datetime
from models import (
    init_db, get_session, ScoutingSession, PitScouting, MatchScore, MatchSchedule
)

# Configure page for mobile responsiveness
st.set_page_config(
    page_title="frc scouting tool",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize database
try:
    init_db()
except Exception as e:
    st.error(f"Database connection error: {e}")

# Mobile-responsive CSS
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
    }
    
    .stButton > button {
        width: 100%;
        min-height: 50px;
        font-size: 16px;
        border-radius: 10px;
        margin: 5px 0;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        font-size: 16px !important;
        min-height: 45px;
    }
    
    .scout-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .match-card {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 8px 0;
        border-left: 4px solid #48bb78;
    }
    
    .main-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        margin-bottom: 20px;
        color: white;
    }
    
    .comparison-card {
        background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 5px;
        border: 2px solid #4a5568;
    }
    
    @media (max-width: 768px) {
        .stColumns > div {
            padding: 5px !important;
        }
        
        .stButton > button {
            min-height: 60px;
            font-size: 18px;
        }
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        min-height: 50px;
        padding: 10px 20px;
        font-size: 16px;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def get_or_create_session(team_code):
    """Get or create a scouting session for the given team code."""
    db = get_session()
    try:
        session = db.query(ScoutingSession).filter(
            ScoutingSession.team_code == team_code.lower()
        ).first()
        
        if not session:
            session = ScoutingSession(team_code=team_code.lower())
            db.add(session)
            db.commit()
            db.refresh(session)
        
        return session.id
    finally:
        db.close()

def get_pit_scouting_data(session_id):
    """Get all pit scouting data for a session."""
    db = get_session()
    try:
        data = db.query(PitScouting).filter(PitScouting.session_id == session_id).all()
        return data
    finally:
        db.close()

def get_match_scores_data(session_id):
    """Get all match scores for a session."""
    db = get_session()
    try:
        data = db.query(MatchScore).filter(MatchScore.session_id == session_id).all()
        return data
    finally:
        db.close()

def get_match_schedule_data(session_id):
    """Get match schedule for a session."""
    db = get_session()
    try:
        data = db.query(MatchSchedule).filter(MatchSchedule.session_id == session_id).order_by(MatchSchedule.match_number).all()
        return data
    finally:
        db.close()

def init_session_state():
    """Initialize session state variables."""
    if 'team_code' not in st.session_state:
        st.session_state.team_code = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None

def login_page():
    """Team code entry page."""
    st.markdown('<div class="main-header"><h1>🤖 FRC Scout</h1><p>Collaborative Robotics Scouting</p></div>', unsafe_allow_html=True)
    
    st.markdown("### Enter Your Team Code")
    st.markdown("Share this code with your teammates so everyone can collaborate on scouting data.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        team_code = st.text_input(
            "Team Code",
            placeholder="e.g., 6619a",
            max_chars=20,
            label_visibility="collapsed"
        ).strip()
        
        if st.button("🚀 Join Scouting Session", type="primary"):
            if team_code:
                st.session_state.team_code = team_code.lower()
                st.session_state.session_id = get_or_create_session(team_code)
                st.rerun()
            else:
                st.error("Please enter a team code")
        
        st.markdown("---")
        st.markdown("**How it works:**")
        st.markdown("1. Enter any code (e.g., your team number + letter)")
        st.markdown("2. Share the code with your scouting team")
        st.markdown("3. Everyone with the same code sees the same data")

def main_app():
    """Main application after login."""
    team_code = st.session_state.team_code
    session_id = st.session_state.session_id
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### 🤖 FRC Scout")
    with col2:
        st.markdown(f"**Code:** `{team_code.upper()}`")
    with col3:
        if st.button("🚪 Exit"):
            st.session_state.team_code = None
            st.session_state.session_id = None
            st.rerun()
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📋 Pit Scouting", 
        "🎯 Match Scoring", 
        "📅 Schedule",
        "📊 Dashboard", 
        "🔍 Search",
        "⚖️ Compare",
        "📤 Export"
    ])
    
    with tab1:
        pit_scouting_page(session_id)
    
    with tab2:
        match_scoring_page(session_id)
    
    with tab3:
        match_schedule_page(session_id)
    
    with tab4:
        dashboard_page(session_id)
    
    with tab5:
        search_page(session_id)
    
    with tab6:
        comparison_page(session_id)
    
    with tab7:
        export_page(session_id)

def pit_scouting_page(session_id):
    """Pit scouting form with photo upload."""
    st.markdown("### 📋 Pit Scouting Form")
    st.markdown("Record robot specifications and team information.")
    
    st.markdown("#### 📸 Robot Photo (optional)")
    uploaded_photo = st.file_uploader("Upload robot photo", type=['png', 'jpg', 'jpeg'], key="robot_photo")
    
    if 'pending_photo' not in st.session_state:
        st.session_state.pending_photo = None
        st.session_state.pending_photo_name = None
    
    if uploaded_photo:
        st.session_state.pending_photo = uploaded_photo.read()
        st.session_state.pending_photo_name = uploaded_photo.name
        st.image(st.session_state.pending_photo, caption="Photo preview", width=200)
    
    with st.form("pit_scouting_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            frc_team = st.text_input("FRC Team Number *", placeholder="e.g., 254")
            team_name = st.text_input("Team Name", placeholder="e.g., The Cheesy Poofs")
            
            drivetrain = st.selectbox("Drivetrain Type", [
                "Select...",
                "Tank/West Coast",
                "Swerve",
                "Mecanum",
                "H-Drive",
                "Other"
            ])
            
            robot_weight = st.number_input("Robot Weight (lbs)", min_value=0, max_value=150, value=0)
        
        with col2:
            robot_height = st.number_input("Robot Height (inches)", min_value=0, max_value=60, value=0)
            
            programming_lang = st.selectbox("Programming Language", [
                "Select...",
                "Java",
                "C++",
                "Python",
                "LabVIEW",
                "Other"
            ])
            
            years_experience = st.number_input("Years in FRC", min_value=0, max_value=30, value=0)
        
        st.markdown("#### Autonomous Capabilities")
        col3, col4 = st.columns(2)
        
        with col3:
            auto_scoring = st.checkbox("Can score in autonomous")
            auto_mobility = st.checkbox("Autonomous mobility")
        
        with col4:
            auto_paths = st.number_input("Number of auto paths", min_value=0, max_value=10, value=0)
        
        st.markdown("#### Game-Specific Capabilities")
        col5, col6 = st.columns(2)
        
        with col5:
            can_climb = st.checkbox("Can climb/hang")
            can_intake_ground = st.checkbox("Ground intake")
            can_intake_source = st.checkbox("Source intake")
        
        with col6:
            can_shoot_speaker = st.checkbox("Can score high")
            can_score_amp = st.checkbox("Can score low")
            has_vision = st.checkbox("Has vision tracking")
        
        st.markdown("#### Additional Notes")
        strengths = st.text_area("Robot Strengths", placeholder="What does this robot do well?")
        weaknesses = st.text_area("Robot Weaknesses", placeholder="Any issues or limitations?")
        strategy_notes = st.text_area("Strategy Notes", placeholder="How would you play with/against this robot?")
        
        scouter_name = st.text_input("Your Name (Scout)", placeholder="Who is recording this?")
        
        submitted = st.form_submit_button("💾 Save Pit Scouting Data", type="primary")
        
        if submitted:
            if not frc_team:
                st.error("Please enter the FRC team number")
            else:
                db = get_session()
                try:
                    existing = db.query(PitScouting).filter(
                        PitScouting.session_id == session_id,
                        PitScouting.frc_team == frc_team
                    ).first()
                    
                    photo_data = st.session_state.pending_photo
                    photo_filename = st.session_state.pending_photo_name
                    
                    if existing:
                        existing.team_name = team_name
                        existing.drivetrain = drivetrain if drivetrain != "Select..." else ""
                        existing.robot_weight = robot_weight
                        existing.robot_height = robot_height
                        existing.programming_lang = programming_lang if programming_lang != "Select..." else ""
                        existing.years_experience = years_experience
                        existing.auto_scoring = auto_scoring
                        existing.auto_mobility = auto_mobility
                        existing.auto_paths = auto_paths
                        existing.can_climb = can_climb
                        existing.can_intake_ground = can_intake_ground
                        existing.can_intake_source = can_intake_source
                        existing.can_shoot_speaker = can_shoot_speaker
                        existing.can_score_amp = can_score_amp
                        existing.has_vision = has_vision
                        existing.strengths = strengths
                        existing.weaknesses = weaknesses
                        existing.strategy_notes = strategy_notes
                        existing.scouter_name = scouter_name
                        existing.timestamp = datetime.utcnow()
                        if photo_data:
                            existing.robot_photo = photo_data
                            existing.photo_filename = photo_filename
                        db.commit()
                        st.success(f"✅ Updated pit scouting data for Team {frc_team}!")
                    else:
                        new_entry = PitScouting(
                            session_id=session_id,
                            frc_team=frc_team,
                            team_name=team_name,
                            drivetrain=drivetrain if drivetrain != "Select..." else "",
                            robot_weight=robot_weight,
                            robot_height=robot_height,
                            programming_lang=programming_lang if programming_lang != "Select..." else "",
                            years_experience=years_experience,
                            auto_scoring=auto_scoring,
                            auto_mobility=auto_mobility,
                            auto_paths=auto_paths,
                            can_climb=can_climb,
                            can_intake_ground=can_intake_ground,
                            can_intake_source=can_intake_source,
                            can_shoot_speaker=can_shoot_speaker,
                            can_score_amp=can_score_amp,
                            has_vision=has_vision,
                            strengths=strengths,
                            weaknesses=weaknesses,
                            strategy_notes=strategy_notes,
                            scouter_name=scouter_name,
                            robot_photo=photo_data,
                            photo_filename=photo_filename
                        )
                        db.add(new_entry)
                        db.commit()
                        st.success(f"✅ Saved pit scouting data for Team {frc_team}!")
                    st.session_state.pending_photo = None
                    st.session_state.pending_photo_name = None
                    if 'robot_photo' in st.session_state:
                        del st.session_state['robot_photo']
                    st.rerun()
                finally:
                    db.close()

def match_scoring_page(session_id):
    """Match scoring interface."""
    st.markdown("### 🎯 Match Scoring")
    
    schedule = get_match_schedule_data(session_id)
    if schedule:
        st.markdown("#### Quick Select from Schedule")
        match_options = ["Select match..."] + [f"Match {m.match_number}" for m in schedule if not m.is_completed]
        selected_match = st.selectbox("Select scheduled match", match_options)
        
        if selected_match != "Select match...":
            match_num = int(selected_match.split(" ")[1])
            match_data = next((m for m in schedule if m.match_number == match_num), None)
            if match_data:
                st.info(f"🔴 Red: {match_data.red_1}, {match_data.red_2}, {match_data.red_3} | 🔵 Blue: {match_data.blue_1}, {match_data.blue_2}, {match_data.blue_3}")
    
    st.markdown("---")
    st.markdown("Record team performance during matches.")
    
    with st.form("match_scoring_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            match_number = st.number_input("Match Number *", min_value=1, max_value=200, value=1)
        with col2:
            frc_team = st.text_input("FRC Team Number *", placeholder="e.g., 254")
        with col3:
            alliance = st.selectbox("Alliance", ["Red", "Blue"])
        
        st.markdown("#### Autonomous Period")
        col4, col5, col6 = st.columns(3)
        
        with col4:
            auto_leave = st.checkbox("Left starting zone")
        with col5:
            auto_high = st.number_input("Auto High Scores", min_value=0, max_value=20, value=0)
        with col6:
            auto_low = st.number_input("Auto Low Scores", min_value=0, max_value=20, value=0)
        
        st.markdown("#### Teleop Period")
        col7, col8, col9 = st.columns(3)
        
        with col7:
            teleop_high = st.number_input("Teleop High Scores", min_value=0, max_value=50, value=0)
        with col8:
            teleop_low = st.number_input("Teleop Low Scores", min_value=0, max_value=50, value=0)
        with col9:
            teleop_cycles = st.number_input("Total Cycles", min_value=0, max_value=30, value=0)
        
        st.markdown("#### Endgame")
        col10, col11 = st.columns(2)
        
        with col10:
            endgame_status = st.selectbox("Endgame", [
                "None",
                "Parked",
                "Climbed - Low",
                "Climbed - Mid",
                "Climbed - High",
                "Harmony Bonus"
            ])
        with col11:
            trap_scored = st.checkbox("Trap/Bonus Scored")
        
        st.markdown("#### Performance Rating")
        col12, col13 = st.columns(2)
        
        with col12:
            defense_rating = st.slider("Defense Played (1-5)", 1, 5, 3)
        with col13:
            driver_skill = st.slider("Driver Skill (1-5)", 1, 5, 3)
        
        col14, col15, col16 = st.columns(3)
        
        with col14:
            died_on_field = st.checkbox("Robot died/disabled")
        with col15:
            tipped_over = st.checkbox("Robot tipped over")
        with col16:
            exploded = st.checkbox("Robot exploded dramatically")
        
        match_notes = st.text_area("Match Notes", placeholder="Any observations about this team's performance?")
        scouter_name = st.text_input("Your Name (Scout)", placeholder="Who is recording this?")
        
        submitted = st.form_submit_button("💾 Save Match Score", type="primary")
        
        if submitted:
            if not frc_team:
                st.error("Please enter the FRC team number")
            else:
                db = get_session()
                try:
                    new_match = MatchScore(
                        session_id=session_id,
                        match_number=match_number,
                        frc_team=frc_team,
                        alliance=alliance,
                        auto_leave=auto_leave,
                        auto_high=auto_high,
                        auto_low=auto_low,
                        teleop_high=teleop_high,
                        teleop_low=teleop_low,
                        teleop_cycles=teleop_cycles,
                        endgame_status=endgame_status,
                        trap_scored=trap_scored,
                        defense_rating=defense_rating,
                        driver_skill=driver_skill,
                        died_on_field=died_on_field,
                        tipped_over=tipped_over,
                        exploded=exploded,
                        match_notes=match_notes,
                        scouter_name=scouter_name
                    )
                    db.add(new_match)
                    db.commit()
                    st.success(f"✅ Saved match {match_number} data for Team {frc_team}!")
                    st.rerun()
                finally:
                    db.close()

def match_schedule_page(session_id):
    """Match schedule management."""
    st.markdown("### 📅 Match Schedule")
    st.markdown("Add matches to the schedule for quick reference during scouting.")
    
    with st.form("add_match_schedule", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            match_number = st.number_input("Match Number", min_value=1, max_value=200, value=1)
            match_type = st.selectbox("Match Type", ["Qualification", "Quarterfinal", "Semifinal", "Final"])
        
        with col2:
            scheduled_time = st.time_input("Scheduled Time (optional)")
        
        st.markdown("#### Red Alliance")
        red_col1, red_col2, red_col3 = st.columns(3)
        with red_col1:
            red_1 = st.text_input("Red 1", placeholder="Team #")
        with red_col2:
            red_2 = st.text_input("Red 2", placeholder="Team #")
        with red_col3:
            red_3 = st.text_input("Red 3", placeholder="Team #")
        
        st.markdown("#### Blue Alliance")
        blue_col1, blue_col2, blue_col3 = st.columns(3)
        with blue_col1:
            blue_1 = st.text_input("Blue 1", placeholder="Team #")
        with blue_col2:
            blue_2 = st.text_input("Blue 2", placeholder="Team #")
        with blue_col3:
            blue_3 = st.text_input("Blue 3", placeholder="Team #")
        
        if st.form_submit_button("➕ Add to Schedule", type="primary"):
            db = get_session()
            try:
                new_match = MatchSchedule(
                    session_id=session_id,
                    match_number=match_number,
                    match_type=match_type,
                    red_1=red_1,
                    red_2=red_2,
                    red_3=red_3,
                    blue_1=blue_1,
                    blue_2=blue_2,
                    blue_3=blue_3
                )
                db.add(new_match)
                db.commit()
                st.success(f"✅ Added Match {match_number} to schedule!")
                st.rerun()
            finally:
                db.close()
    
    st.markdown("---")
    st.markdown("#### Current Schedule")
    
    schedule = get_match_schedule_data(session_id)
    if schedule:
        for match in schedule:
            status = "✅" if match.is_completed else "⏳"
            with st.expander(f"{status} Match {match.match_number} - {match.match_type}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**🔴 Red Alliance:** {match.red_1}, {match.red_2}, {match.red_3}")
                with col2:
                    st.markdown(f"**🔵 Blue Alliance:** {match.blue_1}, {match.blue_2}, {match.blue_3}")
                
                if not match.is_completed:
                    if st.button(f"Mark Complete", key=f"complete_{match.id}"):
                        db = get_session()
                        try:
                            db_match = db.query(MatchSchedule).filter(MatchSchedule.id == match.id).first()
                            if db_match:
                                db_match.is_completed = True
                                db.commit()
                                st.rerun()
                        finally:
                            db.close()
    else:
        st.info("No matches scheduled yet. Add matches above!")

def dashboard_page(session_id):
    """View all scouting data."""
    st.markdown("### 📊 Scouting Dashboard")
    
    pit_data = get_pit_scouting_data(session_id)
    match_data = get_match_scores_data(session_id)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Teams Scouted", len(pit_data))
    with col2:
        st.metric("Matches Recorded", len(match_data))
    with col3:
        unique_teams = len(set([m.frc_team for m in match_data]))
        st.metric("Teams with Match Data", unique_teams)
    
    st.markdown("---")
    
    st.markdown("#### 📋 Pit Scouting Records")
    if pit_data:
        for entry in pit_data:
            with st.expander(f"Team {entry.frc_team} - {entry.team_name or 'Unknown'}"):
                col1, col2 = st.columns(2)
                with col1:
                    if entry.robot_photo:
                        st.image(entry.robot_photo, caption=f"Team {entry.frc_team} Robot", use_container_width=True)
                    
                    st.write(f"**Drivetrain:** {entry.drivetrain or 'N/A'}")
                    st.write(f"**Weight:** {entry.robot_weight or 'N/A'} lbs")
                    st.write(f"**Height:** {entry.robot_height or 'N/A'} in")
                    st.write(f"**Language:** {entry.programming_lang or 'N/A'}")
                with col2:
                    st.write(f"**Auto Scoring:** {'✅' if entry.auto_scoring else '❌'}")
                    st.write(f"**Can Climb:** {'✅' if entry.can_climb else '❌'}")
                    st.write(f"**Vision:** {'✅' if entry.has_vision else '❌'}")
                    st.write(f"**Auto Paths:** {entry.auto_paths or 0}")
                
                if entry.strengths:
                    st.write(f"**Strengths:** {entry.strengths}")
                if entry.weaknesses:
                    st.write(f"**Weaknesses:** {entry.weaknesses}")
                if entry.strategy_notes:
                    st.write(f"**Strategy:** {entry.strategy_notes}")
                
                st.caption(f"Scouted by: {entry.scouter_name or 'Unknown'}")
    else:
        st.info("No pit scouting data yet. Start scouting teams!")
    
    st.markdown("---")
    
    st.markdown("#### 🎯 Match Scores")
    if match_data:
        sorted_matches = sorted(match_data, key=lambda x: (x.match_number, x.frc_team))
        
        for entry in sorted_matches:
            alliance_color = "🔴" if entry.alliance == "Red" else "🔵"
            with st.expander(f"Match {entry.match_number} - Team {entry.frc_team} {alliance_color}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Autonomous:**")
                    st.write(f"Left Zone: {'✅' if entry.auto_leave else '❌'}")
                    st.write(f"High: {entry.auto_high or 0}")
                    st.write(f"Low: {entry.auto_low or 0}")
                
                with col2:
                    st.write("**Teleop:**")
                    st.write(f"High: {entry.teleop_high or 0}")
                    st.write(f"Low: {entry.teleop_low or 0}")
                    st.write(f"Cycles: {entry.teleop_cycles or 0}")
                
                with col3:
                    st.write("**Endgame:**")
                    st.write(f"{entry.endgame_status or 'None'}")
                    st.write(f"Defense: {'⭐' * (entry.defense_rating or 3)}")
                    st.write(f"Skill: {'⭐' * (entry.driver_skill or 3)}")
                
                if entry.died_on_field:
                    st.warning("⚠️ Robot died on field")
                if entry.tipped_over:
                    st.warning("⚠️ Robot tipped over")
                if entry.exploded:
                    st.warning("⚠️ Robot exploded")
                
                if entry.match_notes:
                    st.write(f"**Notes:** {entry.match_notes}")
                
                st.caption(f"Scouted by: {entry.scouter_name or 'Unknown'}")
    else:
        st.info("No match data yet. Start recording matches!")

def search_page(session_id):
    """Search and filter scouting data."""
    st.markdown("### 🔍 Search & Filter")
    
    pit_data = get_pit_scouting_data(session_id)
    match_data = get_match_scores_data(session_id)
    
    search_team = st.text_input("Search by Team Number", placeholder="Enter team number...")
    
    if search_team:
        st.markdown("---")
        
        pit_results = [p for p in pit_data if search_team in p.frc_team]
        match_results = [m for m in match_data if search_team in m.frc_team]
        
        if pit_results:
            st.markdown(f"#### 📋 Pit Scouting for Team {search_team}")
            for entry in pit_results:
                col1, col2 = st.columns([1, 2])
                with col1:
                    if entry.robot_photo:
                        st.image(entry.robot_photo, use_container_width=True)
                with col2:
                    st.write(f"**Team {entry.frc_team}** - {entry.team_name or 'Unknown'}")
                    st.write(f"Drivetrain: {entry.drivetrain or 'N/A'} | Weight: {entry.robot_weight or 'N/A'} lbs")
                    st.write(f"Strengths: {entry.strengths or 'N/A'}")
        
        if match_results:
            st.markdown(f"#### 🎯 Match Performance for Team {search_team}")
            
            if match_results:
                avg_high = sum((m.teleop_high or 0) + (m.auto_high or 0) for m in match_results) / len(match_results)
                avg_low = sum((m.teleop_low or 0) + (m.auto_low or 0) for m in match_results) / len(match_results)
                avg_cycles = sum(m.teleop_cycles or 0 for m in match_results) / len(match_results)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Matches", len(match_results))
                with col2:
                    st.metric("Avg High", f"{avg_high:.1f}")
                with col3:
                    st.metric("Avg Low", f"{avg_low:.1f}")
                with col4:
                    st.metric("Avg Cycles", f"{avg_cycles:.1f}")
        
        if not pit_results and not match_results:
            st.info(f"No data found for team {search_team}")
    
    st.markdown("---")
    st.markdown("#### Quick Filters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧗 Teams that can climb"):
            climbers = [p for p in pit_data if p.can_climb]
            if climbers:
                st.write("**Teams with climbing capability:**")
                for c in climbers:
                    st.write(f"- Team {c.frc_team} ({c.team_name or 'Unknown'})")
            else:
                st.info("No teams with climbing capability recorded")
    
    with col2:
        if st.button("🎯 Teams with vision"):
            vision_teams = [p for p in pit_data if p.has_vision]
            if vision_teams:
                st.write("**Teams with vision tracking:**")
                for v in vision_teams:
                    st.write(f"- Team {v.frc_team} ({v.team_name or 'Unknown'})")
            else:
                st.info("No teams with vision tracking recorded")

def comparison_page(session_id):
    """Compare multiple teams side-by-side."""
    st.markdown("### ⚖️ Team Comparison")
    st.markdown("Select teams to compare their capabilities side-by-side.")
    
    pit_data = get_pit_scouting_data(session_id)
    match_data = get_match_scores_data(session_id)
    
    if not pit_data:
        st.info("No teams to compare. Add pit scouting data first!")
        return
    
    team_options = [f"{p.frc_team} - {p.team_name or 'Unknown'}" for p in pit_data]
    
    selected_teams = st.multiselect(
        "Select teams to compare (up to 4)",
        team_options,
        max_selections=4
    )
    
    if len(selected_teams) >= 2:
        selected_team_nums = [t.split(" - ")[0] for t in selected_teams]
        
        cols = st.columns(len(selected_teams))
        
        for i, team_num in enumerate(selected_team_nums):
            team_pit = next((p for p in pit_data if p.frc_team == team_num), None)
            team_matches = [m for m in match_data if m.frc_team == team_num]
            
            if team_pit:
                with cols[i]:
                    st.markdown(f"### Team {team_num}")
                    st.markdown(f"**{team_pit.team_name or 'Unknown'}**")
                    
                    if team_pit.robot_photo:
                        st.image(team_pit.robot_photo, use_container_width=True)
                    
                    st.markdown("---")
                    st.markdown("**Specs:**")
                    st.write(f"🔧 {team_pit.drivetrain or 'N/A'}")
                    st.write(f"⚖️ {team_pit.robot_weight or 0} lbs")
                    st.write(f"📏 {team_pit.robot_height or 0} in")
                    
                    st.markdown("---")
                    st.markdown("**Capabilities:**")
                    st.write(f"Auto Score: {'✅' if team_pit.auto_scoring else '❌'}")
                    st.write(f"Climb: {'✅' if team_pit.can_climb else '❌'}")
                    st.write(f"Vision: {'✅' if team_pit.has_vision else '❌'}")
                    st.write(f"Auto Paths: {team_pit.auto_paths or 0}")
                    
                    if team_matches:
                        st.markdown("---")
                        st.markdown("**Match Stats:**")
                        avg_high = sum((m.teleop_high or 0) + (m.auto_high or 0) for m in team_matches) / len(team_matches)
                        avg_cycles = sum(m.teleop_cycles or 0 for m in team_matches) / len(team_matches)
                        avg_skill = sum(m.driver_skill or 3 for m in team_matches) / len(team_matches)
                        
                        st.metric("Matches", len(team_matches))
                        st.metric("Avg Scores", f"{avg_high:.1f}")
                        st.metric("Avg Cycles", f"{avg_cycles:.1f}")
                        st.metric("Avg Skill", f"{avg_skill:.1f}⭐")
    elif len(selected_teams) == 1:
        st.warning("Select at least 2 teams to compare")

def export_page(session_id):
    """Export data to CSV/Excel."""
    st.markdown("### 📤 Export Data")
    st.markdown("Download your scouting data for analysis and sharing.")
    
    pit_data = get_pit_scouting_data(session_id)
    match_data = get_match_scores_data(session_id)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Pit Scouting Data")
        if pit_data:
            pit_df = pd.DataFrame([{
                'Team Number': p.frc_team,
                'Team Name': p.team_name,
                'Drivetrain': p.drivetrain,
                'Weight (lbs)': p.robot_weight,
                'Height (in)': p.robot_height,
                'Programming Language': p.programming_lang,
                'Years Experience': p.years_experience,
                'Auto Scoring': p.auto_scoring,
                'Auto Mobility': p.auto_mobility,
                'Auto Paths': p.auto_paths,
                'Can Climb': p.can_climb,
                'Ground Intake': p.can_intake_ground,
                'Source Intake': p.can_intake_source,
                'High Scoring': p.can_shoot_speaker,
                'Low Scoring': p.can_score_amp,
                'Has Vision': p.has_vision,
                'Strengths': p.strengths,
                'Weaknesses': p.weaknesses,
                'Strategy Notes': p.strategy_notes,
                'Scout': p.scouter_name
            } for p in pit_data])
            
            csv_pit = pit_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Pit Scouting CSV",
                data=csv_pit,
                file_name="pit_scouting_data.csv",
                mime="text/csv",
                type="primary"
            )
            
            st.dataframe(pit_df, use_container_width=True)
        else:
            st.info("No pit scouting data to export")
    
    with col2:
        st.markdown("#### 🎯 Match Scores Data")
        if match_data:
            match_df = pd.DataFrame([{
                'Match Number': m.match_number,
                'Team Number': m.frc_team,
                'Alliance': m.alliance,
                'Auto Leave': m.auto_leave,
                'Auto High': m.auto_high,
                'Auto Low': m.auto_low,
                'Teleop High': m.teleop_high,
                'Teleop Low': m.teleop_low,
                'Teleop Cycles': m.teleop_cycles,
                'Endgame': m.endgame_status,
                'Trap Scored': m.trap_scored,
                'Defense Rating': m.defense_rating,
                'Driver Skill': m.driver_skill,
                'Died on Field': m.died_on_field,
                'Tipped Over': m.tipped_over,
                'Exploded': m.exploded,
                'Notes': m.match_notes,
                'Scout': m.scouter_name
            } for m in match_data])
            
            csv_match = match_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Match Scores CSV",
                data=csv_match,
                file_name="match_scores_data.csv",
                mime="text/csv",
                type="primary"
            )
            
            st.dataframe(match_df, use_container_width=True)
        else:
            st.info("No match data to export")
    
    st.markdown("---")
    st.markdown("#### 📊 Combined Report")
    
    if pit_data or match_data:
        if st.button("📥 Download Full Report (Excel)", type="primary"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                if pit_data:
                    pit_df = pd.DataFrame([{
                        'Team Number': p.frc_team,
                        'Team Name': p.team_name,
                        'Drivetrain': p.drivetrain,
                        'Weight (lbs)': p.robot_weight,
                        'Height (in)': p.robot_height,
                        'Can Climb': p.can_climb,
                        'Has Vision': p.has_vision,
                        'Auto Paths': p.auto_paths,
                        'Strengths': p.strengths,
                        'Weaknesses': p.weaknesses
                    } for p in pit_data])
                    pit_df.to_excel(writer, sheet_name='Pit Scouting', index=False)
                
                if match_data:
                    match_df = pd.DataFrame([{
                        'Match': m.match_number,
                        'Team': m.frc_team,
                        'Alliance': m.alliance,
                        'Auto High': m.auto_high,
                        'Auto Low': m.auto_low,
                        'Teleop High': m.teleop_high,
                        'Teleop Low': m.teleop_low,
                        'Cycles': m.teleop_cycles,
                        'Endgame': m.endgame_status,
                        'Skill': m.driver_skill
                    } for m in match_data])
                    match_df.to_excel(writer, sheet_name='Match Scores', index=False)
            
            st.download_button(
                label="📥 Click to Download Excel",
                data=output.getvalue(),
                file_name="frc_scouting_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("No data to export. Start scouting first!")

def main():
    init_session_state()
    
    if st.session_state.team_code is None:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()

"""Andrej Mes."""
"""12/13/25"""
