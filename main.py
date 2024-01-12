import streamlit as st
import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# create a Streamlit UI to collect user input
st.set_page_config(page_icon="🚀", page_title="Send EMAILz")


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

# create a Streamlit UI to collect user input
st.title("Send Files by Email")
sender_email = st.text_input("Sender email address", value="roxy@cemm.com")
sender_password = st.text_input("Sender email password", type="password")
primary_recipient = st.text_input(
    "Primary recipient email address", value="apinvoices@ajinomotofoods.com"
)
cc_recipients = st.text_area(
    "CC recipient email addresses (one per line)",
    value="Sally.Kim@ajinomotofoods.com\nAngel.Alvarez@ajinomotofoods.com\nRoxy@cemm.com",
)
uploaded_files = st.file_uploader("Select files to send", accept_multiple_files=True)
email_body = st.text_area("Email body")


def setup_email_client(smtp_server, smtp_port, sender_email, sender_password):
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    return server


def create_email_message(
    sender_email, primary_recipient, cc_recipients, filename, email_body, file_data
):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = primary_recipient
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
    sender_email, sender_password, primary_recipient, cc_recipients, uploaded_files
):
    # set up SMTP server and login credentials
    smtp_server = "smtp.office365.com"
    smtp_port = 587

    # split cc_recipients by newline and strip whitespace
    cc_recipients_list = [email.strip() for email in cc_recipients.split("\n")]
    all_recipients = [primary_recipient] + cc_recipients_list

    try:
        server = setup_email_client(
            smtp_server, smtp_port, sender_email, sender_password
        )

        # iterate over files and send each one in a separate email
        for uploaded_file in uploaded_files:
            filename = uploaded_file.name
            file_data = uploaded_file.read()

            # construct email message
            message = create_email_message(
                sender_email,
                primary_recipient,
                cc_recipients_list,
                filename,
                email_body,
                file_data,
            )
            with st.spinner(
                f"Sending {filename} to {primary_recipient} with {cc_recipients_list} as CCs"
            ):
                send_email(server, sender_email, all_recipients, message)
            st.success(
                f"Sent {filename} to {primary_recipient} with {cc_recipients_list} as CCs"
            )
    except Exception as e:
        st.error(f"An error occurred: {e}")


if st.button("Send Emails"):
    send_emails(
        sender_email, sender_password, primary_recipient, cc_recipients, uploaded_files
    )
