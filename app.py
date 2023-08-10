import streamlit as st


# Sidebar
st.sidebar.title("Navigation")

# Define sidebar sections and their corresponding pages
sidebar_sections = {
    "My Dashboard": [
        {"name": "Current Day Stats", "url": "homepage.py"},
        {"name": "Day-wise Stats", "url": "MyDashboard/daywiseStats.py"},
        {"name": "Queue Messages", "url": "MyDashboard/queueMessages.py"},
        {"name": "Error Messages", "url": "MyDashboard/errorMessages.py"},
    ],
    "Settings": [
        {"name": "Reset Password", "url": "MyDashboard/resetPassword.py"},
    ],
}

# Get the active page URL (replace this with your active_page_url variable)
active_page_url = "homepage.py"

# Display the collapsible sidebar with sections and pages
st.sidebar.markdown(
    '<div class="sidebar-toggle">☰ Toggle Sidebar</div>', unsafe_allow_html=True
)
st.sidebar.markdown('<div class="sidebar">', unsafe_allow_html=True)
for section, pages in sidebar_sections.items():
    st.sidebar.markdown(f"<h4>{section}</h4>", unsafe_allow_html=True)
    for page in pages:
        active_class = "active" if active_page_url == page["url"] else ""
        st.sidebar.markdown(
            f'<a href="{page["url"]}" class="{active_class}">{page["name"]}</a>',
            unsafe_allow_html=True,
        )
st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Main content
st.title("Main Content")
st.write("This is the main content area.")
