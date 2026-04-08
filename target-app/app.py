import os
import jwt
from flask import Flask, redirect, url_for, session, request, jsonify
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.secret_key = 'random_secret_key_for_flask_sessions'

# Keycloak OIDC Configuration (Zero Trust Architecture)
KEYCLOAK_URL = 'http://localhost:8080/realms/Infotact'
CLIENT_ID = 'flask-target-app'
CLIENT_SECRET = 'placeholder_secret_from_keycloak_dashboard'

oauth = OAuth(app)
keycloak = oauth.register(
    name='keycloak',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url=f'{KEYCLOAK_URL}/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email roles'},
)

@app.route('/')
def index():
    user = session.get('user')
    if user:
        return f"<h1>Welcome to NexusAuth ZT Protected App</h1><p>Logged in as: {user['preferred_username']}</p><a href='/verify-claims'>Verify JWT Claims (Week 3)</a> | <a href='/logout'>Logout</a>"
    return '<h1>Zero Trust Gateway</h1><a href="/login">Login via Keycloak SSO</a>'

@app.route('/login')
def login():
    redirect_uri = url_for('auth_callback', _external=True)
    return keycloak.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    token = keycloak.authorize_access_token()
    user_info = keycloak.parse_id_token(token)
    session['user'] = user_info
    session['access_token'] = token['access_token']
    return redirect('/')

@app.route('/verify-claims')
def verify_claims():
    """Week 3 Requirement: Decode and inspect live Access Token (JWT) for Role/Group claims"""
    token = session.get('access_token')
    if not token:
        return redirect('/login')
    
    # Decoding JWT without verification strictly for introspection display
    decoded_payload = jwt.decode(token, options={"verify_signature": False})
    
    # Extracting RBAC Roles injected by Keycloak
    realm_roles = decoded_payload.get('realm_access', {}).get('roles', [])
    
    return jsonify({
        "status": "Token Introspection Successful",
        "algorithm": "RS256",
        "extracted_roles": realm_roles,
        "full_jwt_payload": decoded_payload
    })

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('access_token', None)
    return redirect(f'{KEYCLOAK_URL}/protocol/openid-connect/logout?redirect_uri=http://localhost:5000')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)