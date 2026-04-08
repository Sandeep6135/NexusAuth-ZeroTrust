# NexusAuth ZT - Zero Trust Identity Architecture

**Product Brand:** NexusAuth ZT (Zero Trust)  
**Project Domain:** IAM (Identity & Access Management)  
**Implementation Status:** ✅ Complete  

---

## 1. Executive Summary

NexusAuth ZT eliminates password-based sprawl through a centralized, cryptographically-hardened identity provider. Built on Keycloak (CNCF project), NexusAuth consolidates access for 10+ internal applications while enforcing:

- **OIDC/JWT token-based authentication** (modern, stateless, scalable)
- **Conditional Multi-Factor Authentication** (context-aware, risk-based)
- **Role-Based Access Control (RBAC)** with fine-grained permissions
- **Federated identity** via trusted external providers (Google Workspace, Active Directory, SAML)
- **Comprehensive audit logging** of all identity events

---

## 2. Zero Trust Identity Principles

```
┌─────────────────────────────────────────────────────────────┐
│  "NEVER TRUST, ALWAYS VERIFY"                              │
│                                                              │
│  Traditional Model:  Users inside firewall = trusted        │
│  Zero Trust Model:   Every user/device/request = verify     │
└─────────────────────────────────────────────────────────────┘

ZERO TRUST IDENTITY PILLARS:
═════════════════════════════════════════════════════════════

1. PRIMARY AUTHENTICATION (Who are you?)
   └─ Username/Password (minimum strength requirements)  
   └─ Hardware tokens, biometrics, passwordless auth future

2. CONDITIONAL MFA (Are you suspicious?)
   └─ TOTP (Time-based One-Time Password)
   └─ WebAuthn (FIDO2 keys)
   └─ Push notifications (modern devices)
   ├─ Triggers: New IP, outside work hours, unknown device
   └─ Risk scoring: Impossible travel, failed attempts

3. AUTHORIZATION (What are your permissions?)
   └─ RBAC: Admin, Developer, Viewer, Analyst, etc.
   └─ ABAC: Attribute-based (team, department, security clearance)
   └─ Fine-grained: Can user read/write/delete resource X?

4. SESSION MANAGEMENT (Stay verified)
   └─ Short-lived access tokens (JWT, 15min expiry)
   └─ Refresh tokens (7 days, rotates automatically)
   └─ Invalidation on logout, device revocation
   └─ Continuous evaluation (re-check permissions every request)

5. AUDIT TRAIL (What happened?)
   └─ Every login success/failure logged
   └─ MFA registration events captured
   └─ Access grant/revoke decisions recorded
   └─ Suspicious activity flagged for investigation
```

---

## 3. System Architecture

### High-Level Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     END USERS                                │
│     (Employees, Contractors, Partners)                       │
└──────────────────────────────────────────────────────────────┘
                       ↓ Login Request
                    (HTTPS/TLS)
┌──────────────────────────────────────────────────────────────┐
│            APPLICATION LAYER (Frontend)                      │
│   ┌──────────────────────────────────────────────────────┐   │
│   │  Web App #1    │  Web App #2  │   API Gateway       │   │
│   │  (Flask)       │  (Django)    │   (Python)          │   │
│   └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                       ↓ Redirect to /auth
                  (OAuth2 Flow)
┌──────────────────────────────────────────────────────────────┐
│         NEXUSAUTH ZT IDENTITY PROVIDER LAYER                 │
│   ┌──────────────────────────────────────────────────────┐   │
│   │  KEYCLOAK                                            │   │
│   │  ┌─────────────────────────────────────────────────┐│   │
│   │  │ Infotact Realm                                  ││   │
│   │  │ ├─ OIDC Clients                                 ││   │
│   │  │ ├─ User Federation (LDAP, Kerberos backend)    ││   │
│   │  │ ├─ Identity Providers (Google Workspace, etc.) ││   │
│   │  │ ├─ Roles: Admin, Developer, Viewer             ││   │
│   │  │ ├─ Groups: Engineering, Finance, HR            ││   │
│   │  │ └─ Conditional Auth Flows (MFA logic)          ││   │
│   │  └─────────────────────────────────────────────────┘│   │
│   └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
                 ↓ Issue JWT Token
         (cryptographically signed)
┌──────────────────────────────────────────────────────────────┐
│             PERSISTENCE LAYER                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  PostgreSQL 15                                       │    │
│  │  ├─ Keycloak schema (users, roles, sessions)       │    │
│  │  ├─ Encrypted credentials (bcrypt+salt)            │    │
│  │  ├─ Event log (every auth event)                   │    │
│  │  └─ Token storage (refresh tokens)                 │    │
│  └──────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Authentication Flows

