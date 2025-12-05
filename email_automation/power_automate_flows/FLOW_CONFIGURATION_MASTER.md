# POWER AUTOMATE FLOW CONFIGURATION - MASTER DOCUMENT
## Complete Email Automation System for Probate and Legal Matters

**Purpose:** Automate email triage, template selection, and response drafting for estate administration
**Platform:** Microsoft Power Automate (formerly Microsoft Flow)
**Integration:** Outlook 365, SharePoint, OneDrive

---

## I. SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│                    EMAIL ARRIVES IN OUTLOOK                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FLOW 1: EMAIL CATEGORIZATION                    │
│  Analyze sender, subject, keywords → Assign category        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FLOW 2: TEMPLATE SELECTION                      │
│  Based on category, suggest appropriate response template   │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FLOW 3: AUTO-FILL VARIABLES                     │
│  Populate template with case data from SharePoint            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FLOW 4: DRAFT CREATION & APPROVAL               │
│  Create draft email, present to user for review              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FLOW 5: SEND & LOG                              │
│  Send approved email, log to SharePoint, set reminders       │
└──────────────────────────────────────────────────────────────┘
```

---

## II. PREREQUISITES

### A. Microsoft 365 Services Required

☑ **Outlook 365** (primary email client)
☑ **Power Automate** (included with Microsoft 365 Business/Enterprise)
☑ **SharePoint Online** (for databases and document storage)
☑ **OneDrive for Business** (for template storage)
☑ **Microsoft Teams** (optional - for notifications)

### B. Permissions Required

- Power Automate license (Premium preferred for advanced features)
- SharePoint site collection administrator (to create lists)
- Outlook mailbox with delegation rights (if managing multiple accounts)

### C. Data Sources to Create

**1. SharePoint Lists:**
- Estate Case Information
- Heir/Beneficiary Contact Database
- Creditor Claims Tracking
- Professional Contacts (attorneys, CPAs, appraisers)
- Communication Log
- Court Hearing Calendar

**2. OneDrive Document Libraries:**
- Email Templates (markdown files)
- Legal Documents
- Court Filings
- Estate Records

---

## III. FLOW 1: EMAIL CATEGORIZATION & ROUTING

**Flow Name:** "Probate Email Auto-Categorizer"

**Trigger:** When a new email arrives (V3)
- **Folder:** Inbox
- **Include Attachments:** Yes
- **Importance:** All

---

### STEP 1: Parse Email Metadata

**Action:** Get email properties
- **Subject:** `triggerBody()?['subject']`
- **From:** `triggerBody()?['from']`
- **Body:** `triggerBody()?['bodyPreview']`
- **Received:** `triggerBody()?['receivedDateTime']`

---

### STEP 2: Analyze Sender

**Action:** Condition - Check sender domain

**Condition A: Court Email**
```
IF @contains(triggerBody()?['from'], 'lacourt.org')
OR @contains(triggerBody()?['from'], 'court.ca.gov')
OR @contains(triggerBody()?['subject'], 'superior court')
THEN
   Set variable: EmailCategory = "Probate - Court"
   Set variable: Priority = "High"
   Set variable: SuggestedTemplate = "Court Correspondence"
```

**Condition B: Creditor Email**
```
IF @contains(triggerBody()?['subject'], 'claim')
OR @contains(triggerBody()?['subject'], 'creditor')
OR @contains(triggerBody()?['subject'], 'estate debt')
OR @contains(triggerBody()?['from'], [Known Creditor Domains])
THEN
   Set variable: EmailCategory = "Probate - Creditor"
   Set variable: Priority = "Medium"
   Set variable: SuggestedTemplate = "Creditor Response"
```

**Condition C: Heir/Family Email**
```
IF @contains(triggerBody()?['from'], [Known Heir Emails])
OR @contains(triggerBody()?['subject'], 'estate of thurman robinson')
THEN
   Set variable: EmailCategory = "Probate - Family"
   Set variable: Priority = "Medium"
   Set variable: SuggestedTemplate = "Heir Communication"
```

**Condition D: Professional Advisor Email**
```
IF @contains(triggerBody()?['from'], [Known Professional Emails])
OR @contains(triggerBody()?['subject'], 'invoice')
OR @contains(triggerBody()?['subject'], 'legal advice')
OR @contains(triggerBody()?['subject'], 'appraisal')
THEN
   Set variable: EmailCategory = "Probate - Professionals"
   Set variable: Priority = "Medium"
   Set variable: SuggestedTemplate = "Professional Advisor"
