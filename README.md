# Project 3: Centralized Zero Trust Identity Architecture (IAM)
**Product Brand Name:** NexusAuth ZT  
[cite_start]**Domain:** Identity and Access Management (IAM) [cite: 28]

## Overview
[cite_start]NexusAuth ZT addresses organizational credential fatigue and inconsistent security policies across siloed internal applications[cite: 78]. [cite_start]This repository provisions a centralized **One Identity** ecosystem powered by Keycloak[cite: 78, 28]. [cite_start]It rigorously enforces Conditional Multi-Factor Authentication (MFA) and fine-grained Role-Based Access Control (RBAC)[cite: 79].

## Architecture & Features
* [cite_start]**OIDC (OpenID Connect):** Implements modern token-based authentication (JWTs) as the standard for target applications[cite: 84].
* [cite_start]**Conditional MFA:** Policy enforcement requiring TOTP/WebAuthn when users authenticate from untrusted contexts (e.g., unknown IP/device)[cite: 85].
* [cite_start]**Federated Identity:** Capability to bridge identity stores (e.g., Google Workspace) via identity brokering[cite: 28, 86].
* [cite_start]**Auditing & Hardening:** Automated deployment of comprehensive user event logging (success/failure, MFA registrations) to monitor for policy violations.

## Deployment Instructions
1. [cite_start]Run `docker-compose up -d` to launch the Keycloak & Postgres infrastructure.
2. Execute `scripts/kcadm_provision.sh` to automatically build the Infotact Realm, OIDC clients, and RBAC roles via the Keycloak Admin CLI.
3. [cite_start]Install dependencies in `target-app/requirements.txt` and run `app.py` to test the SSO login flow and JWT claim introspection.