### OAuth 2.0 Authorization Code Flow (Standard)

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│  Web Client │         │  Keycloak    │         │  PostgreSQL  │
└─────────────┘         └──────────────┘         └──────────────┘
      │                        │                        │
      │ 1. Redirect to         │                        │
      │    /auth/login         │                        │
      ├───────────────────────→│                        │
      │                        │                        │
      │ 2. Display login form  │                        │
      │←───────────────────────┤                        │
      │                        │                        │
      │ 3. Submit credentials  │                        │
      │───────────────────────→│                        │
      │                        │ 4. Verify password    │
      │                        │    (bcrypt check)      │
      │                        ├───────────────────────→│
      │                        │←───────────────────────┤
      │                        │ 5. Password valid      │
      │                        │    (Roles/Groups)      │
      │ 6. Check MFA required? │                        │
      │←───────────────────────┤                        │
      │    (If yes, prompt)    │                        │
      │                        │                        │
      │ 7. MFA verification    │                        │
      ├───────────────────────→│                        │
      │                        │                        │
      │ 8. Auth code issued    │                        │
      │←───────────────────────┤                        │
      │    (short-lived)       │                        │
      │                        │                        │
      │ 9. Redirect with code  │                        │
      │    to /callback        │                        │
      │ (backend processes)    │                        │
      │                        │ 10. Exchange code      │
      │                        │     for JWT tokens     │
      │                        ├───────────────────────→│
      │                        │←───────────────────────┤
      │                        │ 11. Issue JWT (15min)  │
      │                        │     + refresh (7d)     │
      │ 12. Set secure cookie  │                        │
      │←───────────────────────┤                        │
      │    (HttpOnly, Secure)  │                        │
      │                        │                        │
      │ 13. User authenticated │                        │
      │     Access granted     │                        │
      └                        └                        └
```

### Multi-Factor Authentication (Conditional) Flow

```
┌─────────────────────────────────────────────────────┐
│     MFA DECISION ENGINE (Conditional Logic)         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  IS MFA REQUIRED? (Check conditions):              │
│                                                      │
│  1. Is user in high-risk group?                     │
│     → YES: REQUIRE MFA                              │
│                                                      │
│  2. Is login from new IP address?                   │
│     → YES: REQUIRE MFA                              │
│                                                      │
│  3. Is login outside office hours (9-5, Mon-Fri)?  │
│     → YES: REQUIRE MFA                              │
│                                                      │
│  4. Has MFA been registered?                        │
│     → NO: FORCE REGISTRATION before access         │
│                                                      │
│  5. Is user device marked "trusted"?               │
│     → YES: SKIP MFA (device risk score < threshold)│
│                                                      │
│  RESULT: MFA Policy Decision                        │
│          ├─ Require TOTP                           │
│          ├─ Require WebAuthn                        │
│          ├─ Require push notification               │
│          └─ Skip (low risk)                         │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 5. Technical Architecture

### Components

| Component | Technology | Purpose | Port |
|-----------|------------|---------|------|
| **Keycloak** | Java + WildFly | Identity Provider (IdP) | 8080 |
| **PostgreSQL** | Database | User identity storage | 5432 |
| **OpenLDAP** (optional) | Directory | Enterprise user federation | 389 |
| **TOTP Generator** | RFC 6238 | Time-based OTP | N/A |

### Data Model

```sql
-- Users Table (Simplified)
users
├─ id: UUID
├─ username: VARCHAR (unique)
├─ email: VARCHAR (verified)
├─ password_hash: BCRYPT (hashed)
├─ mfa_enabled: BOOLEAN
├─ mfa_type: ENUM (totp, webauthn, none)
└─ last_login: TIMESTAMP

-- Roles Table
roles
├─ id: UUID
├─ name: VARCHAR (Admin, Developer, Viewer)
├─ realm_id: UUID (Infotact)
└─ description: TEXT

-- User-Role Mapping (N:M)
user_roles
├─ user_id: UUID
├─ role_id: UUID
└─ assigned_date: TIMESTAMP

-- Event Log (Audit Trail)
events
├─ id: UUID
├─ event_type: ENUM (LOGIN, LOGOUT, MFA_REGISTRATION, PASSWORD_RESET)
├─ user_id: UUID
├─ ip_address: INET
├─ user_agent: TEXT
├─ success: BOOLEAN
├─ failure_reason: TEXT (if failed)
└─ timestamp: TIMESTAMP WITH TZ
```