```

**Condition E: Debt Collector Email**
```
IF @contains(triggerBody()?['subject'], 'collection')
OR @contains(triggerBody()?['subject'], 'debt')
OR @contains(triggerBody()?['subject'], 'payment')
OR sender matches known debt collector domains
THEN
   Set variable: EmailCategory = "Legal - Debt Collection"
   Set variable: Priority = "High"
   Set variable: SuggestedTemplate = "FTC Settlement Demand"
```

---

### STEP 3: Apply Category to Email

**Action:** Update email
- **Category:** `@{variables('EmailCategory')}`
- **Importance:** `@{variables('Priority')}`
- **Flag:** For follow-up

---

### STEP 4: Save Email to SharePoint

**Action:** Create item in "Communication Log" list
- **Subject:** `@{triggerBody()?['subject']}`
- **From:** `@{triggerBody()?['from']}`
- **Date Received:** `@{triggerBody()?['receivedDateTime']}`
- **Category:** `@{variables('EmailCategory')}`
- **Status:** "Pending Review"
- **Email Body:** `@{triggerBody()?['body']}`

---

### STEP 5: Trigger Template Selection Flow

**Action:** Start child flow "Template Selector"
- **Input - Email ID:** `@{triggerBody()?['id']}`
- **Input - Category:** `@{variables('EmailCategory')}`
- **Input - Suggested Template:** `@{variables('SuggestedTemplate')}`

---

## IV. FLOW 2: TEMPLATE SELECTION & AUTO-FILL

**Flow Name:** "Template Selector & Variable Filler"

**Trigger:** When Flow 1 calls this flow (Manual trigger or HTTP request)

---

### STEP 1: Retrieve Case Data from SharePoint

**Action:** Get items from "Estate Case Information" list
- **Filter:** CaseName eq 'Estate of Thurman Robinson Sr.'
- **Retrieve Fields:**
  - CaseNumber
  - DecedenName
  - DateOfDeath
  - CourtName
  - AdministratorName
  - ContactInfo
  - EstateValue
  - TotalDebts

**Store in variables:**
```
@{outputs('Get_Estate_Info')?['body/value'][0]/CaseNumber}
@{outputs('Get_Estate_Info')?['body/value'][0]/DecedentName}
etc.
```

---

### STEP 2: Select Template Based on Category

**Action:** Switch (multiple conditions)

**Case 1: Court Correspondence**
- **Get file:** OneDrive > Email Templates > TEMPLATE_COURT_CORRESPONDENCE.md
- **Parse:** Extract Template 1-8 based on email content keywords

**Case 2: Creditor Response**
- **Get file:** OneDrive > Email Templates > TEMPLATE_PROBATE_CREDITOR_RESPONSE.md
- **Parse:** Extract Template 1-5 based on:
  - New inquiry → Template 1
  - Need to reject claim → Template 2
  - Need documentation → Template 3
  - Approving claim → Template 4
  - No assets → Template 5

**Case 3: Heir Communication**
- **Get file:** OneDrive > Email Templates > TEMPLATE_HEIR_COMMUNICATIONS.md
- **Parse:** Based on context

**Case 4: Professional Advisor**
- **Get file:** OneDrive > Email Templates > TEMPLATE_PROFESSIONAL_ADVISOR.md
- **Parse:** Based on context

---

### STEP 3: Auto-Fill Template Variables

**Action:** Compose - Replace placeholders

Use **replace()** function to fill in variables:

```json
replace(
  replace(
    replace(
      replace(
        variables('TemplateContent'),
        '[CASE NUMBER]',
        variables('CaseNumber')
      ),
      '[DECEDENT NAME]',
      variables('DecedentName')
    ),
    '[DATE]',
    formatDateTime(utcNow(), 'MMMM d, yyyy')
  ),
  '[ADMINISTRATOR]',
  variables('AdministratorName')
)
```

**Common Variables to Auto-Fill:**
- `[CASE NUMBER]` → from SharePoint
- `[DATE]` → current date
- `[CREDITOR NAME]` → parsed from incoming email sender
- `[AMOUNT]` → parsed from email body (AI Builder or regex)
- `[HEIR NAME]` → matched from Heir Database
- `[HEARING DATE]` → from Court Calendar SharePoint list
- `[ESTATE VALUE]` → from Estate Info
- `[PHONE]` → administrator contact info
- `[EMAIL]` → administrator email
- `[ADDRESS]` → administrator address

---

### STEP 4: Extract Data from Incoming Email (AI Builder)

**Action:** AI Builder - Extract information from text
- **Input:** Email body
- **Extract:**
  - Dollar amounts (regex: `\$[\d,]+\.?\d*`)
  - Dates (regex or AI Builder date extraction)
  - Names (AI Builder entity extraction)
  - Case numbers (regex: `\d{2}-\w+-\d+`)

---

### STEP 5: Create Draft Email

**Action:** Create draft email (V3)
- **To:** `@{triggerBody()?['from']}`  (reply to sender)
- **Subject:** `Re: @{triggerBody()?['subject']}`
- **Body:** `@{outputs('Compose_Template')}`
- **Save as Draft:** Yes (do not send automatically)

---

### STEP 6: Notify User for Review

**Action:** Send Teams notification (or email to self)
- **Message:** "New draft email created for @{variables('EmailCategory')}. Please review and send."
- **Adaptive Card:** Include buttons:
  - "Open Draft in Outlook"
  - "View Original Email"
  - "Edit Template"

---

## V. FLOW 3: CREDITOR CLAIM TRACKER

**Flow Name:** "Creditor Claim Auto-Tracker"

**Trigger:** When an email is categorized as "Probate - Creditor"

---

### STEP 1: Parse Creditor Information

**Action:** AI Builder or Regex
- Extract from email:
  - Creditor name
  - Claim amount (regex: `\$[\d,]+`)
  - Account number
  - Type of debt

---

### STEP 2: Check if Creditor Exists in Database

**Action:** Get items from SharePoint "Creditor Claims" list
- **Filter:** `CreditorName eq '@{variables('CreditorName')}'`

**Condition:**
- **If exists:** Update existing record with new communication
- **If not exists:** Create new record

---

### STEP 3: Create/Update Creditor Record

**Action:** Create item in "Creditor Claims Tracking" list
- **Creditor Name:** `@{variables('CreditorName')}`
- **Claim Amount:** `@{variables('ClaimAmount')}`
- **Date Received:** `@{utcNow()}`
- **Status:** "Pending Review"
- **Last Contact:** `@{utcNow()}`
- **Email Link:** Link to email in Outlook
- **Response Due:** `@{addDays(utcNow(), 30)}`

---

### STEP 4: Set Reminder

**Action:** Create task in Outlook
- **Subject:** "Review creditor claim: @{variables('CreditorName')}"
- **Due Date:** `@{addDays(utcNow(), 30)}`
- **Priority:** High

---

## VI. FLOW 4: COURT DEADLINE TRACKER

**Flow Name:** "Court Hearing & Deadline Monitor"

**Trigger:** Recurrence (daily at 8:00 AM)

---

### STEP 1: Get Upcoming Court Dates

**Action:** Get items from SharePoint "Court Hearing Calendar"
- **Filter:** `HearingDate ge '@{utcNow()}' and HearingDate le '@{addDays(utcNow(), 7)}'`
- **Order By:** HearingDate ascending

---

### STEP 2: Check for Approaching Deadlines

**Action:** Apply to each (loop through hearings)

**Condition:** If HearingDate is within 7 days
- **Send reminder email:**
  - **Subject:** "REMINDER: Court hearing in @{variables('DaysUntil')} days"
  - **Body:** Include hearing details (date, time, dept, matter)
  - **Attachments:** Link to related documents in SharePoint

**Condition:** If HearingDate is within 1 day
- **Send urgent reminder:**
  - **Priority:** High
  - **Teams notification:** Alert user immediately

---

## VII. FLOW 5: INVOICE APPROVAL WORKFLOW

**Flow Name:** "Professional Invoice Approval"

**Trigger:** When email from professional contact contains "invoice" in subject

---

### STEP 1: Detect Invoice Attachment

**Action:** Condition - Check for PDF attachment
- **File type:** .pdf
- **File name contains:** "invoice" OR "bill"

---

### STEP 2: Extract Invoice Data (AI Builder)

**Action:** AI Builder - Process invoice
- **Extract:**
  - Invoice number
  - Invoice date
  - Amount due
  - Vendor name
  - Line items

---

### STEP 3: Save Invoice to SharePoint

**Action:** Create file in SharePoint "Invoices" library
- **File Name:** `Invoice_@{variables('VendorName')}_@{variables('InvoiceNumber')}.pdf`
- **Folder:** /Estate Invoices/
- **Metadata:**
  - Vendor: `@{variables('VendorName')}`
  - Amount: `@{variables('Amount')}`
  - Date: `@{variables('InvoiceDate')}`
  - Status: "Pending Approval"

---

### STEP 4: Create Approval Request

**Action:** Start approval
- **Title:** "Approve Invoice: @{variables('VendorName')} - $@{variables('Amount')}"
- **Assigned to:** Thurman Malik Robinson
- **Details:** Invoice details + link to PDF
- **Approval Type:** First to respond

---

### STEP 5: Process Approval Response

**Condition:** If approved
- **Update SharePoint:** Status = "Approved"
- **Create draft payment email:** Using Professional Advisor Template 5
- **Add to payment queue:** SharePoint list

**Condition:** If rejected
- **Update SharePoint:** Status = "Rejected"
- **Create draft response email:** Explaining rejection with Template 6

---

## VIII. FLOW 6: HEIR UPDATE SCHEDULER

**Flow Name:** "Monthly Heir Status Update"

**Trigger:** Recurrence (1st of every month at 9:00 AM)

---

### STEP 1: Get Heir List

**Action:** Get items from SharePoint "Heir Contact Database"
- **Filter:** Active eq true
- **Select:** Name, Email, Percentage

---

### STEP 2: Get Estate Status

**Action:** Get items from SharePoint "Estate Case Information"
- **Fields:**
  - Total Assets
  - Total Debts
  - Current Stage
  - Expected Distribution Date

---

### STEP 3: Generate Status Update

**Action:** Compose using Heir Communication Template 2
- **Auto-fill:**
  - Current month/year
  - Estate values
  - Distribution percentages
  - Timeline updates

---

### STEP 4: Create Draft Emails (one per heir)

**Action:** Apply to each (loop through heirs)
- **Create draft email** for each heir
- **Personalize** with their name and distribution percentage
- **Save as draft** for manual review and customization

---

### STEP 5: Notify Administrator

**Action:** Send notification
- **Message:** "Monthly heir update emails have been drafted for @{variables('HeirCount')} heirs. Please review and send."

---

## IX. SHAREPOINT LIST SCHEMAS

### List 1: Estate Case Information

| Column Name | Type | Description |
|-------------|------|-------------|
| CaseNumber | Single line text | Court case number |
| DecedentName | Single line text | Full name of decedent |
| DateOfDeath | Date | Date of death |
| CourtName | Single line text | Los Angeles Superior Court |
| AdministratorName | Single line text | Thurman Malik Robinson |
| ContactEmail | Single line text | Administrator email |
| ContactPhone | Single line text | Administrator phone |
| TotalAssets | Currency | Current total estate assets |
| TotalDebts | Currency | Current total debts |
| NetEstate | Calculated | TotalAssets - TotalDebts |
| CurrentStage | Choice | (Probate Filed, Letters Issued, Inventory Filed, Claims Period, Distribution) |
| DistributionDate | Date | Expected distribution date |

---

### List 2: Heir Contact Database

| Column Name | Type | Description |
|-------------|------|-------------|
| HeirName | Single line text | Full name |
| Relationship | Choice | (Son, Daughter, Spouse, Sibling, Other) |
| Email | Single line text | Email address |
| Phone | Single line text | Phone number |
| Address | Multiple lines text | Mailing address |
| DistributionPercentage | Number | % of estate (0-100) |
| EstimatedDistribution | Currency | Calculated amount |
| Active | Yes/No | Currently active heir |
| LastContact | Date | Last communication date |
| Notes | Multiple lines text | Special notes |

---

### List 3: Creditor Claims Tracking

| Column Name | Type | Description |
|-------------|------|-------------|
| CreditorName | Single line text | Creditor name |
| ClaimAmount | Currency | Amount claimed |
| ClaimDate | Date | Date claim filed |
| ClaimType | Choice | (Credit Card, Medical, Loan, Utility, Other) |
| Status | Choice | (Pending, Approved, Rejected, Paid) |
| ResponseDue | Date | Deadline to respond |
| AmountApproved | Currency | Amount approved (if partial) |
| PaymentDate | Date | Date paid |
| Notes | Multiple lines text | Details |
| Attachments | Attachments | Claim forms, supporting docs |

---

### List 4: Professional Contacts

| Column Name | Type | Description |
|-------------|------|-------------|
| ContactName | Single line text | Full name |
| Firm | Single line text | Company/firm name |
| ProfessionType | Choice | (Attorney, CPA, Appraiser, Realtor, Other) |
| Email | Single line text | Email address |
| Phone | Single line text | Phone number |
| HourlyRate | Currency | Rate (if hourly) |
| ServicesProvided | Multiple lines text | Description |
| TotalFeesPaid | Currency | Running total |
| Active | Yes/No | Currently engaged |
| Notes | Multiple lines text | Performance notes |

---

### List 5: Communication Log

| Column Name | Type | Description |
|-------------|------|-------------|
| Subject | Single line text | Email subject |
| From | Single line text | Sender email |
| To | Single line text | Recipient email |
| DateReceived | Date | Date received |
| Category | Choice | (Court, Creditor, Heir, Professional, Other) |
| Status | Choice | (Pending, Responded, No Response Needed, Closed) |
| Template Used | Single line text | Which template was used |
| ResponseSent | Date | Date response sent |
| FollowUpDue | Date | Follow-up date if needed |
| EmailLink | Hyperlink | Link to email in Outlook |
| Notes | Multiple lines text | Summary |

---

### List 6: Court Hearing Calendar

| Column Name | Type | Description |
|-------------|------|-------------|
| HearingDate | Date | Date and time of hearing |
| Department | Single line text | Court department |
| Matter | Single line text | What's being heard |
| Status | Choice | (Scheduled, Continued, Completed, Cancelled) |
| Documents Filed | Attachments | Related court docs |
| Outcome | Multiple lines text | Result of hearing |
| NextHearing | Date | If continued |

---

## X. TESTING & DEPLOYMENT

### Phase 1: Test with Sample Emails (Week 1)

**Test Scenarios:**
1. Send test email from "lacourt.org" address → Should auto-categorize as Court
2. Send email with "creditor claim" in subject → Should trigger creditor tracker
3. Send email from known heir → Should categorize as Family
4. Test invoice attachment → Should extract data and create approval

**Success Criteria:**
- 95%+ accuracy in categorization
- Templates auto-fill correctly
- Drafts created without errors
- SharePoint lists updated properly

---

### Phase 2: Deploy to Production (Week 2)

**Steps:**
1. Activate all flows
2. Monitor for first week
3. Collect user feedback
4. Adjust thresholds and rules

**Training:**
- Review draft emails before sending
- Update SharePoint data regularly
- Report any errors or misclassifications

---

### Phase 3: Optimization (Ongoing)

**Metrics to Track:**
- Time saved per email response (target: 80% reduction)
- Categorization accuracy (target: 95%+)
- User satisfaction (target: 4/5 stars)
- Error rate (target: <5%)

**Continuous Improvement:**
- Add new templates as needed
- Refine categorization rules
- Expand AI Builder models
- Add new SharePoint fields

---

## XI. ESTIMATED TIME & COST SAVINGS

**Before Automation:**
- Average time per email response: 15-30 minutes
- Emails per week: 20-50
- **Total time per week: 5-25 hours**

**After Automation:**
- Average time per email (review draft): 2-5 minutes
- Emails per week: 20-50
- **Total time per week: 0.5-4 hours**

**Time Savings: 80-90% reduction**

**Cost Savings:**
- Time valued at $50/hour: $250-1,250/week saved
- Annual savings: $13,000-$65,000

**ROI:**
- Power Automate cost: $15-40/month ($180-$480/year)
- **Net savings: $12,500-$64,500/year**

---

## XII. TROUBLESHOOTING

**Issue 1: Flow not triggering**
- **Check:** Email is in correct Outlook folder (Inbox)
- **Check:** Flow is turned ON
- **Check:** Connection to Outlook is valid
- **Fix:** Reconnect Outlook connector

**Issue 2: Template not auto-filling**
- **Check:** SharePoint list has data
- **Check:** Variable names match exactly
- **Fix:** Update replace() function with correct variable names

**Issue 3: AI Builder not extracting data**
- **Check:** AI Builder model is trained
- **Check:** Email format is supported
- **Fix:** Add more training data to AI Builder model

**Issue 4: Draft emails not appearing**
- **Check:** Outlook permissions for Power Automate
- **Check:** Email address in "To" field is valid
- **Fix:** Manually create draft as test

---

## XIII. FUTURE ENHANCEMENTS

**Phase 4 (Future):**
1. **AI-Powered Response Generation:**
   - Integrate GPT-4/Claude API
   - Fully generate responses (not just templates)
   - Learn from approved responses

2. **Voice Control:**
   - Dictate responses via Microsoft Cortana or mobile app
   - "Send estate update to all heirs"

3. **Mobile App:**
   - Approve emails on-the-go
   - Review estate status from phone

4. **Advanced Analytics:**
   - Dashboard showing email response times
   - Creditor claim trends
   - Estate progress visualization

5. **Multi-Estate Management:**
   - Scale to handle multiple estates simultaneously
   - Separate SharePoint sites per estate

---

**END OF POWER AUTOMATE FLOW CONFIGURATION - MASTER DOCUMENT**

**Deployment Status:** Ready for implementation
**Estimated Setup Time:** 8-16 hours (one-time)
**Estimated Learning Curve:** 2-4 weeks to full proficiency
**Support:** Microsoft Power Automate documentation + community forums
