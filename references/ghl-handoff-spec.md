# GoHighLevel (GHL) Bigfoot Master Template & Deployment Specification

This document serves as the implementation handoff for Rodrigo to set up the GoHighLevel (GHL) Agency master template subaccount (snapshot) and deploy it to the live Bigfoot directory subaccounts.

---

## 1. Master Template Snapshot: Custom Values Mapping

To ensure the master template is completely modular and portable, **do not hardcode any site-specific details** in the email templates, SMS, form titles, or workflow steps. Use the following **Custom Values** in the master snapshot:

| Custom Value Key | Description | Example (for US Well Drillers) |
| :--- | :--- | :--- |
| `{{custom_value.directory_name}}` | Human-readable name of the directory. | `US Well Drillers` |
| `{{custom_value.directory_url}}` | The main production domain URL (no trailing slash). | `https://uswelldrillers.com` |
| `{{custom_value.support_email}}` | The primary contact and sender email for the site. | `claims@uswelldrillers.com` |
| `{{custom_value.niche_noun}}` | Singular noun representing the target professionals. | `water well driller` |
| `{{custom_value.niche_plural}}` | Plural noun representing the target professionals. | `water well drillers` |
| `{{custom_value.compliance_address}}` | Physical physical/mailing address for CAN-SPAM footer. | `2302 Parklake Dr NE, Suite 675, Atlanta, GA 30345` |
| `{{custom_value.compliance_email}}` | Dedicated email inbox for legal, TOS, and privacy inquiries. | `compliance@uswelldrillers.com` |

---

## 2. Automated Workflows (Phase 1 Scope)

Rodrigo needs to construct the following automated workflows in the master snapshot.

### A. Profile Claims Verification
* **Trigger:** Webhook/Form submitted with *Claim Listing Request* payload.
* **Fields Captured:**
  * Contact Name, Email, Phone
  * Business Name, Business Address, Target Profile ID (`business_id`)
  * Professional License Number (if applicable)
* **Automation Actions:**
  1. Add Tag: `claimed_pending`.
  2. Set Custom Fields: `business_id` (store SQLite/Supabase primary key), `submitted_license_num`.
  3. **Verification Email (Auto-responder):**
     * **Subject:** `Action Required: Confirm your listing on {{custom_value.directory_name}}`
     * **Body:**
       > *"Hi [First Name],*
       >
       > *We received your request to claim the profile for **[Business Name]** on {{custom_value.directory_name}}.*
       >
       > *To complete your verification and unlock editor access to update your services, descriptions, and logo, please reply directly to this email with:*
       > *1. A photo/PDF of your active state license or business registration.*
       > *2. Or simply reply from an email address matching your business domain (e.g., info@yourbusiness.com).*
       >
       > *Best regards,*
       > *The {{custom_value.directory_name}} Verification Team"*
  4. **Internal Admin Notification (Temporary):**
     * Send email/in-app alert to directory moderators: *"New claim request for [Business Name] on {{custom_value.directory_name}}. License submitted: [License Num]."*
     * **Temporary Routing:** Also send a direct notification email to `rodrigo.fernandez@paretotalent.com` so he is immediately notified when claims come in during the early launch phase.

### B. User Email Opt-in & Welcome Sequence
* **Trigger:** Webhook/Form submitted for *Newsletter signup* or *Calculator Guest Mode*.
* **Automation Actions:**
  1. Add Tag: `newsletter_subscriber`.
  2. **Welcome Email:**
     * **Subject:** `Welcome to {{custom_value.directory_name}}! 🛠️`
     * **Body:**
       > *"Hi [First Name],*
       >
       > *Thanks for subscribing to {{custom_value.directory_name}}!*
       >
       > *We'll keep you updated with the latest local directory updates, news, and utility tool releases.*
       >
       > *Feel free to search listings and run calculations anytime here: {{custom_value.directory_url}}.*
       >
       > *If you already have feedback on our listings, just reply directly to this email with the details—we'd love to hear from you!*
       >
       > *Best,*
       > *The Team"*

### C. Newsjacking Broadcast (Newsletter updates)
* **Trigger:** Inbound Webhook (triggered programmatically when new content is published via the Newsjacking Engine).
* **Automation Actions:**
  1. Parse the incoming webhook payload (`{ "title": "...", "excerpt": "...", "url": "..." }`).
  2. Trigger email to all contacts tagged with `newsletter_subscriber`.
     * **Subject:** `[New Update] {{webhook.title}}`
     * **Body:** Summarizes the news item and directs them to click the link back to the directory blog.

### D. Privacy / Terms of Service Inquiries
* **Trigger:** 
  1. Support/legal form submitted on site containing keywords `privacy`, `do not sell`, or `terms`.
  2. **OR** Inbound email received at `{{custom_value.compliance_email}}`.
