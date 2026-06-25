# API Reference

Base URL: `http://localhost:8000/api/v1`  
Interactive docs: `http://localhost:8000/api/docs`

All write endpoints require `Authorization: Bearer <token>`.  
Obtain a token via `POST /auth/login`.

---

## Auth

### POST /auth/login
```json
{ "username": "admin", "password": "ChangeMe123!" }
```
Returns `{ "access_token": "...", "token_type": "bearer" }`.

### GET /auth/me
Returns the current admin's profile.

---

## Matches

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /matches/today | — | Today's matches (bot: Today's Matches) |
| GET | /matches/upcoming | — | Future scheduled matches |
| GET | /matches/live | — | Live + half-time matches |
| GET | /matches | — | All matches (filterable: `tournament_id`, `status_filter`) |
| GET | /matches/{id} | — | Single match with teams + streams |
| POST | /matches | manager+ | Create match |
| PUT | /matches/{id} | manager+ | Update match fields |
| PATCH | /matches/{id}/status | moderator+ | Update status + score; triggers notifications |
| DELETE | /matches/{id} | manager+ | Delete match |

### PATCH /matches/{id}/status — body
```json
{ "status": "live", "home_score": 1, "away_score": 0 }
```
Status values: `scheduled` `live` `halftime` `finished` `postponed` `cancelled`

---

## Streams

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /streams | — | All streams (admin listing) |
| GET | /matches/{id}/streams | — | Streams for one match (bot: Watch Now) |
| POST | /matches/{id}/streams | manager+ | Add stream to match |
| PUT | /streams/{id} | manager+ | Update stream |
| DELETE | /streams/{id} | manager+ | Remove stream |

### POST /matches/{id}/streams — body
```json
{
  "language": "English",
  "quality": "1080p",
  "stream_type": "hls",
  "url": "https://example.com/stream.m3u8",
  "is_active": true,
  "sort_order": 0
}
```
`stream_type`: `hls` `mp4` `external` `webapp`

---

## Highlights

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /highlights | — | All highlights |
| GET | /matches/{id}/highlight | — | Highlight for one match (bot) |
| POST | /highlights | moderator+ | Add highlight |
| PUT | /highlights/{id} | moderator+ | Update highlight |
| DELETE | /highlights/{id} | moderator+ | Remove highlight |

### POST /highlights — body
```json
{ "match_id": 1, "youtube_url": "https://youtube.com/watch?v=...", "title": "Full Highlights" }
```

---

## Notifications

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /notifications/subscribe | — | Subscribe (bot: Notify Me) |
| DELETE | /notifications/unsubscribe | — | Unsubscribe |
| GET | /notifications/status | — | Check subscription (bot toggle button) |
| GET | /notifications | admin | List all active subscriptions |

### POST /notifications/subscribe — body
```json
{ "telegram_id": 123456789, "match_id": 1 }
```

---

## Tournaments & Teams

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /tournaments | — | List all tournaments |
| POST | /tournaments | manager+ | Create tournament |
| PUT | /tournaments/{id} | manager+ | Update tournament |
| DELETE | /tournaments/{id} | super_admin | Delete tournament (cascades) |
| GET | /tournaments/{id}/groups | — | List groups |
| POST | /tournaments/{id}/groups | manager+ | Add group |
| GET | /teams | — | List teams (`?tournament_id=`) |
| POST | /teams | manager+ | Create team |
| PUT | /teams/{id} | manager+ | Update team |
| DELETE | /teams/{id} | manager+ | Delete team |

---

## Standings

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /standings | — | Points table (`?tournament_id=`, `?group_id=`) |
| PUT | /standings | manager+ | Upsert one standing row |

---

## FIFA Data Sync

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /fifa/sync/{tournament_id} | manager+ | Pull provider data into DB |

---

## Dashboard

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /dashboard/metrics | any admin | Users, live, today, notifications, streams, tournaments counts |

---

## Admin Users

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /admin-users | super_admin | List staff accounts |
| POST | /admin-users | super_admin | Create admin |
| PUT | /admin-users/{id} | super_admin | Update admin |
| DELETE | /admin-users/{id} | super_admin | Remove admin |

---

## Audit Logs

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /audit-logs | manager+ | Recent admin actions (`?entity_type=`, `?limit=`) |

---

## Settings

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | /settings | manager+ | All key/value settings |
| PUT | /settings/{key} | super_admin | Upsert a setting |

---

## Uploads

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /upload/image | moderator+ | Upload JPEG/PNG/WebP (≤ MAX_UPLOAD_SIZE_MB) |

Returns `{ "url": "/static/uploads/<filename>" }`.

---

## Users (Bot internal)

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /users/upsert | — | Register/update Telegram user on /start |
