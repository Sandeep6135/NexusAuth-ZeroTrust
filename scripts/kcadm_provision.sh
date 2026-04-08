#!/bin/bash
# NexusAuth ZT - Automated Realm & Role Provisioning via Keycloak Admin CLI

KEYCLOAK_URL="http://localhost:8080"
ADMIN_USER="admin"
ADMIN_PASS="super_secure_admin_pass"
REALM_NAME="Infotact"

echo "Authenticating with Keycloak..."
docker exec -it nexusauth_idp /opt/keycloak/bin/kcadm.sh config credentials --server $KEYCLOAK_URL --realm master --user $ADMIN_USER --password $ADMIN_PASS

echo "Creating Infotact Realm..."
docker exec -it nexusauth_idp /opt/keycloak/bin/kcadm.sh create realms -s realm=$REALM_NAME -s enabled=true

echo "Creating OIDC Client for Target App..."
docker exec -it nexusauth_idp /opt/keycloak/bin/kcadm.sh create clients -r $REALM_NAME -s clientId="flask-target-app" -s enabled=true -s clientAuthenticatorType="client-secret" -s standardFlowEnabled=true -s directAccessGrantsEnabled=true -s redirectUris='["http://localhost:5000/auth/callback"]'

echo "Creating RBAC Roles (Admin, Developer, Viewer)..."
docker exec -it nexusauth_idp /opt/keycloak/bin/kcadm.sh create roles -r $REALM_NAME -s name=Admin
docker exec -it nexusauth_idp /opt/keycloak/bin/kcadm.sh create roles -r $REALM_NAME -s name=Developer
docker exec -it nexusauth_idp /opt/keycloak/bin/kcadm.sh create roles -r $REALM_NAME -s name=Viewer

echo "Enabling Comprehensive User Event Logging (Week 4 Requirement)..."
docker exec -it nexusauth_idp /opt/keycloak/bin/kcadm.sh update events/config -r $REALM_NAME -s eventsEnabled=true -s adminEventsEnabled=true -s eventsListeners='["jboss-logging"]'

echo "Provisioning Complete. Zero Trust framework initialized."