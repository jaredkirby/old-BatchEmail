import streamlit as st
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# Set up Streamlit page configuration
st.set_page_config(page_icon="🚀", page_title="Send EMAILz")

# Define categories and associated email addresses
CATEGORIES = {
    "Taquitos": ["anastasia.balashova@ajinomotofoods.com"],
    "Potstickers/Gyozas": [
        "priya.jani@ajinomotofoods.com",
        "jackie.kim@ajinomotofoods.com",
    ],
    "Mexican": ["anastasia.balashova@ajinomotofoods.com"],
    "Rice": ["doug.biehl@ajinomotofoods.com"],
    "Noodles": ["caleb.park@ajinomotofoods.com"],
}


def get_random_cat_image_url():
    url = "https://api.thecatapi.com/v1/images/search"
    response = requests.get(url)
    json_data = response.json()
    return json_data[0]["url"]


# Fetch cat image URL
cat_image_url = get_random_cat_image_url()

# Display the image centered
st.markdown(
    f'<center><img src="{cat_image_url}" alt="Random cat image" height="300"></center>',
    unsafe_allow_html=True,
)

st.title("Send Lots of Stuff via EMAIL!!!")
code = """
Powered by: The World Wide Webz and Jared <3
"""
st.code(code, language="python")

# Create Streamlit UI to collect user input
st.title("Send Files by Email")
sender_email = st.text_input("Sender email address", value="roxy@cemm.com")
access_password = st.text_input("Access password", type="password")

# Add category selection
selected_categories = st.multiselect(
    "Select invoice categories", options=list(CATEGORIES.keys())
)

# Generate recipient list based on selected categories
primary_recipients = set()
for category in selected_categories:
    primary_recipients.update(CATEGORIES[category])

# Display and allow editing of primary recipient list
st.subheader("Primary Recipients")
primary_recipients = st.text_area(
    "Edit primary recipients (one email per line)", value="\n".join(primary_recipients)
)

# Convert primary recipients back to a list
primary_recipient_list = [
    email.strip() for email in primary_recipients.split("\n") if email.strip()
]

# CC recipients
st.subheader("CC Recipients")
cc_recipients = st.text_area(
    "CC recipient email addresses (one per line)",
    value="Sally.Kim@ajinomotofoods.com\nSuzette.Magpayo@ajinomotofoods.com\nRoxy@cemm.com",
)
cc_recipient_list = [
    email.strip() for email in cc_recipients.split("\n") if email.strip()
]

uploaded_files = st.file_uploader("Select files to send", accept_multiple_files=True)
email_body = st.text_area("Email body")


def setup_email_client(smtp_server, smtp_port, sender_email, sender_password):
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    return server


def create_email_message(
    sender_email, primary_recipients, cc_recipients, filename, email_body, file_data
):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(primary_recipients)
    msg["CC"] = ", ".join(cc_recipients)
    msg["Subject"] = filename

    msg.attach(MIMEText(email_body, "plain"))

    part = MIMEBase("application", "octet-stream")
    part.set_payload(file_data)
    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )

    msg.attach(part)
    return msg.as_string()


def send_email(server, sender_email, recipient_emails, message):
    server.sendmail(sender_email, recipient_emails, message)


def send_emails(
    sender_email,
    access_password,
    primary_recipient_list,
    cc_recipient_list,
    uploaded_files,
):
    # Set up SMTP server and login credentials
    smtp_server = "smtp.office365.com"
    smtp_port = 587

    try:
        # Compare the access password entered by the user with the stored access password
        if access_password == st.secrets["ACCESS_PASSWORD"]:
            sender_password = st.secrets["SENDER_EMAIL_PASSWORD"]
        else:
            sender_password = access_password

        server = setup_email_client(
            smtp_server, smtp_port, sender_email, sender_password
        )

        all_recipients = primary_recipient_list + cc_recipient_list

        # Iterate over files and send each one in a separate email
        for uploaded_file in uploaded_files:
            filename = uploaded_file.name
            file_data = uploaded_file.read()

            # Construct email message
            message = create_email_message(
                sender_email,
                primary_recipient_list,
                cc_recipient_list,
                filename,
                email_body,
                file_data,
            )
            with st.spinner(
                f"Sending {filename} to {', '.join(primary_recipient_list)} with {', '.join(cc_recipient_list)} as CCs"
            ):
                send_email(server, sender_email, all_recipients, message)
            st.success(
                f"Sent {filename} to {', '.join(primary_recipient_list)} with {', '.join(cc_recipient_list)} as CCs"
            )
    except Exception as e:
        st.error(f"An error occurred: {e}")


if st.button("Send Emails"):
    send_emails(
        sender_email,
        access_password,
        primary_recipient_list,
        cc_recipient_list,
        uploaded_files,
    )
