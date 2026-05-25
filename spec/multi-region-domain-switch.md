# Multi-Region Domain Switch

## Introduction

Skyline currently requires users to select a region during login. After login,
users cannot switch to another region without re-login. This design document
proposes to remove the region selection from the login page and allow users to
switch regions from the header after login.

This spec only covers the skyline-apiserver side changes. The skyline-console
side changes are handled separately.

## Problem Description

1. Skyline requires users to select a region during login. Users who need to
   access multiple regions must maintain multiple accounts or re-login to switch
   regions, which is inconvenient.

2. Skyline does not support switching domains after login. Users with resources
   across multiple domains cannot conveniently switch between them.

## Use Cases

**End User**

- As an end user, after logging in with my domain credentials, I want to
  switch to another region from the header so that I can access resources in
  that region without re-login.

- As an end user, after logging in, I want to switch between projects in
  different domains through a single project switcher, without a separate
  domain switch operation.

**Deployer**

- As a deployer, I want to configure a default region so that users can log
  in without selecting a region.

## Proposed Change

This spec covers the backend changes in skyline-apiserver only.

The proposed changes are:

1. Remove region selection from login: the backend will always use the
   configured `default_region` instead of accepting region from the login
   request.

2. The login credential schema will make `domain` optional, defaulting to
   the configured `user_default_domain`.

3. A new `POST /switch_region/{region}` API will be added to switch the
   current region. This operation is lightweight: it does not re-scope the token
   or re-authenticate. It only updates the `profile.region` field and
   regenerates the endpoints from the new region's catalog.

4. The `GET /profile` API will be extended with two new fields:

   - `regions`: a list of region IDs the current user can access, computed
     from the user's token catalog (not the system user catalog).

   - `projects`: each project entry will include `domain_name` in addition to
     `domain_id`, sourced directly from the Keystone project object with zero
     extra API calls.

5. The `POST /switch_project/{project_id}` API will be enhanced with a
   pre-validation check to verify the project belongs to the current user
   before attempting to re-scope the token.

## Key Design Decisions

**Region switching does not re-scope the token**

A Keystone scoped token is valid across all regions within the same Keystone.
The `profile.region` field determines which region's catalog is used for
endpoint resolution. Switching regions only updates this field and regenerates
the endpoints; no re-scope or re-authentication is required. This makes
region switching lightweight.

**Projects carry domain information**

The Keystone `projects.list(user=user)` response includes the project object
with a nested `domain` object containing both `id` and `name`. The backend
will include `domain_name` in the projects dictionary at no additional API
cost. This enables the frontend to display and filter projects by domain
without a separate domain switch operation.

**No separate domain switch**

Switching a project automatically carries the correct `project_domain_id`
because Keystone token scoping uses the project's domain implicitly. There is
no need for a separate domain switch operation.

## Alternatives

**Region endpoints map in profile**

An alternative approach would be to return all region-endpoints mappings in
the profile and let the frontend store the current region. However, this would
require changing all OpenStack client calls to accept region from the request
context rather than from the JWT `profile.region`. This is a much larger
architectural change and is out of scope for this spec.

## Data Model Impact

None. No database schema changes are required.

## REST API Impact

| API                               | Method | Change    | Notes                                   |
|-----------------------------------|--------|-----------|-----------------------------------------|
| `/login`                          | POST   | Modified  | region field ignored; domain optional    |
| `/switch_region/{region}`         | POST   | New       | lightweight region switch                |
| `/switch_project/{project_id}`    | POST   | Enhanced  | adds project ownership pre-check         |
| `/profile`                        | GET    | Extended  | adds regions list and domain_name       |
| `/config`                         | GET    | Extended  | may add default_region                   |

Details:

1. `POST /login`: the `Credential` schema will make `domain` optional. The
   `region` field, if provided by the frontend, will be ignored; the backend
   will always use `default_region`.

2. `POST /switch_region/{region}` (new): accepts a region ID in the URL
   path. Validates the region exists in the user's accessible region list.
   Generates a new profile with the target region, regenerates endpoints, and
   returns the updated profile with a new JWT cookie. This operation does
   not re-scope the token.

3. `POST /switch_project/{project_id}` (enhanced): adds a pre-validation
   check that verifies `project_id` exists in `profile.projects` before
   attempting to re-scope the token.

4. `GET /profile` (extended): adds `regions` field (`List[str]`) computed
   from the user's token catalog. Each project in the `projects` dictionary
   gains a `domain_name` (`str`) field.

5. `GET /config` (extended): may add `default_region` to its response for
   frontend documentation purposes.

## Security Impact

None. Region switching uses the existing scoped token which remains valid. Roles
and permissions are unchanged because they are bound to the project scope, not
the region.

## Performance Impact

Negligible. Region switching only involves regenerating the endpoint dictionary
and writing a new JWT cookie. No re-authentication or token re-scoping is
performed.

## Other Deployer Impact

None. The existing configuration options (`default_region`, `user_default_domain`,
`nginx_prefix`) continue to work as-is. No new configuration options are
required for this spec.

## Developer Impact

Developers integrating with the new `switch_region` endpoint should be aware
that the operation does not invalidate or reissue the underlying Keystone
token; only the Skyline JWT cookie and the `profile.region` field are updated.

## Implementation

### Assignee(s)

TBD.

### Work Items

1. Modify `POST /login` to ignore the `region` field from the request and
   always use `default_region`.

2. Modify the `Credential` schema to make `domain` optional.

3. Add `POST /switch_region/{region}` endpoint in
   `skyline_apiserver/api/v1/login.py`.

4. Enhance `POST /switch_project/{project_id}` with a project ownership
   pre-check using the `profile.projects` dictionary.

5. Extend `GET /profile` to compute and return `regions` from the user's
   token catalog and add `domain_name` to each project entry.

6. Add unit tests for the new and modified endpoints.

## Dependencies

None. This spec does not introduce new dependencies beyond the existing
keystoneauth1 and keystoneclient libraries.

## Testing

Unit tests will be added to cover:

- Login ignoring the region field from the request.
- Region switching validates the region is in the accessible list.
- Region switching does not re-scope the token.
- Project switch pre-validation rejects unauthorized projects.
- Profile includes `regions` and `domain_name` fields correctly.

## Documentation Impact

The API documentation should be updated to reflect:

- The `region` field in login requests is ignored.
- The new `switch_region` endpoint.
- The new fields in the `profile` response.
- The optional `domain` in login credentials.

## References

- Keystone Token Scoping:
  https://docs.openstack.org/keystone/latest/api/token-scoping.html

- keystoneauth1 Token auth:
  https://docs.openstack.org/keystoneauth/latest/using-tokens.html

## History

None.
