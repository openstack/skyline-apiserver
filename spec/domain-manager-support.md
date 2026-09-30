# Domain Manager Support

## Introduction

Keystone's default policies (2024.2 and later) define a *domain manager* persona: a user with the
`manager` role on a domain manages the users, groups and projects of that domain and assigns a
restricted set of roles there, without cloud-admin rights. Every rule of that persona is written
against `token.domain.id`, so it only applies to **domain-scoped** tokens.

Skyline issues project-scoped tokens only. A domain manager logged in to Skyline gets a token that
Keystone rejects for the identity operations the persona exists for (`POST /v3/users` answers 403
through Skyline's own proxy), and the console has no identity pages outside the Administrator
platform, which is gated on `system_admin_roles`.

This spec describes domain manager support in skyline-apiserver: acquisition of a domain-scoped
token at login, its presence in the session and profile, and policy evaluation with domain scope.
The matching skyline-console change (a "Domain" area for users, groups and projects of the user's
own domain) is tracked separately. Both were implemented and verified end to end on a 2026.1
deployment (Keystone 29) before this spec was written; the design below is the one that works.

## Problem Description

1. `login`, `login/totp` and `websso` obtain an unscoped token and then a project-scoped token
   (`get_project_scope_token`). No domain-scoped token is ever requested, although Keystone lists
   the domains a user may scope to (`GET /v3/auth/domains`) exactly like `GET /v3/auth/projects`,
   which Skyline already uses.

2. `GET /api/v1/policies` evaluates the rules with a project-scoped context. It already re-scopes
   the user's token to *system* scope to detect system administrators, but there is no *domain*
   counterpart, so every `identity:*` rule of the domain manager persona evaluates to false.

3. The bundled copy of the Keystone policies (`policy/manager/keystone.py`) predates the domain
   manager persona: none of its rules mentions the `manager` role, so even a correct domain-scoped
   evaluation would deny everything.

4. skyline-console has no user-facing identity pages; the usual workarounds are Horizon with
   `OPENSTACK_KEYSTONE_MULTIDOMAIN_SUPPORT` or the CLI with `--os-domain-name`.

## Use Cases

**Customer domain manager (one Keystone domain per customer)**

- After logging in, see and manage the users, groups and projects of my domain, and assign the
  roles Keystone lets me assign (`manager`, `member`, `reader`) on my projects, without the cloud
  operator.
- Never see users, projects or domains of other customers, and never be offered what Keystone
  forbids (the dashboard must not advertise what Keystone refuses).

**Cloud operator**

- Choose which roles enable the domain self-service area (default `manager`), the same way
  `system_admin_roles` chooses who gets the Administrator platform.

**Everybody else**

- Users without domain role assignments see no change: no extra token, no new menu.

## Proposed Change

1. **Domain-scoped token at login.** After the unscoped token is obtained, list the domains it can
   scope to (`GET /v3/auth/domains`, enabled ones only). If the user's own domain is among them,
   request a domain-scoped token for it with the same pattern as the project-scoped token
   (`keystoneauth1.identity.v3.Token` with `domain_id`). Users without domain assignments get
   nothing, and any Keystone failure on this path is logged at debug level and ignored: it never
   blocks the login. `login` and `login/totp` pick the user's login domain; `websso` takes the
   first domain listed.

2. **Session and profile.** The domain-scoped token travels in the session JWT
   (`Payload.domain_scope_token`, optional) so that it survives the profile regeneration done by
   the request middleware and the token renewal. `generate_profile` validates it with Keystone and
   fills `Profile.domain`, `Profile.domain_roles` and `Profile.domain_scope_token_exp`; a token
   that is no longer valid is simply dropped from the profile. `switch_project` and
   `switch_region` keep it (it does not depend on the project or the region); `logout` revokes it
   together with the project-scoped token.

3. **Policies.** `GET /policies` and `POST /policies/check` evaluate the rules of
   `DOMAIN_SCOPE_SERVICES` (Keystone) a second time when the session carries a domain-scoped
   token. The credentials come from re-authenticating that token **with** `domain_id` (a bare token
   auth would re-scope to the default project) and carry a nested `token.domain.id` entry, because
   oslo.policy resolves dotted credential keys through nested lookups. The target maps every
   `*.domain_id` key to the user's domain and sets `target.role.name` to `member`, the least
   privileged role a manager may grant, so that grant rules get a meaningful generic answer. A rule
   is allowed when either scope allows it.

4. **Bundled Keystone rules.** `policy/manager/keystone.py` is regenerated from Keystone 2026.1 so
   that the `manager` clauses exist.

5. **Configuration.** `openstack.domain_manager_roles` (default `["manager"]`), exposed by
   `GET /config`, tells the console which roles of the domain-scoped token enable the domain area.

6. **Proxy.** No change: the console sends the domain-scoped token in `X-Auth-Token` for its
   identity requests; nginx forwards headers as it does today.

## Key Design Decisions

**Two tokens in the session, not one.** Keystone tokens have exactly one scope. Compute, network
and storage calls need the project-scoped token; identity calls of the domain area need the
domain-scoped one. The console decides per request.

**Re-scoping keeps the domain.** `Token(auth_url, token)` without a scope makes Keystone issue a
token scoped to the user's default project; the domain-scoped evaluation must pass `domain_id`.
This was the root cause of the first implementation attempt returning `False` for
`identity:list_users` and `identity:create_project`.

**Keystone stays the enforcement point.** The dashboard only hides what the evaluation reports as
denied; every identity request is authorised by Keystone with the domain-scoped token. A
misconfigured `domain_manager_roles` shows menus that Keystone will then refuse, nothing more.

**Same shape as the system-scope check.** The domain evaluation mirrors the existing
`get_system_scope_access` path in `list_policies`, keeping the enforcers and `_generate_target` as
the single source of truth.

## Alternatives

1. **Horizon with multidomain support**: works (Horizon acquires a domain-scoped token at login),
   but needs a second dashboard and a custom `keystone_policy.yaml` accepting `manager`; it is the
   workaround used until this change lands.
2. **Proxying identity calls through skyline-apiserver** with on-the-fly re-scoping: a larger API
   surface and a double hop per identity call, for no functional gain over sending the
   domain-scoped token from the console.
3. **Granting customers `admin` on their domain**: rejected; with the default policies `admin` on
   any target is treated as cloud administrator by most services, which is what the `manager`
   persona exists to avoid.

## Data Model Impact

None in the database. The session payload gains the optional `domain_scope_token`.

## REST API Impact

| Endpoint                 | Method | Change   | Notes                                                             |
|--------------------------|--------|----------|-------------------------------------------------------------------|
| `/login`, `/login/totp`, `/websso` | POST | Extended | may acquire a domain-scoped token; request unchanged          |
| `/profile`               | GET    | Extended | `domain_scope_token`, `domain`, `domain_roles`, `domain_scope_token_exp` (all optional) |
| `/switch_project`, `/switch_region` | POST | Extended | keep the domain-scoped token                                |
| `/logout`                | POST   | Extended | revokes the domain-scoped token too                               |
| `/policies`, `/policies/check` | GET/POST | Extended | Keystone rules also evaluated with domain scope             |
| `/config`                | GET    | Extended | adds `domain_manager_roles`                                       |

All new fields are optional; clients that ignore them behave as before.

## Security Impact

- The domain-scoped token is handled exactly like the project-scoped one (signed session payload,
  `X-Auth-Token` from the browser). It carries only the user's own domain roles; Keystone's
  `domain_managed_target_role` rule prevents granting `admin`, and other domains stay invisible
  (403 or filtered lists), as verified against Keystone 29.
- No new call is made with the Skyline system user.
- Logout revokes both tokens.

## Performance Impact

One extra `GET /v3/auth/domains` per login and, for users with domain assignments, one extra token
request. Policy evaluation runs the Keystone rule set twice only for those users.

## Other Deployer Impact

New optional setting `openstack.domain_manager_roles` in `skyline.yaml` (default `["manager"]`).
Deployments whose Keystone predates the domain manager persona keep working: without domain
assignments there is no domain-scoped token and no new menu.

## Developer Impact

skyline-console (separate change): the root store keeps the domain-scoped token and decides,
synchronously from the profile at login, whether the user is a domain manager (the pages fire
their requests before the asynchronous role probes finish); the request layer sends that token on
Keystone URLs for such users; a "Domain" menu block (Users, Projects, User Groups) reuses the
existing identity pages through their non-admin routes, with the user's domain preselected in the
forms and the system-scope and quota actions hidden.

## Implementation

### Assignee(s)

Primary assignee: dgines

### Work Items

1. `client/openstack/system.py`: `get_scope_domains()` and `get_domain_scope_token()`.
2. `schemas/login.py`: `Payload.domain_scope_token`; `Profile.domain`, `domain_roles`,
   `domain_scope_token_exp`; `Config.domain_manager_roles`.
3. `core/security.py`: carry and validate the domain-scoped token in `parse_access_token`,
   `generate_profile_by_token` and `generate_profile`.
4. `api/v1/login.py`: `_get_domain_scope_token()`; acquisition in `_build_profile_from_unscope`,
   `_finish_login` and `websso`; propagation in `switch_project`/`switch_region`; revocation in
   `logout`; `domain_manager_roles` in `get_config`.
5. `api/v1/policy.py`: `_generate_domain_target()`, `_domain_user_context()`, `_authorize()`.
6. `config/openstack.py`: `domain_manager_roles`.
7. `policy/manager/keystone.py`: regenerated from Keystone 2026.1.
8. Unit tests (`tests/unit/api/v1/test_domain_manager.py`) and release note.

## Dependencies

Keystone 2024.2+ default policies. No new Python dependencies.

## Testing

- Unit: session payload round trip, profile with valid / invalid / absent domain-scoped token,
  token acquisition (own domain, no assignment, other domain only, disabled domain, Keystone
  failure), config, domain target, domain context (re-auth with `domain_id`, nested `token`
  credentials), authorization fallback limited to Keystone.
- Functional (done on 2026.1, Keystone 29, default policies): a `manager` of domain `d1` logs in;
  the profile carries the domain-scoped token with roles `manager, member, reader`; `/policies`
  allows `identity:create_user`, `list_users`, `create_project`, `create_group`, `create_grant`,
  `list_role_assignments` and denies `create_domain`/`update_domain`; through the proxy,
  `POST /v3/users` in `d1` returns 201 with the domain-scoped token and 403 with the project-scoped
  one, granting `member` returns 204, the token is revoked at logout.
- Console end to end (Chromium): the manager sees only the users of the own domain, creates a user
  with project and role and deletes it from the UI; an administrator and a plain `member` see no
  "Domain" area.

## Documentation Impact

Configuration reference (`domain_manager_roles`); user guide section on managing the own domain.

## References

- Keystone, Domain Manager Usage: https://docs.openstack.org/keystone/latest/user/domain-manager-usage.html
- Keystone, Service API protection: https://docs.openstack.org/keystone/latest/admin/service-api-protection.html
- Bug #2013056, Skyline system scope support: https://bugs.launchpad.net/skyline-console/+bug/2013056
- SCS standard scs-0302, Domain Manager configuration for Keystone: https://docs.scs.community/standards/scs-0302-v1-domain-manager-role/