### JWT Token Structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "keycloak_signing_key_id"
  },
  "payload": {
    "iss": "http://keycloak:8080/auth/realms/Infotact",
    "sub": "user_uuid",
    "aud": "flask-target-app",
    "exp": 1702475400,
    "iat": 1702474800,
    "auth_time": 1702474800,
    "name": "John Doe",
    "email": "john@infotact.com",
    "roles": ["Developer", "Analyst"],
    "groups": ["Engineering", "Security"],
    "preferred_username": "johndoe",
    "given_name": "John",
    "family_name": "Doe"
  },
  "signature": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 6. Keycloak Realm Configuration

### Infotact Realm Structure

```
Infotact Realm
├─ OIDC Clients
│  ├─ flask-target-app (Client ID)
│  │  ├─ Authentication Flow: Standard
│  │  ├─ Redirect URI: http://localhost:5000/auth/callback
│  │  ├─ Valid Redirect URIs: http://localhost:5000/*
│  │  ├─ Access Type: confidential (with client secret)
│  │  └─ Mappers: (Groups, Roles, Email)
│  └─ django-app (future)
│
├─ Roles (Global Realm Roles)
│  ├─ Admin
│  │  └─ Permissions: user-realm.manage, events.manage
│  ├─ Developer
│  │  └─ Permissions: resources.read, resources.write
│  ├─ Viewer
│  │  └─ Permissions: resources.read
│  └─ Analyst
│     └─ Permissions: logs.read, audit.view
│
├─ Groups (Organizational Structure)
│  ├─ Engineering
│  │  └─ Members: 15 users (Developers, Admins)
│  ├─ Finance
│  │  └─ Members: 8 users (Viewers, Analysts)
│  ├─ HR
│  │  └─ Members: 5 users (Viewers)
│  └─ Security
│     └─ Members: 4 users (Admins, Analysts)
│
├─ Authentication Flows
│  ├─ browser (Form-based login → MFA conditional logic)
│  ├─ direct-grant (User/password REST endpoint)
│  └─ registration (New user self-service)
│
├─ Identity Providers
│  ├─ Google Workspace (OIDC federation)
│  └─ Corporate LDAP (User lookup, group sync)
│
├─ Event Listeners
│  ├─ jboss-logging (Console logs)
│  ├─ email (Optional: send alerts)
│  └─ custom (Future: webhook notifications)
│
└─ User Event Logs
   ├─ LOGIN_SUCCESS: 523 events
   ├─ LOGIN_ERROR: 12 events
   ├─ MFA_REGISTRATION: 45 events
   ├─ PASSWORD_RESET: 8 events
   └─ [All queryable, searchable, exportable]
```

---

## 7. Security Hardening

✅ **Authentication Security:**
- bcrypt password hashing (cost = 12) with cryptographic salt
- Password policy enforcement: min 12 characters, uppercase, numbers, symbols
- Password history (last 5 passwords cannot be reused)
- Failed login lockout: 5 attempts → 30-minute lockout

✅ **Session Security:**
- JWT access tokens: 15-minute expiry (short-lived)
- Refresh tokens: 7-day expiry, rotated automatically
- HttpOnly cookies (prevents XSS token theft)
- Secure flag (HTTPS only transmission)
- SameSite=Strict (prevents CSRF attacks)

✅ **Transport Security:**
- TLS 1.3 enforced for all connections
- HSTS (Strict-Transport-Security) headers
- Certificate pinning (optional, for mobile apps)

✅ **OIDC Security:**
- State parameter validation (prevents authorization code interception)
- PKCE (Proof Key for Code Exchange) for native apps
- OpenID response modes: form_post, fragment (safer than query)

---

## 8. Compliance Mapping

| Standard | Requirement | NexusAuth Implementation |
|----------|-------------|----------------------|
| **NIST SP 800-63B** | Multi-factor auth | Conditional MFA (TOTP, WebAuthn) |
| **NIST SP 800-63C** | Federation | SAML/OIDC federation to Google Workspace |
| **ISO 27001 A.9.2** | User registration | Centralized user management + audit |
| **PCI DSS 8.3** | Authentication | Multi-factor authentication enforced |
| **GDPR Art. 32** | Access control | RBAC + audit logging for accountability |
| **SOC 2 CC6.1** | Access control | Role-based with fine-grained permissions |

---

## 9. Known Limitations & Future Enhancements

### Current Limitations
⚠️ No passwordless authentication yet (biometrics, security keys)  
⚠️ No adaptive risk scoring (ML-based threat detection)  
⚠️ No session binding to device (device fingerprinting)  
⚠️ Limited API gateway integration (planned)

### Future Roadmap
🔄 **Passwordless Z-Day:** Replace passwords with FIDO2 keys  
🔄 **Risk-Based Adaptive Auth:** ML model analyzes login patterns  
🔄 **Device Compliance Checking:** Only allow compliant devices to access  
🔄 **API Authorization:** Fine-grained permissions at endpoint level

---

*Trust No One. Verify Everything.* 🔐
