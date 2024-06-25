import os
from markupsafe import escape
import flask
import requests_oauthlib
from requests_oauthlib.compliance_fixes import facebook_compliance_fix
from flask import jsonify

# Your ngrok url, obtained after running "ngrok http 5000"
#URL = "https://698bde48.ngrok.io"
URL = "http://localhost:5000"

FB_CLIENT_ID = ""
FB_CLIENT_SECRET = ""

FB_AUTHORIZATION_BASE_URL = "https://www.facebook.com/dialog/oauth"
FB_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

FB_SCOPE = ["email","ads_read"]

# This allows us to use a plain HTTP callback
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


app = flask.Flask(__name__)


@app.route("/")
def index():
    return """
    <a href="/fb-login">Login with Facebook</a>
    """


@app.route("/fb-login")
def login():
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, redirect_uri=URL + "/fb-callback", scope=FB_SCOPE
    )
    authorization_url, _ = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)

    return flask.redirect(authorization_url)


@app.route("/fb-callback")
def callback():
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, scope=FB_SCOPE, redirect_uri=URL + "/fb-callback"
    )

    # we need to apply a fix for Facebook here
    facebook = facebook_compliance_fix(facebook)

    token = facebook.fetch_token(
        FB_TOKEN_URL,
        client_secret=FB_CLIENT_SECRET,
        authorization_response=flask.request.url,
    )
    print("printing token")
    print(token)

    # Fetch a protected resource, i.e. user profile, via Graph API
    facebook_user_data = facebook.get(
        "https://graph.facebook.com/me?fields=id,name,email,picture{url}"
    ).json()

    email = facebook_user_data["email"]
    name = facebook_user_data["name"]
    picture_url = facebook_user_data.get("picture", {}).get("data", {}).get("url")
    print("email is"+email)
   
if __name__ == "__main__":
    app.run(debug=True)