* **Automation Actions:**
  1. Create a Support Ticket in the GHL Pipeline.
  2. Send automated confirmation from `{{custom_value.compliance_email}}`: *"We've received your compliance inquiry regarding {{custom_value.directory_name}} and will process your request within 30 days."*
  3. **Temporary Admin Notification:** Forward incoming message body/ticket alert to `rodrigo.fernandez@paretotalent.com`.

### E. Feedback Email Reply Capture (Temporary)
* **Trigger:** Customer Reply (Channel: Email, Reply to welcome sequence or other emails).
* **Automation Actions:**
  1. Add Tag: `listing_feedback_received`.
  2. **Internal Notification Email:**
     * **Recipient:** `rodrigo.fernandez@paretotalent.com`
     * **Subject:** `[Feedback Received] Customer Reply on {{custom_value.directory_name}}`
     * **Body:**
       > *"Hi Rodrigo,*
       >
       > *A user has replied with feedback for **{{custom_value.directory_name}}**.*
       >
       > * **Contact Name:** {{contact.name}}*
       > * **Contact Email:** {{contact.email}}*
       > * **Message Content:** {{message.body}}*
       >
       > *Please review this reply directly in the GHL conversation timeline."*

---

## 3. Site-by-Site Deployment Checklist

For the active directories (**01-GABAR**, **02-SEPTIC**, **03-WELLS**), execute the following steps to bind their production builds to GHL:

### Step 1: Subaccount Creation & Snapshot Sync
1. In the GHL Agency account, spin up a new subaccount for each:
   * **01-GABAR:** `Bigfoot - Georgia Closing Lawyers`
   * **02-SEPTIC:** `Bigfoot - Georgia Grease Trap`
   * **03-WELLS:** `Bigfoot - US Well Drillers`
2. Load Rodrigo's Master Snapshot into each subaccount.

### Step 2: Custom Domain & Email Delivery
For each subaccount, set up the mail routing subdomain on the domain provider (GoDaddy/Cloudflare/etc.):
* **01-GABAR:**
  * Domain: `gaclosinglawyers.com`
  * Mail Subdomain: `mail.gaclosinglawyers.com` (or LC Email equivalent)
  * Default From: `claims@gaclosinglawyers.com`
  * Dedicated Compliance Email: `compliance@gaclosinglawyers.com`
* **02-SEPTIC:**
  * Domain: `georgiagreasetrap.com`
  * Mail Subdomain: `mail.georgiagreasetrap.com`
  * Default From: `claims@georgiagreasetrap.com`
  * Dedicated Compliance Email: `compliance@georgiagreasetrap.com`
* **03-WELLS:**
  * Domain: `uswelldrillers.com`
  * Mail Subdomain: `mail.uswelldrillers.com`
  * Default From: `claims@uswelldrillers.com`
  * Dedicated Compliance Email: `compliance@uswelldrillers.com`
* *Configure DNS records (SPF, DKIM, MX, DMARC) for each and verify inside GHL settings. Configure email forwarding/routing for compliance@ emails to feed directly into the subaccount inbox.*

### Step 3: Populate Custom Values
Fill out the specific custom values in GHL Settings for each subaccount:

#### 01-GABAR Values
* `directory_name`: `Georgia Closing Lawyers`
* `directory_url`: `https://gaclosinglawyers.com`
* `support_email`: `claims@gaclosinglawyers.com`
* `compliance_email`: `compliance@gaclosinglawyers.com`
* `niche_noun`: `closing attorney`
* `niche_plural`: `closing attorneys`

#### 02-SEPTIC Values
* `directory_name`: `Georgia Grease Trap`
* `directory_url`: `https://georgiagreasetrap.com`
* `support_email`: `claims@georgiagreasetrap.com`
* `compliance_email`: `compliance@georgiagreasetrap.com`
* `niche_noun`: `grease trap hauler`
* `niche_plural`: `grease trap haulers`

#### 03-WELLS Values
* `directory_name`: `US Well Drillers`
* `directory_url`: `https://uswelldrillers.com`
* `support_email`: `claims@uswelldrillers.com`
* `compliance_email`: `compliance@uswelldrillers.com`
* `niche_noun`: `water well driller`
* `niche_plural`: `water well drillers`

### Step 4: Endpoint Integrations
1. Generate the GHL Location API key (V1) or authenticate the app via OAuth 2.0 (V2) to retrieve the access token for each site.
2. In the respective codebase repositories (`tamo42/gaclosinglawyers.com`, `tamo42/georgiagreasetrap.com`, `tamo42/uswelldrillers.com`), add the following to the `.env` production deployment secrets:
   * `GHL_LOCATION_ID`
   * `GHL_API_KEY` (or OAuth access credentials)
   * `GHL_CLAIM_FORM_WEBHOOK_URL`
3. Verify that the static HTML claims form on each site posts a clean payload to the Webhook URL.
