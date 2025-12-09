# URL routes overview

Key routes (see `frontend/urls.py`):

- `/` — Home
- `/business-profile/` — Entry to businesses
- `/bizneslar/` — All businesses grid
- `/business/<pk>/` — Company detail with reviews, filters, pagination
- `/sharh-yozish/` — Create a review (text-only)
- `/reviews/<pk>/report/` — Report a review
- Manager
  - `/business-dashboard/` — Manager dashboard
  - `/manager/company/<pk>/edit/` — Edit company
  - `/manager/reviews/<pk>/request-approval/` — Request approval
  - `/manager/reviews/<pk>/respond/` — Respond to a review
- Claim & verification
  - `/business/<pk>/claim/` — Start claim (email verification)
  - `/claim/verify/<token>/` — Verify claim token
  - `/verification-badge/` — What the badge means
- Auth (email login; phone routes exist but hidden in UI)
  - `/accounts/login/`, `/accounts/signup/`, `/accounts/logout/`
  - `/accounts/phone/`, `/accounts/phone/verify/` (OTP demo)
