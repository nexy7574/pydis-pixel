git clone https://github.com/python-discord/pixels.git 2> /dev/null  # doesn't really matter if
cd pixels || exit 1
echo '# Discord OAuth variables. Create an application at https://discord.com/developers/applications/.
CLIENT_ID=<Discord app client ID>
CLIENT_SECRET=<Discord app client secret>
# Add the redirect BASE_URL/callback to your application, then generate an OAuth2 URL with scopes: identify.
AUTH_URL=<Discord OAuth2 URL>
# The webhook to periodically post the canvas state to
WEBHOOK_URL=<Discord Webhook URL>
# Where the root endpoint can be found.
BASE_URL=http://localhost:8000
# 32 byte (64 digit hex string) secret for encoding tokens. Any value can be used.
JWT_SECRET=c78f1d852e2d5adefc2bc54ed256c5b0c031df81aef21a1ae1720e7f72c2d39
# Used to hide moderation endpoints in Redoc.
PRODUCTION=false' > .env
$EDITOR .env || vim .env || nano .env || exit 1
docker-compose up
