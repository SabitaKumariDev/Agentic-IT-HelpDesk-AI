"""
Enterprise IT Knowledge Base Documents
Simulated knowledge base containing IT support documentation
for common enterprise IT issues and procedures.
"""

IT_KNOWLEDGE_BASE = [
    {
        "id": "kb-001",
        "title": "VPN Troubleshooting Guide",
        "category": "vpn",
        "tags": ["vpn", "connectivity", "network", "troubleshooting", "globalprotect", "cisco"],
        "content": """VPN Troubleshooting Guide - Enterprise IT

Common VPN Issues and Solutions:

1. VPN Client Not Connecting
   - Ensure you are connected to the internet first
   - Restart the VPN client application (Cisco AnyConnect or GlobalProtect)
   - Check if your corporate credentials have expired
   - Verify that your system clock is accurate (time sync issues can cause certificate failures)
   - Try connecting to an alternate VPN gateway server

2. VPN Disconnects Frequently
   - Check your internet connection stability
   - Disable any conflicting firewall or antivirus software temporarily
   - Update the VPN client to the latest version
   - If on WiFi, try switching to a wired connection
   - Contact IT if the issue persists after 3 reconnection attempts

3. Slow VPN Connection
   - Close unnecessary applications consuming bandwidth
   - Try connecting to a geographically closer VPN server
   - Split tunneling may help - contact IT to enable it
   - Run a speed test with and without VPN to isolate the issue

4. VPN Authentication Failures
   - Verify your corporate password hasn't expired
   - Re-authenticate with Okta MFA
   - Clear saved VPN credentials and re-enter them
   - Check if your account has been locked due to failed attempts

Escalation: If issues persist after following these steps, create a support ticket with category 'Network - VPN' and include your error messages.""",
        "source": "IT Operations Handbook v3.2",
        "last_updated": "2025-01-15"
    },
    {
        "id": "kb-002",
        "title": "Okta MFA Reset Procedures",
        "category": "security",
        "tags": ["okta", "mfa", "authentication", "security", "reset", "multi-factor"],
        "content": """Okta MFA Reset Procedures - Security Guide

How to Reset Okta Multi-Factor Authentication (MFA):

Self-Service Reset:
1. Navigate to https://company.okta.com/signin
2. Click 'Need help signing in?' at the bottom of the login page
3. Select 'Reset Multifactor Authentication'
4. Enter your corporate email address
5. You will receive a verification email - click the reset link
6. Follow the on-screen prompts to set up a new MFA method

Supported MFA Methods:
- Okta Verify (Push notification) - Recommended
- Google Authenticator or Microsoft Authenticator
- SMS verification (backup only)
- Hardware security key (YubiKey)

If Self-Service Fails:
1. Contact the IT Help Desk at ext. 5555 or helpdesk@company.com
2. Provide your employee ID and the email associated with your Okta account
3. IT will verify your identity through security questions
4. A temporary bypass code will be issued (valid for 24 hours)
5. Use the bypass code to log in and set up new MFA

Security Notes:
- Never share your MFA codes with anyone
- Report any suspicious MFA prompts you did not initiate
- MFA bypass codes expire after 24 hours
- Contact security team immediately if you suspect account compromise

Related: Password Reset Procedures (kb-005)""",
        "source": "Okta Security Guide v2.1",
        "last_updated": "2025-02-01"
    },
    {
        "id": "kb-003",
        "title": "Laptop WiFi Troubleshooting",
        "category": "hardware",
        "tags": ["wifi", "laptop", "wireless", "connectivity", "hardware", "network"],
        "content": """Laptop WiFi Troubleshooting Guide

Common WiFi Issues and Solutions:

1. WiFi Not Detecting Networks
   - Check if WiFi is enabled (look for hardware switch or Fn key combination)
   - Run Windows Network Troubleshooter: Settings > Network and Internet > Network troubleshooter
   - Restart the WiFi adapter: Device Manager > Network adapters > Right-click WiFi adapter > Disable then Enable
   - Update WiFi drivers from Device Manager
   - Restart your laptop

2. Connected but No Internet
   - Forget the network and reconnect with the correct password
   - Run 'ipconfig /release' then 'ipconfig /renew' in Command Prompt (admin)
   - Flush DNS cache: 'ipconfig /flushdns'
   - Check if other devices can connect to the same network
   - Try connecting to a different network to isolate the issue

3. Slow WiFi Connection
   - Move closer to the wireless access point
   - Check for interference from other devices (microwaves, Bluetooth)
   - Switch from 2.4GHz to 5GHz band if available
   - Close bandwidth-heavy applications
   - Contact IT to check the access point health

4. Corporate WiFi Authentication Issues
   - Ensure you're connecting to the correct SSID (Corp-Secure, not Guest)
   - Your corporate credentials may need refreshing - try logging out and back in
   - Certificate-based authentication may require re-enrollment
   - Contact IT if you see 'Authentication Failed' messages repeatedly

5. MacOS Specific:
   - Open System Preferences > Network > WiFi > Advanced > Remove old networks
   - Reset SMC and NVRAM if WiFi issues persist

Escalation: Create a ticket with category 'Hardware - WiFi' if troubleshooting steps do not resolve the issue.""",
        "source": "Employee IT Handbook v4.0",
        "last_updated": "2025-01-20"
    },
    {
        "id": "kb-004",
        "title": "Slack Access and Configuration",
        "category": "software",
        "tags": ["slack", "access", "software", "communication", "request", "channel"],
        "content": """Slack Access Requests and Configuration Guide

Requesting Slack Access:
1. New employees are automatically provisioned with Slack access on Day 1
2. If you do not have access, submit a request through the IT Service Portal
3. Go to https://serviceportal.company.com > Software Access > Slack
4. Select your department and manager for approval
5. Access is typically granted within 4 business hours

Joining Channels:
- Public channels: Browse and join directly
- Private channels: Request access from the channel admin
- Department channels: Auto-joined based on your department
- Project channels: Request through project manager

Common Slack Issues:
1. Cannot Log In
   - Slack uses SSO through Okta - ensure your Okta account is active
   - Clear browser cache and cookies
   - Try the desktop app instead of browser
   - If using 2FA, ensure your authenticator is synced

2. Notifications Not Working
   - Check Slack notification settings: Preferences > Notifications
   - Verify system notification permissions for Slack
   - Check Do Not Disturb schedule settings
   - Reinstall the Slack app if notifications are completely broken

3. Unable to Send Messages
   - Check your internet connection
   - Verify you have posting permissions in the channel
   - Ensure your account has not been deactivated
   - Contact the channel admin or IT support

Escalation: Contact IT at helpdesk@company.com for access issues.""",
        "source": "Software Access Guide v2.5",
        "last_updated": "2024-12-15"
    },
    {
        "id": "kb-005",
        "title": "Password Reset Procedures",
        "category": "security",
        "tags": ["password", "reset", "security", "credentials", "account", "locked"],
        "content": """Corporate Password Reset Procedures

Self-Service Password Reset:
1. Go to https://passwordreset.company.com
2. Enter your corporate email address
3. Complete MFA verification (Okta Verify or backup method)
4. Create a new password following the password policy:
   - Minimum 12 characters
   - At least one uppercase letter, one lowercase, one number, one special character
   - Cannot reuse last 10 passwords
   - Cannot contain your name or email
5. Your new password will sync across all corporate services within 15 minutes

Active Directory Password Reset:
- Press Ctrl+Alt+Delete on your Windows device
- Select 'Change a Password'
- Enter current password and new password twice
- Password syncs to email, VPN, and other services automatically

Password Expired While Remote:
1. Connect to VPN with your old password (if still within grace period)
2. Use Ctrl+Alt+Delete to change password while on VPN
3. Alternatively, use the self-service portal from any browser
4. If locked out, contact IT Help Desk for a temporary password

Account Lockout:
- Accounts lock after 5 failed login attempts
- Auto-unlock after 30 minutes
- For immediate unlock, contact IT Help Desk
- Provide your employee ID for identity verification

Related: Okta MFA Reset (kb-002)""",
        "source": "Security Policy Document v5.0",
        "last_updated": "2025-02-10"
    },
    {
        "id": "kb-006",
        "title": "Laptop Hardware Issues and Repair",
        "category": "hardware",
        "tags": ["laptop", "hardware", "repair", "screen", "keyboard", "battery"],
        "content": """Laptop Hardware Issues and Repair Guide

Common Hardware Issues:

1. Screen and Display Issues
   - Flickering: Update graphics drivers, check display cable connection
   - Dead pixels: Document the location and count, create a hardware ticket
   - Cracked screen: Do not attempt self-repair, create an urgent hardware ticket
   - External monitor not detected: Check cable, try different port, update drivers

2. Keyboard Issues
   - Keys not responding: Check for debris, try compressed air cleaning
   - Sticky keys: Clean with isopropyl alcohol on a cloth (not directly on keys)
   - Keyboard backlight not working: Check Fn key combinations
   - Complete keyboard failure: Connect external USB keyboard and create a repair ticket

3. Battery Issues
   - Battery draining fast: Check power settings, reduce screen brightness
   - Not charging: Try a different charger, check the charging port for debris
   - Battery health below 80%: Eligible for battery replacement - create a ticket
   - Swollen battery: STOP using immediately, contact IT for emergency replacement

4. Performance Issues
   - Running slow: Restart, close unnecessary apps, check disk space
   - Overheating: Clean vents, use on hard surface, check for high CPU processes
   - Blue screen errors: Note the error code, restart, create ticket if recurring

Repair Process:
1. Create a ticket through IT Service Portal or the IT Assistant
2. Include: Device model, serial number, detailed description of issue
3. IT will triage and assign a technician
4. Repair options: On-site repair, mail-in repair, or device replacement
5. Standard repair SLA: 3-5 business days
6. Critical repairs (no working device): Loaner device provided within 24 hours

Escalation: For urgent hardware issues affecting work, call IT at ext. 5555.""",
        "source": "Hardware Support Guide v3.1",
        "last_updated": "2025-01-25"
    },
    {
        "id": "kb-007",
        "title": "Email and Outlook Configuration",
        "category": "software",
        "tags": ["email", "outlook", "configuration", "calendar", "microsoft", "mobile"],
        "content": """Email and Microsoft Outlook Configuration Guide

Setting Up Outlook:
1. Desktop App (Windows and Mac)
   - Open Outlook, it should auto-detect your corporate email
   - Sign in with your corporate credentials through Okta SSO
   - Wait for mailbox synchronization (may take 15-30 minutes for first sync)

2. Mobile Setup (iOS and Android)
   - Download Microsoft Outlook from App Store or Google Play
   - Tap Add Account and enter your corporate email
   - Complete Okta MFA verification
   - Allow notification permissions for email alerts

3. Web Access
   - Go to https://outlook.office365.com
   - Sign in through Okta SSO
   - Full functionality available in browser

Common Email Issues:
1. Not Receiving Emails
   - Check junk or spam folder
   - Verify your mailbox is not full (50GB limit)
   - Check email rules that might be redirecting messages
   - Sync may be delayed - wait 5 minutes and refresh

2. Cannot Send Emails
   - Check attachment size (25MB limit per email)
   - Verify recipient email address is correct
   - Check if your outbound email is being blocked (contact IT)
   - Try sending from Outlook Web if desktop app fails

3. Calendar Issues
   - Calendar not syncing: Remove and re-add account
   - Cannot see shared calendars: Ask calendar owner to re-share
   - Meeting room booking: Use the Room Finder in Outlook

Escalation: For persistent email issues, contact IT with your email address and error messages.""",
        "source": "Employee IT Handbook v4.0",
        "last_updated": "2025-01-10"
    },
    {
        "id": "kb-008",
        "title": "Software Installation and Access Requests",
        "category": "software",
        "tags": ["software", "installation", "access", "request", "license", "admin"],
        "content": """Software Installation and Access Request Guide

Pre-Approved Software:
The following software can be installed without IT approval:
- Google Chrome, Firefox
- Zoom, Microsoft Teams
- Visual Studio Code
- Notepad++, Sublime Text
- 7-Zip, Adobe Acrobat Reader
Install via Software Center (Windows) or Self Service (Mac).

Requesting New Software:
1. Go to IT Service Portal > Software Requests
2. Fill out the request form:
   - Software name and version
   - Business justification
   - Number of licenses needed
   - Department and cost center
3. Requests are reviewed within 2 business days
4. Approved software will be deployed remotely or made available in Software Center

License Management:
- Check available licenses: IT Service Portal > My Software
- Return unused licenses when no longer needed
- License transfers require manager approval
- Annual license audits - respond promptly to audit requests

Admin Access Requests:
- Standard users do not have admin rights by default
- Temporary admin access (24hr) can be requested for specific installations
- Permanent admin access requires director-level approval
- All admin activities are logged for security

Escalation: Contact software-support@company.com for license issues.""",
        "source": "Software Access Guide v2.5",
        "last_updated": "2024-11-30"
    },
    {
        "id": "kb-009",
        "title": "Printer and Printing Troubleshooting",
        "category": "hardware",
        "tags": ["printer", "printing", "hardware", "network printer", "driver", "queue"],
        "content": """Printer and Printing Troubleshooting Guide

Setting Up a Network Printer:
1. Go to Settings > Printers & Scanners > Add a printer
2. Select the printer from the network list (printers are auto-discovered)
3. If not listed, click 'Add manually' and enter the printer IP address
4. Install the driver if prompted (drivers are available on Software Center)
5. Print a test page to verify

Common Printing Issues:

1. Print Job Stuck in Queue
   - Open Print Queue (right-click printer icon in taskbar)
   - Cancel all documents and restart the Print Spooler service
   - Windows: Run 'services.msc' > find Print Spooler > Restart
   - Mac: System Preferences > Printers > Reset printing system
   - Re-submit your print job

2. Printer Not Found on Network
   - Ensure you are on the corporate network (Corp-Secure WiFi or wired)
   - Check if the printer is powered on and online (status light should be solid green)
   - Try adding by IP address: ask your floor admin for the printer IP
   - VPN users: network printers are not accessible over VPN - use web print portal instead

3. Poor Print Quality
   - Run the printer's built-in cleaning cycle (access via printer's touch panel)
   - Check toner/ink levels on the printer display
   - Try printing from a different application to rule out software issues
   - For color issues, run a color calibration from the printer menu

4. Secure Print / Pull Printing
   - All corporate printers use secure pull printing
   - Send your print job normally, then go to any printer
   - Tap your employee badge on the printer's card reader
   - Select your job from the queue and print
   - Uncollected jobs are deleted after 24 hours

Escalation: For hardware failures (paper jams, error codes), create a ticket with category 'Hardware - Printer' including the printer name and location.""",
        "source": "Employee IT Handbook v4.0",
        "last_updated": "2025-02-01"
    },
    {
        "id": "kb-010",
        "title": "Microsoft Teams Setup and Troubleshooting",
        "category": "software",
        "tags": ["teams", "microsoft", "video", "conferencing", "meetings", "chat", "collaboration"],
        "content": """Microsoft Teams Setup and Troubleshooting Guide

Initial Setup:
1. Download Microsoft Teams from Software Center (Windows/Mac)
2. Sign in with your corporate email through Okta SSO
3. Teams will sync your contacts, chats, and calendar automatically
4. Mobile: Download from App Store/Google Play and sign in

Common Issues:

1. Cannot Join Meetings
   - Check your internet connection and bandwidth (video calls need 1.5+ Mbps)
   - Clear Teams cache: close Teams, delete contents of %appdata%/Microsoft/Teams/Cache
   - Try joining from the browser (teams.microsoft.com) as a fallback
   - Ensure your system clock is accurate (clock drift causes auth failures)
   - Restart Teams if the 'Join' button is grayed out

2. Audio or Microphone Not Working
   - Check Teams Settings > Devices and verify the correct mic/speaker is selected
   - Test audio with the 'Make a test call' feature in Settings > Devices
   - Check system audio settings - ensure Teams has microphone permission
   - If using a headset, try unplugging and re-plugging it
   - Ensure no other app (Zoom, Slack) is using the microphone

3. Screen Sharing Issues
   - Windows: Grant screen recording permission in Settings > Privacy > Screen recording
   - Mac: System Preferences > Security & Privacy > Screen Recording > enable Teams
   - If sharing a specific window, ensure the window is not minimized
   - Try sharing 'Desktop' instead of a specific window if issues persist

4. Teams Running Slow
   - Clear the Teams cache (see step above)
   - Disable GPU hardware acceleration: Settings > General > uncheck GPU acceleration
   - Close unnecessary tabs and applications
   - Check for Teams updates: click your profile > Check for updates

5. Chat Messages Not Sending
   - Check if you are in 'Available' status (not offline)
   - Verify internet connectivity
   - Try sending from Teams web app to isolate the issue
   - If persistent, sign out and sign back in

Escalation: Contact IT for Teams admin issues (channel creation, guest access, policy changes).""",
        "source": "Collaboration Tools Guide v3.0",
        "last_updated": "2025-01-28"
    },
    {
        "id": "kb-011",
        "title": "OneDrive and SharePoint File Sync",
        "category": "software",
        "tags": ["onedrive", "sharepoint", "file sync", "cloud storage", "backup", "documents"],
        "content": """OneDrive and SharePoint File Sync Guide

Setting Up OneDrive Sync:
1. OneDrive is pre-installed on corporate laptops
2. Sign in with your corporate email when prompted
3. Choose which folders to sync (default: Desktop, Documents, Pictures)
4. Files are automatically backed up to the cloud
5. Access files from any device at onedrive.com

SharePoint Library Sync:
1. Navigate to the SharePoint site in your browser
2. Click 'Sync' button in the document library toolbar
3. OneDrive will handle the sync - files appear in File Explorer under the site name
4. Changes sync automatically when connected to the internet

Common Issues:

1. Files Not Syncing
   - Check the OneDrive icon in the system tray for errors (red X or yellow warning)
   - Right-click OneDrive icon > View sync problems for specific file errors
   - Common cause: file name too long (max 400 characters for full path)
   - Common cause: unsupported characters in file names (# % & * : < > ? / |)
   - Pause and resume sync: right-click OneDrive icon > Pause syncing > Resume

2. Storage Quota Exceeded
   - Corporate OneDrive quota: 1 TB per user
   - Check usage: OneDrive Settings > Account > Storage
   - Move large files to SharePoint team libraries instead
   - Empty OneDrive recycle bin to reclaim space
   - Request quota increase through IT Service Portal if needed

3. Conflicting Copies
   - OneDrive creates copies when two people edit the same file offline
   - Look for files with 'conflicting copy' in the name
   - Manually merge changes and delete the conflicting copy
   - Prevent conflicts: use Office co-authoring (edit simultaneously online)

4. SharePoint Sync Errors
   - 'This library can't be synced' - ensure OneDrive is up to date
   - 'Access denied' - request permissions from the SharePoint site owner
   - Too many items: SharePoint libraries with 300,000+ items may fail to sync
   - Solution: sync specific folders instead of the entire library

5. Recovering Deleted Files
   - OneDrive Recycle Bin retains files for 93 days
   - SharePoint Recycle Bin: two stages (site recycle bin + site collection recycle bin)
   - For files older than 93 days, contact IT for backup restoration

Escalation: Contact IT for quota increases, permission issues, or backup restoration.""",
        "source": "Cloud Storage Guide v2.0",
        "last_updated": "2025-02-05"
    },
    {
        "id": "kb-012",
        "title": "Zoom Video Conferencing Setup",
        "category": "software",
        "tags": ["zoom", "video", "conferencing", "meetings", "webinar", "recording"],
        "content": """Zoom Video Conferencing Setup and Troubleshooting

Installation:
1. Download Zoom from Software Center (Windows/Mac)
2. Sign in using 'SSO' option with company domain: company.zoom.us
3. Complete Okta authentication when redirected
4. Mobile: Download Zoom from App Store/Google Play

Scheduling Meetings:
- From Zoom app: click 'Schedule' and configure meeting options
- From Outlook: use the Zoom Outlook plugin (auto-installed) to add Zoom to calendar events
- Meeting links are automatically generated and included in calendar invites
- Enable 'Waiting Room' for external participants as per company policy

Common Issues:

1. Cannot Sign In
   - Use SSO sign-in, not regular email/password
   - Company domain: company.zoom.us
   - If Okta authentication fails, clear browser cookies and retry
   - Check if your Zoom license is active: contact IT if you see 'Basic' instead of 'Licensed'

2. Poor Video or Audio Quality
   - Check bandwidth: Zoom needs 3.0 Mbps for HD video
   - Close other bandwidth-heavy applications
   - Use wired connection instead of WiFi when possible
   - In Zoom settings, lower video quality: Settings > Video > uncheck HD
   - Use 'Touch up my appearance' sparingly as it uses more CPU

3. Recording Issues
   - Cloud recording: available for Licensed users, recordings saved to zoom.us/recording
   - Local recording: saved to Documents/Zoom folder by default
   - 'Recording failed' error: check available disk space (local) or cloud storage quota
   - Cloud recordings are automatically deleted after 120 days
   - For compliance: all external meeting recordings require participant consent notification

4. Zoom Crashing or Freezing
   - Update Zoom to the latest version: Zoom app > check for updates
   - Clear Zoom cache: uninstall and reinstall from Software Center
   - Disable virtual backgrounds if experiencing performance issues
   - Ensure graphics drivers are up to date

5. Breakout Rooms and Webinars
   - Breakout rooms: available for meetings with 2+ participants
   - Webinar license: request through IT Service Portal if needed
   - Webinar practice session: use 'Practice Session' before going live
   - Max participants: 300 (meeting), 500 (webinar) with current license

Escalation: For license upgrades or account issues, submit a request through IT Service Portal.""",
        "source": "Collaboration Tools Guide v3.0",
        "last_updated": "2025-01-30"
    }
]
