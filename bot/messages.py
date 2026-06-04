"""
All user-facing text strings.

Keeping them in one file makes copy edits trivial and sets up the project
for translation later — swap this module for one with `gettext` calls and
nothing else has to change.
"""

WELCOME = (
    "👋 Welcome!\n\n"
    "I'll help you submit your application in a few short steps. "
    "You can cancel at any time with /cancel.\n\n"
    "Let's start — what is your full name?"
)

ASK_EMAIL = "📧 Great. What email should we use to reach you?"
ASK_PHONE = (
    "📱 Got it. What is your phone number? "
    "(Include country code, e.g. +380...)"
)
ASK_MESSAGE = (
    "💬 Anything you'd like to add? "
    "A short message about your request, your availability, or anything "
    "else we should know."
)

CONFIRM_TEMPLATE = (
    "Please review your application:\n\n"
    "<b>Name:</b> {full_name}\n"
    "<b>Email:</b> {email}\n"
    "<b>Phone:</b> {phone}\n"
    "<b>Message:</b> {message}\n\n"
    "Tap <b>Submit</b> to send, or <b>Edit</b> to start over."
)

SUBMITTED = (
    "✅ Your application has been submitted.\n\n"
    "Thanks for reaching out — we'll get back to you shortly."
)

CANCELLED = "Cancelled. Send /start when you'd like to try again."

ALREADY_SUBMITTED = (
    "We already have your application on file from earlier. "
    "If you need to update something, please contact the team directly."
)

INVALID_EMAIL = (
    "That doesn't look like a valid email. "
    "Please send it in the form: someone@example.com"
)

INVALID_PHONE = (
    "That doesn't look like a valid phone number. "
    "Please include the country code (e.g. +380501234567)."
)

INVALID_NAME = (
    "Please send your full name as text (at least 2 characters)."
)

ERROR_GENERIC = (
    "Something went wrong on our side. The team has been notified. "
    "Please try again with /start, or message support directly."
)

# Admin notification template
ADMIN_NEW_SUBMISSION_TEMPLATE = (
    "🆕 <b>New application</b>\n\n"
    "<b>From:</b> @{username} (id: <code>{user_id}</code>)\n"
    "<b>Name:</b> {full_name}\n"
    "<b>Email:</b> {email}\n"
    "<b>Phone:</b> {phone}\n"
    "<b>Message:</b> {message}\n\n"
    "<i>Synced to Google Sheets ✓</i>"
)

# Admin stats template
ADMIN_STATS_TEMPLATE = (
    "📊 <b>Submission stats</b>\n\n"
    "Today: <b>{today}</b>\n"
    "This week: <b>{week}</b>\n"
    "All time: <b>{total}</b>"
)

ADMIN_ONLY = "This command is for admins only."
