# Testing Strategy Constraint Template

## Document Control

- Document ID `[required]`: `testing-core`
- Owner `[required]`: `[engineering lead or QA owner]`
- Last validated `[required]`: `YYYY-MM-DD`
- Stability class `[required]`: `mixed`

## 1. Scope `[required]`

Example:
`Applies to backend API services, background jobs, infrastructure checks, and repository CI gates.`

## 2. Test Pyramid Targets `[required]`

| Test Type | Target Range | Notes |
|---|---|---|
| `Unit` | `60% to 75%` | `Fast behavioral coverage for pure logic and service methods` |
| `Integration` | `20% to 30%` | `Database, queue, and API boundary checks` |
| `E2E` | `5% to 10%` | `Critical journey coverage only` |

## 3. Coverage Thresholds by Module Type `[required]`

| Module Type | Line Coverage Floor | Branch Coverage Floor | Notes |
|---|---|---|---|
| `Domain services` | `85%` | `75%` | `Public methods must be directly exercised` |
| `Controllers/handlers` | `80%` | `70%` | `Validation and auth paths required` |
| `Migrations` | `N/A` | `N/A` | `Use migration verification criteria instead` |

## 4. Test Data Management Strategy `[required]`

Example:
- `Integration tests use disposable local databases seeded from committed fixtures.`
- `No tests may depend on mutable shared remote environments.`

## 5. Forbidden Test Patterns `[required]`

Example:
- `Tests hitting production infrastructure are forbidden.`
- `Tests asserting only status code without response body semantics are insufficient for contract behavior.`
- `Sleeping for eventual consistency without timeout rationale is forbidden.`

## 6. CI Gate Requirements `[required]`

Example:
- `Unit and integration suites must pass before merge.`
- `E2E smoke suite must pass on main before deployment promotion.`
- `Coverage regression below floor blocks merge.`

## 7. Mutation Testing Requirements `[required]`

Example:
- `Required: yes`
- `Threshold: 60% mutation score for domain services`

## 8. Performance Test Requirements `[required]`

Example:
- `Any WP that introduces new background fan-out, indexing strategy, or public list endpoint must include a performance criterion.`

## 9. Prohibited Agent Actions `[required]`

Example:
- `Do not delete failing tests to satisfy CI.`
- `Do not replace integration tests with mocks when the done criteria require persistence verification.`

## Change Log

| Date | Author | Change |
|---|---|---|
| `YYYY-MM-DD` | `[name]` | `Initial draft` |
