import streamlit as st
import base64
import psycopg2
import streamlit_authenticator as stauth
from psycopg2 import Error
from werkzeug.security import generate_password_hash, check_password_hash
from st_pages import add_page_title

st.set_page_config(
    page_icon="🧊",
)


@st.cache_resource
def create_connection():
    return psycopg2.connect(**st.secrets["postgres"])


conn = create_connection()


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

names_list, authentication_status, user_names_list = authenticator.login(
    "Login", "main"
)

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:
    authenticator.logout("Logout", "sidebar")
    add_page_title({"Password Reset"})

    # Show logo
    def get_base64_of_bin_file(png_file):
        with open(png_file, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()

    def build_markup_for_logo(
        png_file,
        background_position="50% 10%",
        margin_top="15%",
        margin_bottom="10%",
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
                        margin_bottom: %s;
                        background-size: %s %s;
                    }
                </style>
                """ % (
            binary_string,
            background_position,
            margin_top,
            margin_bottom,
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
    user_name = user_names_list
    if user_name == "admin":
        st.markdown(
            """<style>[data-testid="stSidebarNav"] {padding-top: 30%;}</style>""",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """<style>[data-testid="stSidebarNav"] {padding-top: 20%;}</style>""",
            unsafe_allow_html=True,
        )
    username = st.text_input("Username")
    old_password = st.text_input("Old Password", type="password")
    new_password = st.text_input("New Password", type="password")
    repeat_password = st.text_input("Repeat Password", type="password")
    reset_button = st.button("Reset Password")

    if reset_button:
        conn = create_connection()
        cursor = conn.cursor()

        # Check if the username exists in the database
        cursor.execute(
            "SELECT password FROM tbl_acl WHERE tbl_acl.user = %s", (username,)
        )
        result = cursor.fetchone()

        if result:
            stored_password = result[0]
            # if check_password_hash(stored_password, old_password):
            if old_password == stored_password:
                if new_password == repeat_password:
                    try:
                        # hashed_password = generate_password_hash(new_password)
                        # Update the password in the database
                        cursor.execute(
                            "UPDATE tbl_acl SET password = %s WHERE tbl_acl.user = %s",
                            (new_password, username),
                        )
                        conn.commit()
                        st.success("Password reset successful!")
                    except Error as e:
                        st.error("Error occurred while resetting the password.")
                        print(e)
                else:
                    st.warning("New password and Repeat password do not match.")
            else:
                st.warning("Old password is incorrect.")
        else:
            st.warning("Username not found in the database.")

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
