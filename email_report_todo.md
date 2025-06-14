# 📬 Email Report Feature – To-Do Checklist

## ✅ Basic Functionality
- [ ] Add form in the UI to input:
  - [ ] Receiver email address
  - [ ] Sender email address
  - [ ] SMTP server, port, username, password
- [ ] Collect last 7 days of user data (same as in weekly summary)
- [ ] Format report content (text-based to start)
- [ ] Send email via `smtplib` and `email.mime.text`

## ✨ Optional Upgrades
- [ ] Format report in **HTML** for rich styling
- [ ] Allow sending as **PDF attachment**
- [ ] Automate sending every Sunday (requires backend or scheduling support)
- [ ] Save previous reports for access history
- [ ] Use a trusted email service provider (SendGrid, Mailgun, etc.)
- [ ] OAuth login for Gmail instead of raw SMTP credentials

## 🔐 Security Considerations
- [ ] Encrypt/store credentials securely (avoid raw text)
- [ ] Warn user about handling sensitive login info
- [ ] Add "test connection" button before sending

## 🛠 Tech Requirements (when ready)
- `smtplib`, `email.mime.text`
- (Optional later) `email.mime.multipart`, `email.mime.application` for PDF
- (Optional later) `reportlab` or `pdfkit` for PDF generation