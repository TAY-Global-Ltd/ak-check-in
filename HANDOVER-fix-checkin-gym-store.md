# HANDOVER: fix-checkin-gym-store

Finding F3 of kakuto-super-admin `docs/health-audit-2026-11-12.md` (55e40ac).
`ak-check-in-prod` had 291 errors in 1,120 invocations and 97 `AsyncEventsDropped`.
Every error was `KeyError: '/users/<email>'` in `user_action`. 55 members of
non-default gyms were affected, about 21 a day since 11-09. UAT shows the same
error (6/6 on 11-11).

## Root cause

ak-class-timetable `_notify_checkins` (ak-server samurai-claw) invokes
`ak-check-in-<stage>` asynchronously with `gym_id` at the **top level** of the
event. That `gym_id` is the class's gym, from `gym_id_from_db(db)`. The deployed
ak-check-in ignores it and reads `/users/<id>` from the root store
(`dynamodb://ak-<stage>`). A member of another gym exists only under that gym's
prefix (`/diesel_gym/users/<id>`), so the lookup raised `KeyError`. The async
invoke retried each event twice and then dropped it.

## The fix

It is `958550b` (already on **main** via PR #141, merged 2026-11-09, but
**never deployed**), plus this branch:

- `user_action(..., gym_id=None)` reads the user and the stars from
  `dynamodb://<TABLE_MAP[stage]><GYM_DB_SUFFIX[gym_id]>`. `lambda_handler`
  passes the top-level `gym_id` through.
- An unknown gym or a missing user logs a WARNING and is skipped. It no longer
  raises, so nothing is retried or dropped.
- **This branch:** adds `kakuto_demo` to `GYM_DB_SUFFIX`. ak-server's
  `lib/lambda/gym_config.DB_SUFFIX` gained it after 958550b, and its smoke users'
  notifications would otherwise be skipped as "unknown gym".
- **This branch:** `server/tests/test_gym_store.py` (58 tests):
  - It replays the exact `_notify_checkins` event for every gym × {uat, prod} ×
    {signedup, checkedin, cancelled}.
  - It covers the old event without `gym_id`, `gym_id=diesel_ak`, and one store
    connection per gym.
  - It checks that a missing user or an unknown gym never raises.
  - It checks the suffix convention.
  - It includes a parity test against ak-server's `DB_SUFFIX`. That test runs
    when `AK_SERVER_DIR` is set and is skipped otherwise.
- **Not pushed (follow-up for the hub or owner):** a `server-unittest` CI job.
  The worker token has no `workflow` scope, so GitHub refused the change. The
  job to add to `.github/workflows/run_tests.yml` is:
  `actions/setup-python` with Python 3.14, then
  `pip install -r requirements.txt -r requirements-dev.txt`, then
  `make unittest`, all in `server/`.

## Evidence (gate)

- `npm run lint`: pass. `npm test` (jest): 6/6 pass.
- `server` pytest on python:3.14-slim with requirements.txt and
  requirements-dev.txt:
  - **67 passed**, run with `AK_SERVER_DIR` pointing at ak-server samurai-claw
    8d3152f, so the parity test ran and passed.
  - 66 passed and 1 skipped without it.
- **Reproduction:** the same tests run against the pre-fix `lambda_function.py`
  (d5adc1b, with only the map constants grafted on so it imports) give
  **55 failed**, each with `KeyError: '/users/...'`. That is the prod error.

## What deploys, and how (hub)

Only the Lambda in `server/` deploys. The React app (`deploy.py`, gh-pages and
CloudFront) is unchanged and does **not** need a release.

From a checkout of `samurai-claw`, on a machine with the real
`server/settings.py` (it is gitignored: the owner's local copy), Python 3.14,
`uv` and AWS credentials:

```
cd server
make clean install build    # build/ = deps + settings.py + lambda_function.py + lib/
make deploy                 # UAT:  aws lambda update-function-code ak-check-in-uat
make deploy-prod            # prod: aws lambda update-function-code ak-check-in-prod
```

Both functions are deployed by hand from that local checkout. There is no CI
deploy.

Before releasing:

1. **Diff the deployed code first.** The prod traceback puts the failing line
   at `lambda_function.py` **line 397**. In no committed version is it there
   (pre-fix main has it at line 248). The deployed package (last changed
   2026-10-10) was therefore built from uncommitted local changes. Download it
   (`aws lambda get-function --function-name ak-check-in-prod`, then
   `Code.Location`) and diff it against `server/lambda_function.py` here.
   Otherwise the release may silently drop those changes. Workers cannot do
   this: `kakuto-agent-worker` has no `lambda:Get*`.
2. Check that the deployed `settings.py` `TABLE_MAP[stage]` is the stage's main
   table (`ak-uat` / `ak-prod`). Per-gym stores are `<that table>/<gym>`. If it
   is a different table, set `GYM_DB_SUFFIX` in settings.

## UAT check (after `make deploy`)

1. In UAT, sign up for or check in to a class of a non-default gym (e.g.
   diesel_gym) as one of its members.
2. In `/aws/lambda/ak-check-in-uat`, expect `Sending message: {... 'name': ...}`
   and no `KeyError`. A member who is not in the store gives a
   `user_action: no user ...` WARNING, not an error.
3. Lambda `Errors` and `AsyncEventsDropped` for ak-check-in-uat should stay at 0.

For prod, run the same check on `ak-check-in-prod` after `make deploy-prod`.
Errors should fall from about 21 a day to 0.

## Not changed

- `user_action` still publishes each message twice.
- `initial_state` / `_get_participants` still read attendees from the root
  store. They serve the TeamUp calendar, which is the default gym's.
- The display filters by `event_id`, so other gyms' messages only render for
  events on the screen's calendar. Stopping the errors and drops is the fix.
