import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# ---------------------------
# SET PAGE CONFIG
# ---------------------------
st.set_page_config(
    page_title="Personal Library Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# CUSTOM CSS
# ---------------------------
st.markdown("""
<style>
h1, h2, h3 {
    color: #333;
}
.success-message {
    background-color: #d4edda;
    color: #155724;
    padding: 1rem;
    border-radius: 5px;
    font-weight: bold;
}
.warning-message {
    background-color: #fff3cd;
    color: #856404;
    padding: 1rem;
    border-radius: 5px;
    font-weight: bold;
}
.book-card {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    color: #333;
            
    font-size: 1rem;
    font-family: 'Arial', sans-serif;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.read-badge {
    background-color: #28a745;
    color: white;
    padding: 0.3rem 0.7rem;
    border-radius: 5px;
    font-size: 0.9rem;
}
.unread-badge {
    background-color: #dc3545;
    color: white;
    padding: 0.3rem 0.7rem;
    border-radius: 5px;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# LOTTIE ANIMATION
# ---------------------------
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# ---------------------------
# INIT SESSION STATE
# ---------------------------
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'book_updated' not in st.session_state:
    st.session_state.book_updated = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# ---------------------------
# FILE HANDLING FUNCTIONS
# ---------------------------
def load_library():
    if os.path.exists("library.json"):
        try:
            with open("library.json", "r") as f:
                st.session_state.library = json.load(f)
        except Exception as e:
            st.error(f"Error loading library: {e}")

def save_library():
    try:
        with open("library.json", "w") as f:
            json.dump(st.session_state.library, f, indent=4)
    except Exception as e:
        st.error(f"Error saving library: {e}")

# ---------------------------
# ADD, REMOVE, SEARCH
# ---------------------------
def add_book(title, author, year, genre, read_status):
    book = {
        "title": title,
        "author": author,
        "publication_year": year,
        "genre": genre,
        "read_status": read_status,
        "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True

def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        # ---------------------------
# SIDEBAR NAVIGATION
# ---------------------------
st.sidebar.title("📚 Personal Library Manager")
st.sidebar.markdown("---")
view = st.sidebar.radio("Navigation Bar", ["Library", "Add Book", "Search", "Statistics"])

# Reset view and flags
st.session_state.current_view = view
st.session_state.book_added = False
st.session_state.book_removed = False
st.session_state.book_updated = False

# Load books from file on app start
load_library()
# ---------------------------
# ADD BOOK
# ---------------------------
if view == "Add Book":
    st.title("➕ Add a New Book")
    with st.form("add_book_form"):
        title = st.text_input("Title")
        author = st.text_input("Author")
        year = st.number_input("Publication Year", min_value=1000, max_value=2100, step=1)
        genre = st.text_input("Genre")
        read_status = st.selectbox("Have you read it?", ["Unread", "Read"])
        submitted = st.form_submit_button("Add Book")
        if submitted and title and author:
            add_book(title, author, year, genre, read_status)
            st.success("Book added successfully!")

# ---------------------------
# VIEW LIBRARY
# ---------------------------
if view == "Library":
    st.title("📘 My Book Library")

    if st.session_state.book_removed:
        st.success("Book removed successfully!")

    if not st.session_state.library:
        st.info("No books in your library yet. Add some!")
    else:
        for i, book in enumerate(st.session_state.library):
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="book-card">
                        <h3>{book["title"]}</h3>
                        <p><strong>Author:</strong> {book.get("author")}</p>
                        <p><strong>Year:</strong> {book.get("publication_year", "N/A")}</p>
                        <p><strong>Genre:</strong> {book.get("genre")}</p>
                        <span class="{ 'read-badge' if boo.get('read_status') == 'Read' else 'unread-badge' }">
                            {book.get('read_status')}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("❌ Remove", key=f"remove_{i}"):
                        remove_book(i)
                        st.experimental_rerun()
                    toggle = st.selectbox(
                        "Change status", ["Unread", "Read"],
                        index=1 if book["read_status"] == "Read" else 0,
                        key=f"toggle_{i}"
                    )
                    if toggle != book["read_status"]:
                        book["read_status"] = toggle
                        save_library()
                        st.session_state.book_updated = True
                        st.experimental_rerun()
# ---------------------------
# SEARCH BOOKS
# ---------------------------
if view == "Search":
    st.title("🔍 Search Your Library")
    search_term = st.text_input("Search by title or author")

    if search_term:
        results = [book for book in st.session_state.library
                   if search_term.lower() in book["title"].lower()
                   or search_term.lower() in book["author"].lower()]
        if results:
            st.success(f"Found {len(results)} matching book(s):")
            for book in results:
                st.markdown(f"""
                <div class="book-card">
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <span class="{ 'read-badge' if book['read_status'] == 'Read' else 'unread-badge' }">
                        {book['read_status']}
                    </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No matching books found.")

# ---------------------------
# STATISTICS
# ---------------------------
if view == "Statistics":
    st.title("📊 Library Statistics")

    if not st.session_state.library:
        st.info("No data to show. Add some books!")
    else:
        df = pd.DataFrame(st.session_state.library)

        col1, col2 = st.columns(2)

        with col1:
            status_counts = df["read_status"].value_counts()
            fig1 = px.pie(
                names=status_counts.index,
                values=status_counts.values,
                title="Read vs Unread"
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            genre_counts = df["genre"].value_counts()
            fig2 = px.bar(
                x=genre_counts.index,
                y=genre_counts.values,
                labels={'x': 'Genre', 'y': 'Count'},
                title="Books by Genre"
            )
            st.plotly_chart(fig2, use_container_width=True)


