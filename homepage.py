# import module
import streamlit as st
import base64
import streamlit_authenticator as stauth
import psycopg2
import pandas as pd

from streamlit_extras.stoggle import stoggle

# What is the source of this page ?
from st_pages import Page, Section, show_pages, add_page_title
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

# when i use "st_pages", than "set_page_config" doesn't work
st.set_page_config(
    page_icon="🧊",
    initial_sidebar_state="expanded",
)


# Initialize connection.
@st.cache_resource
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])


conn = init_connection()


# Perform query.
@st.cache_data(ttl=600)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


user_names = run_query("SELECT tbl_acl.user FROM tbl_acl")
user_names_list = [item[0] for item in user_names]

names = run_query("SELECT last_name FROM tbl_acl")
# Converting to List
names_list = [item[0] for item in names]

passwords = run_query("SELECT password FROM tbl_acl")
passwords_list = [item[0] for item in passwords]

hashed_passwords = stauth.Hasher(passwords_list).generate()

credentials = {"usernames": {}}

for un, name, pw in zip(user_names_list, names, hashed_passwords):
    user_dict = {"name": name, "password": pw}
    credentials["usernames"].update({un: user_dict})

authenticator = stauth.Authenticate(
    credentials, "some_cookie_name", "some_signature_key", cookie_expiry_days=30
)

names, authentication_status, user_names_list = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    user_name = user_names_list
    authenticator.logout("Logout", "sidebar")

    st.markdown(
        """
        <style>
        .css-e3xfei.eczjsme4 {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 10%;
            height: 100px;
            background-color: #f0f0f0;
            /* Add any other styling you want for the class */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="css-e3xfei.eczjsme4"></div>', unsafe_allow_html=True)

    if user_name == "admin":
        show_pages(
            [
                Section(name="My Dashboard"),
                Page("homepage.py", "Current Day Stats"),
                Page("MyDashboard/daywiseStats.py", "Day-wise Stats"),
                Page("MyDashboard/queueMessages.py", "Queue Messages"),
                Page("MyDashboard/errorMessages.py", "Error Messages"),
                Section(name="Settings"),
                Page("MyDashboard/resetPassword.py", "Reset Password"),
            ]
        )
        st.markdown(
            """<style>[data-testid="stSidebarNav"] {padding-top: 30%;}</style>""",
            unsafe_allow_html=True,
        )
    else:
        show_pages(
            [
                Section(name="My Dashboard"),
                Page("homepage.py", "Current Day Stats"),
                Page("MyDashboard/daywiseStats.py", "Day-wise Stats"),
                Section(name="Settings"),
                Page("MyDashboard/resetPassword.py", "Reset Password"),
            ]
        )
        st.markdown(
            """<style>[data-testid="stSidebarNav"] {padding-top: 20%;}</style>""",
            unsafe_allow_html=True,
        )

    # Show logo
    def get_base64_of_bin_file(png_file):
        with open(png_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    def build_markup_for_logo(
        png_file,
        background_position="50% 10%",
        margin_top="15%",
        image_width="60%",
        image_height="",
    ):
        binary_string = get_base64_of_bin_file(png_file)
        return """
                <style>
                    [data-testid="stSidebarNav"] {
                        background-image: url("data:image/png;base64,%s");
                        background-repeat: no-repeat;
                        background-position: %s;
                        margin-top: %s;
                        background-size: %s %s;
                    }
                </style>
                """ % (
            binary_string,
            background_position,
            margin_top,
            image_width,
            image_height,
        )

    def add_logo(png_file):
        logo_markup = build_markup_for_logo(png_file)
        st.markdown(
            logo_markup,
            unsafe_allow_html=True,
        )

    add_logo("resources/ESoftLogo.png")

    add_page_title()

    recordOwnerList = run_query(
        "SELECT record_owner FROM tbl_acl WHERE tbl_acl.user = '"
        + user_names_list
        + "'"
    )
    string_value = recordOwnerList[0][0]

    rows = run_query(
        "select date_trunc('day', creation_datetime),count(*), SUM(CEIL(msg_len/70.0))::integer FROM public.tbl_outbox where msg_status = 0 and op_status = 0 AND record_owner = '"
        + string_value
        + "' group by date_trunc('day', creation_datetime) order by date_trunc('day', creation_datetime) desc;"
    )

    # df = pd.DataFrame(rows,columns=["Date","Sum"]
    df = pd.DataFrame(rows)
    # Rename the colum from 0 ,1 etc to Date-Count

    df.columns = ["Date-Time", "Request-Count", "Total-Count"]
    # df['Sum'] = df.sum(axis=1)

    # df.loc["Total", ""] = df.MyColumn.sum()

    # This works
    # Draws 2 Graphs -
    st.line_chart(
        data=df,
        x="Date-Time",
        y=["Request-Count", "Total-Count"],
        use_container_width=True,
    )

    # st.dataframe(df)  # S..ame as st.write(df)
    # st.dataframe(df,use_container_width=True)

    # ----
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=True)  # Add pagination
    gb.configure_side_bar()  # Add a sidebar
    # gb.configure_selection('multiple', use_checkbox=True, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
    # gb.configure_selection('multiple', use_checkbox=False, groupSelectsChildren="Group checkbox select children") #Enable multi-row selection
    gridOptions = gb.build()
    # ------

    grid_response = AgGrid(
        df,
        gridOptions=gridOptions,
        #    data_return_mode='AS_INPUT',
        #    update_mode='MODEL_CHANGED',
        fit_columns_on_grid_load=True,
        #    #theme='blue', #Add theme color to the table
        theme="balham",
        #    enable_enterprise_modules=True,
        #    height=650,
        width="100%",
        #    reload_data=True
    )

else:
    st.markdown(
        """
        <style>
            section[data-testid="stSidebar"][aria-expanded="true"]{
                display: none;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )
