# HANDOVER: checkin-live-patch

samurai-claw now holds the code that runs in `ak-check-in-uat` and `ak-check-in-prod`, on top of the F3 fix
(`HANDOVER-fix-checkin-gym-store.md`). That code was deployed on 2026-10-10 from uncommitted local edits.
The hub can now deploy samurai-claw without losing anything. **Code only:** nothing was deployed and nothing
was written to AWS.

Sources: kakuto-agent-org `tmp/handover-checkin-deploy-diff.md` (the diff findings) and the patch
`workspace/tmp/checkin-diff/live-only.patch`, which was made against samurai-claw 3f78848.

## What was merged

- Commit `65dc4a1`, "server: capture live 2026-10-10 deploy": `git apply --3way live-only.patch` onto 3f78848.
  It touched `server/lambda_function.py`, `server/settings-example.py` (black style, with the TABLE_MAP example now
  ak-uat/ak-prod) and `server/test.py` (+377 lines). The diff of `settings-example.py` holds placeholders only.
  `settings.py` stays gitignored and out of git.
- Commit `faa0e3a`, "server tests": adds `server/tests/test_live_behaviours.py` (28 tests). It also changes
  `tests/test_user_action.py` `published()` so that it no longer de-duplicates. Each F3 test unpacks a one-item list,
  so a second publish now fails 50+ tests.
- The merge of `worker/checkin-live-patch` into samurai-claw (`--no-ff`); its commit id is at the end of this
  file. `main` is untouched.

The seven live-only behaviours, all kept:

1. The pubnub import and init, and the loading of TEAMUP_API_KEY and AUTHORIZATION_TOKEN, are each in a try/except.
   The module loads without them (`pubnub = None`).
2. `user_action` publishes **once**, guarded by `if pubnub is not None`; a publish error is printed, not raised.
3. `_is_kakuto()`: a store whose `/configs/timetable` has `provider == "kakuto"` gets its classes from
   ak-class-timetable through `_get_events` (`get_classes`) and `_get_event` (`get_events`). The code tries
   `calendar_provider` first; it is not packaged, so the Lambda invoke runs.
4. Tolerant parsing: times may be a datetime or a str, `now` may be a str or naive, and an unknown subcalendar falls
   back (`CAL_EVENT_ICON_MAP.get(..., "default.png")`, `CAL_EVENT_TITLE.get(...)`).
   `_find_check_in_windows` uses `self._today()`.
5. `initial_state` returns `subscribe_key ""` when PubNub is unavailable.
6. `_get_participants`: a signed-up pid < 0 is keyed by the bare email, and a member who signed up and then checked
   in appears once.
7. Internal (`stage`/`method`) allow-list: {user_action, current_event, next_event, initial_state}.

## Conflict resolution

There was none. The 3-way apply was clean, and `user_action` came out exactly as intended:

- It keeps the F3 per-gym store lookup (`_gym_db(gym_id)`, with `gym_id` passed through from the top-level event in
  `lambda_handler`), and it warns and skips an unknown gym or a missing user.
- It then makes the single guarded publish (`if pubnub is not None: try: publish ... except: print`).
- The F3 handover's "Not changed: user_action still publishes each message twice" no longer applies.

## Tests (Python 3.14)

- `make unittest` (pytest `server/tests`, python:3.14-slim, requirements.txt + requirements-dev.txt):
  **94 passed, 1 skipped**. That is the 58 F3 gym-store tests, the user_action tests and the 28 new tests. The skip
  is the ak-server `DB_SUFFIX` parity test, which needs `AK_SERVER_DIR`.
- New tests, by behaviour:
  1. Module import with no secrets and no pubnub, and with only the PubNub secrets failing (isolated module load).
  2. Exactly one publish; no PubNub gives no error; a publish error is swallowed.
  3. kakuto gym via ak-class-timetable with boto3 stubbed: uat and prod function names, the `get_classes`
     payload, a dict or bare-list answer, `get_event`, a missing event raises `ValueError`, `current_event` end to
     end, Teamup never called. A Teamup gym still uses Teamup and never invokes.
  4. Datetime or str times, an unknown subcalendar, a str or naive `now`, and `_find_check_in_windows` with
     `_today`.
  5. `initial_state` with no pnconfig.
  6. Signed up then checked in (as `email` or `email!-1`) appears once; member and child are separate entries;
     signed up only.
  7. `lambda_handler` internal: current_event, next_event and initial_state are allowed; `_get_events`,
     `_signed_ups` and the rest are refused.
- `server/test.py` is a mixed pytest file, **not** a unit-test suite (`make unittest` only runs `tests/`).
  - Its 4 live tests need the real DynamoDB and the UAT API. `test_checkin` and `test_signup` **write** to UAT. They
    were not run.
  - Its 5 offline tests need the real `settings.py` (icon and title maps). In a copy, with the real settings and
    no AWS credentials, they gave **5 passed**.
- Repo root: `npm ci --legacy-peer-deps` (a plain `npm ci` fails on a react peer conflict, which predates this
  change), then `npm run lint` passed (exit 0) and `npm test` passed 6/6.
- After the merge (samurai-claw had not moved since 3f78848) the gate was re-run with the same results.

## Build check (no deploy)

- I copied the real `server/settings.py` into the clone and ran `make clean install build` with a uv Python 3.14
  venv on x86_64.
- `build/` held `lambda_function.py`, `settings.py`, `test.py`, `lib/` (`ak_user.py`, `kms_utils.py`) and all the
  deps.
- Then I deleted the copied `settings.py` and `build/`. Nothing was printed or committed.
- Compared with the deployed prod package (`workspace/tmp/checkin-diff/prod/`):
  - `settings.py`, `lib/` and `test.py` are byte-identical.
  - The top-level package names are the same (prod also has a stray `__pycache__`).
  - `lambda_function.py` differs **only by the F3 fix**: `import settings`, `GYM_DB_SUFFIX`, `Handler(connect=)` and
    `_gym_db`, a tolerant `_get_stars(db)`, the `user_action(gym_id=)` warn-and-skip, `_connect_db`, and
    `lambda_handler` passing the top-level `gym_id` through.
- The built package imports cleanly in python:3.14-slim with no network and no secrets (it logs the PubNub and
  AUTHORIZATION_TOKEN warnings; `pubnub` is None).
- **Dependency drift:** `make install` uses `uv pip install --upgrade`, so the deps are newer than prod's (pubnub
  10.7.2 -> 10.8.1, multidict 6.9.1 -> 7.2.1, boto3/botocore 1.43.102 -> 1.44.1, aiohttp 3.14.3 -> 3.14.5 and minor
  others; kydb is the same at 1.1.0). The tests pass on the new versions. Watch the UAT logs for PubNub publish
  errors.

## Deploy steps for the hub (ak-check-in is not in `org deploy`, so it is deployed by hand)

The React app is unchanged. Only the `server/` Lambda deploys.

1. Take the lease `org lease deploy:ak-check-in:lambda:uat`. On a fresh clone of `origin/samurai-claw` (clean, not
   a worker branch) at or after the merge commit below, copy in the real `server/settings.py` from
   `workspace/ak-check-in/server/` (never print or commit it). Then, in a Python 3.14 environment with uv and
   AWS credentials for the AK account:
   ```
   cd server
   make clean install build
   make deploy          # ak-check-in-uat
   ```
   Record the CodeSha256 and the commit, then release the lease.
2. **UAT check** (from HANDOVER-fix-checkin-gym-store.md, plus this patch):
   1. In UAT, sign up for or check in to a class of a non-default gym (e.g. diesel_gym) as one of its members.
   2. In `/aws/lambda/ak-check-in-uat`, expect `Sending message: {... 'name': ...}`, **one** `Publish time:` line
      per action (it was two before), and no `KeyError`. A member who is not in the store gives a
      `user_action: no user ...` WARNING, not an error.
   3. Lambda `Errors` and `AsyncEventsDropped` for ak-check-in-uat stay at 0.
   4. Check that current_event and next_event still work (the check-in display) for the Teamup gym (diesel_ak). For a
      kakuto-provider store they come from ak-class-timetable.
3. Prod: take the lease `deploy:ak-check-in:lambda:prod` and run `make deploy-prod` from the same commit with the
   same settings.
   - Record the CodeSha256 in the ledger.
   - Watch `/aws/lambda/ak-check-in-prod`: expect `user_action: no user...` WARNINGs instead of KeyError tracebacks,
     and errors falling from about 21 a day to 0.
   - Then delete the copied `settings.py` and `build/`.
4. Follow-up from F3, still open: add the `server-unittest` CI job (it needs a token with `workflow` scope).

## Merge commit

`effb578` "Merge worker/checkin-live-patch" on samurai-claw (parents 3f78848 and the worker head). Deploy from this commit
or later.
