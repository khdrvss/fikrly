# Core models

- Company
  - name, category, city, description
  - image/image_url, library_image_path
  - website, official_email_domain
  - manager (User), is_verified, rating, review_count
- Review
  - company, user, user_name, rating, text
  - is_approved, approval_requested, created_at
  - owner_response_text, owner_response_at
- ReviewReport
  - review, reporter, reason, details, status
- UserProfile
  - user, avatar, bio, approval fields
- ActivityLog
  - actor, action, company, review, details, created_at
- PhoneOTP
  - phone, code, attempts, is_used
- CompanyClaim
  - company, claimant, email, token, status, created_at, verified_at, expires_at

Relations
- Company 1—* Review
- Company 1—* CompanyClaim
- Company 1—* ActivityLog
- Review 1—* ReviewReport
- Review 1—* ActivityLog
- User 1—1 UserProfile
- User 1—* Reviews, Claims, ActivityLogs
