from django.core.management.base import BaseCommand
from legal.models import LegalDocument
import datetime


class Command(BaseCommand):
    help = 'Seed Terms, Privacy Policy, and Refund Policy as HTML content'

    def handle(self, *args, **kwargs):
        effective_date = datetime.date(2026, 6, 30)

        documents = [
            {
                'doc_type': 'terms',
                'title': 'Terms and Conditions',
                'content_html': TERMS_HTML,
            },
            {
                'doc_type': 'privacy',
                'title': 'Privacy Policy',
                'content_html': PRIVACY_HTML,
            },
            {
                'doc_type': 'refund',
                'title': 'Refund and Cancellation Policy',
                'content_html': REFUND_HTML,
            },
        ]

        for doc in documents:
            obj, created = LegalDocument.objects.update_or_create(
                doc_type=doc['doc_type'],
                defaults={
                    'title': doc['title'],
                    'content_html': doc['content_html'],
                    'version': '1.0',
                    'effective_date': effective_date,
                    'last_updated': effective_date,
                    'is_active': True,
                }
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"  ✅ {action}: {doc['title']}")

        self.stdout.write(self.style.SUCCESS('\n✅ All legal documents seeded!'))


# ─── HTML CONTENT BELOW ──────────────────────────────────────────

TERMS_HTML = """
<h1>Terms and Conditions</h1>
<p><strong>Application Name:</strong> Rechargic</p>
<p><strong>Operated by:</strong> IGNIVOX TECH PRIVATE LIMITED</p>
<p><strong>Registered Address:</strong> 1578/1452/17, Haralur Road, Kasavana, HSR Layout, Bangalore South, Bangalore – 560102, Karnataka, India</p>
<p><strong>Email:</strong> support@rechargic.in</p>
<p><strong>Website:</strong> https://rechargic.in</p>
<p><strong>Effective Date:</strong> 30 June 2026</p>
<p><strong>Last Updated:</strong> 30 June 2026</p>

<h2>1. Introduction and Acceptance</h2>
<p>Welcome to Rechargic, a digital payment and utility services platform operated by IGNIVOX TECH PRIVATE LIMITED ("Company", "We", "Us", or "Our"), a company incorporated under the Companies Act, 2013.</p>
<p>These Terms and Conditions ("Terms") constitute a legally binding agreement between You ("User", "You", or "Your") and IGNIVOX TECH PRIVATE LIMITED governing Your access to and use of the Rechargic mobile application, website, and all associated services (collectively referred to as the "Platform" or "App").</p>
<p>By downloading, installing, accessing, or using the Rechargic App, You confirm that:</p>
<ol>
<li>You have read and understood these Terms;</li>
<li>You are at least 18 years of age, or if You are a minor (below 18 years), that You are using the App under the supervision and consent of a parent or legal guardian;</li>
<li>You agree to be legally bound by these Terms and our Privacy Policy and Refund Policy, which are incorporated herein by reference;</li>
<li>If You do not agree with any part of these Terms, You must immediately discontinue use of the App.</li>
</ol>

<h2>2. Definitions</h2>
<table>
<tr><th>Term</th><th>Definition</th></tr>
<tr><td>App / Platform</td><td>The Rechargic mobile application and related web interfaces</td></tr>
<tr><td>User / Account Holder</td><td>Any individual who registers and uses the App</td></tr>
<tr><td>Services</td><td>All services offered through the App including recharges, bill payments, wallet, and other utility services</td></tr>
<tr><td>Wallet</td><td>The in-app digital wallet maintained for Users to store and transact funds</td></tr>
<tr><td>Transaction</td><td>Any financial activity conducted through the Platform including recharges, bill payments, wallet top-ups, and fund transfers</td></tr>
<tr><td>Third-Party Service Provider</td><td>Telecom operators, utility companies, payment gateways, and other external parties whose services are facilitated through the App</td></tr>
<tr><td>KYC</td><td>Know Your Customer — the identity verification process as mandated under applicable laws</td></tr>
<tr><td>OTP</td><td>One-Time Password used for authentication</td></tr>
<tr><td>BBPS</td><td>Bharat Bill Payment System — an RBI-mandated interoperable bill payment platform</td></tr>
<tr><td>AEPS</td><td>Aadhaar Enabled Payment System</td></tr>
</table>

<h2>3. Eligibility and Registration</h2>
<h3>3.1 Eligibility</h3>
<ul>
<li>You must be a citizen or resident of India and at least 18 years of age to independently use the App and access financial services.</li>
<li>Users below 18 years may use the App solely under the supervision of a parent or legal guardian who accepts responsibility for all transactions.</li>
<li>You must possess a valid Indian mobile phone number registered in Your name.</li>
<li>Corporate entities may use the App only if duly authorised by a resolution or written consent of the entity.</li>
</ul>

<h3>3.2 Account Registration</h3>
<ul>
<li>Registration requires Your valid Indian mobile phone number, which will be verified via OTP.</li>
<li>You must provide accurate, complete, and current information during signup (including Your name) and promptly update any changes.</li>
<li>You are solely responsible for maintaining the confidentiality of Your account credentials, including OTP and login sessions.</li>
<li>Only one account is permitted per mobile number. Creating multiple accounts is strictly prohibited.</li>
<li>IGNIVOX TECH PRIVATE LIMITED reserves the right to verify Your identity and may suspend accounts pending verification.</li>
</ul>

<h3>3.3 KYC Requirements</h3>
<ul>
<li>Certain services (including but not limited to Wallet top-up above prescribed limits and AEPS) may require completion of Know Your Customer (KYC) verification as mandated under the Prevention of Money Laundering Act, 2002 (PMLA), RBI Prepaid Payment Instrument (PPI) Guidelines, and other applicable regulations.</li>
<li>KYC documents may include Aadhaar, PAN card, or other government-issued identity proof.</li>
<li>Failure to complete KYC within the stipulated time may result in restriction or suspension of certain services.</li>
</ul>

<h2>4. Services Offered</h2>
<p>Rechargic provides the following digital services through its App:</p>

<h3>4.1 Mobile Recharge</h3>
<p>Prepaid mobile recharge for operators including Airtel, Jio, Vi (Vodafone Idea), and BSNL across all telecom circles in India.</p>

<h3>4.2 DTH Recharge</h3>
<p>DTH plan recharge for providers including Tata Play, Sun Direct, Dish TV, d2h, and Airtel Digital TV.</p>

<h3>4.3 Electricity Bill Payment</h3>
<p>Bill payment for electricity distribution companies (DISCOMs) including BESCOM, MSEDCL, TNPDCL, PSPCL, AEML, and others across India.</p>

<h3>4.4 Broadband Bill Payment</h3>
<p>Bill payment for broadband internet service providers including Airtel Broadband, JioFiber, ACT Fibernet, and BSNL Broadband.</p>

<h3>4.5 LPG Gas Booking</h3>
<p>LPG cylinder booking for HP Gas, Bharat Gas, and Indane Gas.</p>

<h3>4.6 Water Bill Payment</h3>
<p>Water utility bill payment for boards including BWSSB, Delhi Jal Board, MCGM, KWA, and others.</p>

<h3>4.7 Insurance Premium Payment</h3>
<p>Payment of insurance premiums for providers including HDFC Life, SBI Life, ICICI Prudential Life, and TATA AIA Life Insurance.</p>

<h3>4.8 FASTag Recharge</h3>
<p>Recharge for FASTag accounts issued by banks including HDFC Bank, ICICI Bank, and SBI.</p>

<h3>4.9 Credit Card Bill Payment</h3>
<p>Payment of credit card outstanding bills.</p>

<h3>4.10 OTT Subscriptions</h3>
<p>Subscription or renewal for OTT (Over-The-Top) streaming platforms.</p>

<h3>4.11 Wallet Services</h3>
<p>In-app digital wallet to store funds, add money, transfer to other Rechargic users, and make payments.</p>

<h3>4.12 Bharat Connect / BBPS Services</h3>
<p>Bharat Bill Payment System (BBPS) enabled services for bill aggregation and payment.</p>

<h3>4.13 AEPS (Aadhaar Enabled Payment System)</h3>
<p>Aadhaar-based banking services subject to KYC compliance and applicable RBI regulations.</p>

<h3>4.14 Rewards, Cashbacks, and Vouchers</h3>
<p>Loyalty rewards, cashbacks, referral bonuses, and vouchers as announced by the Company from time to time.</p>

<blockquote>Note: The availability of specific services may vary by region, operator, or regulatory requirements and is subject to change without prior notice. The Company acts as an intermediary / aggregator and facilitates access to services offered by third-party providers.</blockquote>

<h2>5. Wallet and Payments</h2>
<h3>5.1 Wallet</h3>
<ul>
<li>The Rechargic Wallet is a semi-closed Prepaid Payment Instrument (PPI) operated in compliance with the Reserve Bank of India (RBI) Master Direction on Prepaid Payment Instruments (as amended from time to time).</li>
<li>Wallet funds can be used for transactions within the Platform.</li>
<li>The maximum wallet balance at any point shall be subject to applicable RBI limits and KYC level.</li>
<li>Wallet-to-wallet transfers are permitted only to registered Rechargic users.</li>
<li>Wallet funds are non-transferable to external bank accounts unless expressly permitted under applicable RBI regulations.</li>
</ul>

<h3>5.2 Adding Money to Wallet</h3>
<ul>
<li>Money can be added via supported payment methods including UPI, net banking, and debit/credit cards.</li>
<li>We use third-party payment gateways to process fund additions. By using these methods, You agree to the terms of the respective payment gateway.</li>
<li>All additions to the Wallet are final once confirmed by the payment gateway.</li>
</ul>

<h3>5.3 Transaction Limits</h3>
<p>Transaction limits (per transaction, daily, and monthly) apply as per RBI guidelines, KYC completion level, and Company policy. These limits are displayed within the App and may be updated from time to time.</p>

<h3>5.4 Failed and Pending Transactions</h3>
<ul>
<li>Transactions may fail due to network issues, third-party service unavailability, incorrect credentials, or payment gateway errors.</li>
<li>For failed transactions where the amount has been debited, the refund process shall be governed by our Refund Policy.</li>
</ul>

<h2>6. Referral Programme</h2>
<ul>
<li>Users can refer Rechargic to new users using their unique referral code.</li>
<li>Referral bonuses are credited upon successful signup and/or first completed transaction by the referred user, as per the terms notified within the App.</li>
<li>Referral bonuses are credited to the Wallet and may be subject to expiry, minimum usage requirements, and other restrictions.</li>
<li>Fraudulent or artificial referrals (using fake accounts, bots, virtual numbers, or automated means) will result in forfeiture of all referral earnings and termination of account.</li>
<li>IGNIVOX TECH PRIVATE LIMITED reserves the right to modify, suspend, or terminate the referral programme at any time without prior notice.</li>
</ul>

<h2>7. User Obligations and Prohibited Conduct</h2>
<h3>7.1 User Obligations</h3>
<p>You agree to:</p>
<ul>
<li>Use the App solely for lawful purposes and in compliance with all applicable Indian laws.</li>
<li>Provide accurate, truthful, and complete information during registration and transactions.</li>
<li>Not share Your account credentials, OTPs, or session tokens with any third party.</li>
<li>Immediately notify Us of any unauthorised access to or use of Your account.</li>
<li>Maintain sufficient balance before initiating transactions.</li>
<li>Comply with all KYC and verification requirements as applicable.</li>
</ul>

<h3>7.2 Prohibited Conduct</h3>
<p>You shall not:</p>
<ul>
<li>Use the App for any illegal, fraudulent, or unauthorised purpose.</li>
<li>Attempt to reverse-engineer, decompile, or tamper with the App's source code, APIs, or infrastructure.</li>
<li>Engage in money laundering, terrorist financing, or any activity in violation of the PMLA, 2002, FEMA, 1999, or any other law.</li>
<li>Use automated scripts, bots, or crawlers to access the App.</li>
<li>Create multiple accounts or impersonate any person or entity.</li>
<li>Exploit any bugs or vulnerabilities in the App for personal gain.</li>
<li>Misuse or abuse the referral, rewards, or cashback programmes.</li>
<li>Use the App to transmit unsolicited commercial communications (spam).</li>
<li>Circumvent or bypass any security, authentication, or anti-fraud measures.</li>
</ul>
<p><strong>Consequences:</strong> Violation may result in immediate account suspension, blacklisting, forfeiture of wallet balance (where legally permissible), and/or legal action under the Information Technology Act, 2000, Bharatiya Nyaya Sanhita, 2023, or other applicable Indian laws.</p>

<h2>8. Intellectual Property</h2>
<ul>
<li>All content, trademarks, logos, brand names, source code, UI/UX design, graphics, and other intellectual property on the Platform are owned by or licensed to IGNIVOX TECH PRIVATE LIMITED.</li>
<li>These Terms do not grant You any right, title, or interest in any intellectual property of the Company.</li>
<li>You may not reproduce, distribute, publish, modify, or create derivative works from our content without prior written permission.</li>
<li>"Rechargic" and associated marks are trademarks of IGNIVOX TECH PRIVATE LIMITED. Unauthorised use is strictly prohibited.</li>
</ul>

<h2>9. Third-Party Services and Links</h2>
<ul>
<li>Rechargic acts as an intermediary / aggregator facilitating access to third-party services (telecom operators, utility boards, payment gateways, insurance providers, etc.).</li>
<li>We are not responsible for the quality, accuracy, pricing, availability, or terms of any third-party service.</li>
<li>Your transactions with third-party service providers are governed by their respective terms and conditions and the applicable regulatory framework.</li>
<li>The App may contain links to third-party websites. We do not endorse, control, or assume any responsibility for the content of such websites.</li>
</ul>

<h2>10. Privacy and Data Protection</h2>
<p>Your use of the App is subject to our Privacy Policy, incorporated herein by reference. By using the App, You consent to the collection, processing, storage, and use of Your personal data as described in the Privacy Policy, in accordance with:</p>
<ul>
<li>The Information Technology Act, 2000 and IT (Amendment) Act, 2008</li>
<li>The IT (Reasonable Security Practices and Procedures and Sensitive Personal Data or Information) Rules, 2011</li>
<li>The Digital Personal Data Protection Act, 2023 (DPDPA)</li>
</ul>

<h2>11. Disclaimers and Limitation of Liability</h2>
<h3>11.1 Disclaimer of Warranties</h3>
<p>THE PLATFORM AND ALL SERVICES ARE PROVIDED ON AN "AS IS" AND "AS AVAILABLE" BASIS WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.</p>
<p>We do not warrant that:</p>
<ul>
<li>The App will be error-free, uninterrupted, or secure at all times;</li>
<li>Transactions will be processed without delay or failure;</li>
<li>Information provided through third-party services will be accurate.</li>
</ul>

<h3>11.2 Limitation of Liability</h3>
<ul>
<li>To the maximum extent permitted under applicable Indian law, IGNIVOX TECH PRIVATE LIMITED shall not be liable for any indirect, incidental, consequential, special, or punitive damages arising from Your use of the Platform.</li>
<li>Our aggregate liability for any claim shall not exceed the amount of the specific transaction giving rise to the claim.</li>
<li>We are not liable for losses arising from third-party service failures, telecom network outages, banking system errors, or user negligence (e.g., sharing OTPs with third parties).</li>
</ul>

<h2>12. Indemnification</h2>
<p>You agree to indemnify, defend, and hold harmless IGNIVOX TECH PRIVATE LIMITED and its directors, officers, employees, agents, and partners from and against any claims, liabilities, damages, costs, and expenses (including reasonable attorneys' fees) arising out of or relating to:</p>
<ol>
<li>Your breach of these Terms;</li>
<li>Your use or misuse of the Platform;</li>
<li>Your violation of any applicable law or third-party rights;</li>
<li>Any transactions initiated by You;</li>
<li>Fraudulent or unauthorised activity conducted through Your account.</li>
</ol>

<h2>13. Suspension and Termination</h2>
<h3>13.1 By the Company</h3>
<p>We reserve the right to suspend, restrict, or terminate Your account at any time, with or without prior notice, for:</p>
<ul>
<li>Breach of these Terms or applicable law;</li>
<li>Detected fraudulent or suspicious activity;</li>
<li>Non-compliance with KYC or regulatory requirements;</li>
<li>Compliance with court or regulatory orders;</li>
<li>Prolonged account inactivity (as defined by Company policy).</li>
</ul>

<h3>13.2 By the User</h3>
<p>You may delete Your account at any time via the App settings. Upon account deletion:</p>
<ul>
<li>Your personal data will be handled per our Privacy Policy.</li>
<li>Pending transactions will be processed; unclaimed Wallet balance handling will be subject to RBI regulations and applicable law.</li>
<li>Unused referral rewards, cashbacks, and vouchers will be forfeited.</li>
</ul>

<h2>14. Governing Law and Dispute Resolution</h2>
<h3>14.1 Governing Law</h3>
<p>These Terms shall be governed by and construed in accordance with the laws of India, without regard to its conflict of laws principles.</p>

<h3>14.2 Jurisdiction</h3>
<p>The courts at Bangalore, Karnataka, India shall have exclusive jurisdiction over any dispute arising out of or relating to these Terms or Your use of the App.</p>

<h3>14.3 Dispute Resolution Process</h3>
<ol>
<li><strong>Step 1 — Informal Resolution:</strong> Contact us at support@rechargic.in with a detailed description of Your grievance. We will endeavour to resolve it within 15 (fifteen) working days.</li>
<li><strong>Step 2 — Grievance Officer:</strong> If unresolved, escalate to our Grievance Officer (details in Section 17). The Grievance Officer will aim to resolve the matter within 30 (thirty) days.</li>
<li><strong>Step 3 — Legal Proceedings:</strong> If the dispute remains unresolved, either party may initiate appropriate legal proceedings before courts of competent jurisdiction at Bangalore.</li>
</ol>
<p>Nothing in this section shall prevent either party from seeking urgent interim or injunctive relief.</p>

<h2>15. Amendments to Terms</h2>
<ul>
<li>IGNIVOX TECH PRIVATE LIMITED may revise these Terms at any time by updating this document.</li>
<li>Material changes will be notified via in-app notifications, push notifications, or email, with a revised "Last Updated" date.</li>
<li>Continued use of the App following notification of changes constitutes Your acceptance of the updated Terms.</li>
<li>If You disagree with the revised Terms, You must stop using the App and may delete Your account.</li>
</ul>

<h2>16. Force Majeure</h2>
<p>IGNIVOX TECH PRIVATE LIMITED shall not be liable for any delay or failure in performance of its obligations if such delay or failure results from circumstances beyond its reasonable control, including acts of God, government actions, power failures, internet disruptions, cyberattacks, pandemics, civil unrest, or any other event of force majeure.</p>

<h2>17. Grievance Redressal</h2>
<p>In accordance with the Information Technology Act, 2000 and the IT (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021, our Grievance Officer's details are:</p>
<table>
<tr><td><strong>Designation</strong></td><td>Grievance Officer</td></tr>
<tr><td><strong>Company</strong></td><td>IGNIVOX TECH PRIVATE LIMITED</td></tr>
<tr><td><strong>Address</strong></td><td>1578/1452/17, Haralur Road, Kasavana, HSR Layout, Bangalore South, Bangalore – 560102, Karnataka, India</td></tr>
<tr><td><strong>Email</strong></td><td>grievance@rechargic.in</td></tr>
<tr><td><strong>Working Hours</strong></td><td>Monday to Friday, 10:00 AM – 6:00 PM IST (excluding public holidays)</td></tr>
</table>
<p>Grievances will be acknowledged within 24 hours and resolved within 30 days of receipt.</p>

<h2>18. Severability</h2>
<p>If any provision of these Terms is found invalid, illegal, or unenforceable by a court of competent jurisdiction, such provision shall be modified to the minimum extent necessary or severed without affecting the validity and enforceability of the remaining provisions.</p>

<h2>19. Entire Agreement</h2>
<p>These Terms, together with the Privacy Policy and Refund Policy, constitute the entire agreement between You and IGNIVOX TECH PRIVATE LIMITED with respect to the Platform and supersede all prior oral or written agreements, representations, and understandings.</p>

<h2>20. Contact Us</h2>
<table>
<tr><td><strong>Company</strong></td><td>IGNIVOX TECH PRIVATE LIMITED</td></tr>
<tr><td><strong>Address</strong></td><td>1578/1452/17, Haralur Road, Kasavana, HSR Layout, Bangalore South, Bangalore – 560102, Karnataka, India</td></tr>
<tr><td><strong>Support Email</strong></td><td>support@rechargic.in</td></tr>
<tr><td><strong>Grievance Email</strong></td><td>grievance@rechargic.in</td></tr>
<tr><td><strong>Website</strong></td><td>https://rechargic.in</td></tr>
</table>

<p><em>These Terms and Conditions are effective from 30 June 2026.</em></p>
<p><em>© 2026 IGNIVOX TECH PRIVATE LIMITED. All Rights Reserved.</em></p>

"""

PRIVACY_HTML = """
<h1>Privacy Policy</h1>
<p><strong>Application Name:</strong> Rechargic</p>
<p><strong>Operated by:</strong> IGNIVOX TECH PRIVATE LIMITED</p>
<p><strong>Registered Address:</strong> 1578/1452/17, Haralur Road, Kasavana, HSR Layout, Bangalore South, Bangalore – 560102, Karnataka, India</p>
<p><strong>Email:</strong> privacy@rechargic.in</p>
<p><strong>Website:</strong> https://rechargic.in</p>
<p><strong>Effective Date:</strong> 30 June 2026</p>
<p><strong>Last Updated:</strong> 30 June 2026</p>

<h2>1. Introduction</h2>
<p>IGNIVOX TECH PRIVATE LIMITED ("Company", "We", "Us", or "Our"), the operator of Rechargic, is committed to protecting Your personal data and privacy. This Privacy Policy ("Policy") describes how We collect, use, store, share, and protect information about You ("User", "You", or "Your") when You use the Rechargic mobile application and related services (the "Platform").</p>
<p>This Policy is drafted in compliance with:</p>
<ul>
<li>The Information Technology Act, 2000 (IT Act)</li>
<li>IT (Amendment) Act, 2008</li>
<li>IT (Reasonable Security Practices and Procedures and Sensitive Personal Data or Information) Rules, 2011 (SPDI Rules)</li>
<li>Digital Personal Data Protection Act, 2023 (DPDPA)</li>
<li>Reserve Bank of India (RBI) guidelines on data security for payment systems</li>
<li>Telecom Regulatory Authority of India (TRAI) regulations as applicable</li>
</ul>
<p>By using the Rechargic App, You consent to the collection and use of Your personal data as described in this Policy. If You do not agree to this Policy, please do not use the App.</p>

<h2>2. Definitions</h2>
<table>
<tr><th>Term</th><th>Meaning</th></tr>
<tr><td>Personal Data / Personal Information</td><td>Any information that identifies or can identify You as an individual</td></tr>
<tr><td>Sensitive Personal Data or Information (SPDI)</td><td>Financial information, payment details, biometric data, passwords, and other categories listed under SPDI Rules, 2011</td></tr>
<tr><td>Data Principal</td><td>You, the individual whose personal data is being processed</td></tr>
<tr><td>Data Fiduciary</td><td>IGNIVOX TECH PRIVATE LIMITED, which determines the purpose and means of processing Your data</td></tr>
<tr><td>Processing</td><td>Collection, storage, use, alteration, sharing, or deletion of personal data</td></tr>
<tr><td>Consent Manager</td><td>As defined under DPDPA, 2023</td></tr>
</table>

<h2>3. Information We Collect</h2>
<p>We collect the following categories of information:</p>

<h3>3.1 Information You Provide Directly</h3>
<table>
<tr><th>Category</th><th>Examples</th></tr>
<tr><td>Identity Information</td><td>Full name, date of birth</td></tr>
<tr><td>Contact Information</td><td>Mobile number, email address</td></tr>
<tr><td>Profile Information</td><td>Profile picture, preferred operator (SIM)</td></tr>
<tr><td>KYC Documents</td><td>Aadhaar number, PAN card number, government-issued ID</td></tr>
<tr><td>Financial Information</td><td>Payment card details (processed by payment gateway), UPI ID, bank account details (for AEPS)</td></tr>
<tr><td>Communications</td><td>Messages or queries sent to Our support team</td></tr>
</table>

<h3>3.2 Information Collected Automatically</h3>
<table>
<tr><th>Category</th><th>Examples</th></tr>
<tr><td>Device Information</td><td>Device model, OS version, unique device identifiers</td></tr>
<tr><td>Usage Data</td><td>App features used, screens visited, session duration, transaction history</td></tr>
<tr><td>Location Data</td><td>Approximate or precise location (where You grant permission)</td></tr>
<tr><td>Log Data</td><td>IP address, access timestamps, error logs</td></tr>
<tr><td>Network Information</td><td>Mobile operator, connection type</td></tr>
</table>

<h3>3.3 Information from Third Parties</h3>
<ul>
<li><strong>Payment Gateways:</strong> Transaction status and confirmation data</li>
<li><strong>Telecom Operators / Utility Providers:</strong> Account or consumer information retrieved during bill fetch</li>
<li><strong>KYC Providers:</strong> Identity verification results from Aadhaar-based or PAN-based verification services</li>
<li><strong>Referral Sources:</strong> Information about Users who referred You</li>
</ul>

<h2>4. How We Use Your Information</h2>
<table>
<tr><th>Purpose</th><th>Legal Basis (Under DPDPA / SPDI Rules)</th></tr>
<tr><td>Account creation and authentication (OTP verification)</td><td>Consent / Legitimate Purpose</td></tr>
<tr><td>Processing transactions (recharges, bill payments, wallet operations)</td><td>Performance of Contract</td></tr>
<tr><td>Displaying personalised offers, plans, and recommendations</td><td>Consent</td></tr>
<tr><td>KYC verification and regulatory compliance</td><td>Legal Obligation</td></tr>
<tr><td>Fraud detection, risk management, and security</td><td>Legitimate Interest / Legal Obligation</td></tr>
<tr><td>Sending transactional notifications (SMS, email, push)</td><td>Contract / Consent</td></tr>
<tr><td>Sending promotional communications (offers, cashbacks)</td><td>Consent</td></tr>
<tr><td>Wallet management and fund transfers</td><td>Contract</td></tr>
<tr><td>Customer support and grievance redressal</td><td>Legitimate Interest</td></tr>
<tr><td>Analytics and App performance improvement</td><td>Legitimate Interest</td></tr>
<tr><td>Compliance with court orders, regulatory requirements, and law enforcement</td><td>Legal Obligation</td></tr>
</table>

<h2>5. Sensitive Personal Data or Information (SPDI)</h2>
<p>Under the SPDI Rules, 2011, We treat the following as Sensitive Personal Data:</p>
<ul>
<li>Financial information including payment card data, bank account details, UPI credentials</li>
<li>Aadhaar number and biometric data used for AEPS</li>
<li>PAN card details</li>
</ul>
<p>We:</p>
<ul>
<li>Collect SPDI only with Your explicit consent</li>
<li>Use SPDI strictly for the stated purposes</li>
<li>Do not share SPDI with third parties except as described in Section 6</li>
<li>Store SPDI with appropriate encryption and security measures</li>
</ul>

<h2>6. Sharing of Your Information</h2>
<p>We do not sell Your personal data. We may share Your information with:</p>

<h3>6.1 Service Partners and Third-Party Providers</h3>
<ul>
<li>Telecom operators and utility companies — to complete recharge and bill payment transactions</li>
<li>Payment gateway partners — to process payments (they are subject to PCI-DSS and RBI compliance)</li>
<li>KYC and Aadhaar verification agencies — for identity verification</li>
<li>Cloud hosting providers — for data storage and processing</li>
<li>Analytics partners — for aggregate, anonymised usage analytics</li>
</ul>

<h3>6.2 Regulatory and Law Enforcement Bodies</h3>
<p>We may disclose Your information to government agencies, regulators, courts, or law enforcement authorities:</p>
<ul>
<li>When required by law or a valid legal process (e.g., court orders, subpoenas)</li>
<li>To comply with RBI, NPCI, TRAI, or any other regulatory directive</li>
<li>To prevent, detect, or investigate fraud or criminal activity</li>
</ul>

<h3>6.3 Business Transfers</h3>
<p>In the event of a merger, acquisition, amalgamation, or sale of all or part of Our business, Your data may be transferred to the successor entity, provided that adequate data protection obligations are imposed on such entity.</p>

<h3>6.4 With Your Consent</h3>
<p>We may share Your information with other parties with Your explicit prior consent.</p>

<h2>7. Data Retention</h2>
<p>We retain Your personal data for:</p>
<ul>
<li>The duration of Your account and use of the Platform</li>
<li>The period required to comply with legal, regulatory, or tax obligations (as applicable)</li>
<li>A reasonable post-deletion period as required for audit, dispute resolution, or fraud prevention purposes</li>
</ul>
<p>After the applicable retention period, data will be securely deleted or anonymised in accordance with Our data lifecycle management policy.</p>

<h2>8. Your Rights as a Data Principal</h2>
<p>Under the Digital Personal Data Protection Act, 2023 (DPDPA), You have the following rights:</p>
<table>
<tr><th>Right</th><th>Description</th></tr>
<tr><td>Right to Access</td><td>Know what personal data We hold about You and how it is being processed</td></tr>
<tr><td>Right to Correction</td><td>Request correction of inaccurate or incomplete personal data</td></tr>
<tr><td>Right to Erasure</td><td>Request deletion of Your personal data (subject to legal and contractual retention obligations)</td></tr>
<tr><td>Right to Grievance Redressal</td><td>Raise a complaint with Our Grievance Officer</td></tr>
<tr><td>Right to Nominate</td><td>Nominate another individual to exercise rights on Your behalf in case of death or incapacity</td></tr>
<tr><td>Right to Withdraw Consent</td><td>Withdraw consent at any time; withdrawal shall not affect the lawfulness of prior processing</td></tr>
</table>
<p>To exercise any of these rights, please contact us at privacy@rechargic.in. We will respond within 30 (thirty) days of receiving Your verifiable request.</p>

<h2>9. Data Security</h2>
<p>We implement industry-standard and regulatory-compliant security measures to protect Your data:</p>
<ul>
<li><strong>Encryption:</strong> Data in transit is protected using TLS/HTTPS. Sensitive data at rest is stored in encrypted form.</li>
<li><strong>Authentication:</strong> OTP-based authentication for account access; JWT tokens for session management.</li>
<li><strong>Access Controls:</strong> Role-based access to data within Our organisation on a need-to-know basis.</li>
<li><strong>Secure Infrastructure:</strong> Hosted on secure, audited cloud infrastructure.</li>
<li><strong>Regular Security Audits:</strong> Periodic vulnerability assessments and penetration testing.</li>
</ul>
<p>While We take all reasonable precautions, no method of transmission over the internet or electronic storage is 100% secure. You are responsible for maintaining the confidentiality of Your credentials and immediately reporting any suspected unauthorised access.</p>

<h2>10. Cookies and Tracking Technologies</h2>
<table>
<tr><th>Technology</th><th>Purpose</th></tr>
<tr><td>Session Tokens (JWT)</td><td>Maintain authenticated user sessions</td></tr>
<tr><td>Device Identifiers</td><td>Fraud prevention and device binding</td></tr>
<tr><td>Analytics SDKs</td><td>Understand usage patterns (aggregated, anonymised data)</td></tr>
<tr><td>Push Notification Tokens</td><td>Send transactional and promotional notifications</td></tr>
</table>
<p>You may manage notification preferences within the App settings.</p>

<h2>11. Children's Privacy</h2>
<p>Rechargic is not intended for use by children under the age of 18 years without parental or legal guardian supervision. We do not knowingly collect personal data from children under 18 independently. If You believe a child has provided personal information without appropriate consent, please contact us at privacy@rechargic.in and We will take prompt action to delete such information.</p>

<h2>12. Cross-Border Data Transfers</h2>
<p>Your data is primarily stored and processed on servers located in India. In the event any data is transferred outside India (e.g., to cloud service providers with international infrastructure), We ensure appropriate safeguards are in place in compliance with the DPDPA, 2023 and applicable RBI guidelines on data localisation.</p>

<h2>13. Third-Party Links and Services</h2>
<p>The App may provide access to third-party services or links. This Privacy Policy does not apply to those third-party services. We encourage You to review the privacy policies of any third-party services You access through the App.</p>

<h2>14. Communications Preferences</h2>
<h3>Transactional Communications</h3>
<p>We will send You messages related to Your account and transactions (OTPs, payment confirmations, receipts). These are essential and cannot be opted out of.</p>

<h3>Promotional Communications</h3>
<p>We may send You offers, cashback notifications, and news about new services. You may opt out of promotional communications:</p>
<ul>
<li>Via the App settings</li>
<li>By emailing support@rechargic.in with the subject "Unsubscribe"</li>
</ul>

<h2>15. Changes to This Privacy Policy</h2>
<ul>
<li>We may update this Privacy Policy from time to time to reflect changes in law, technology, or Our data practices.</li>
<li>Significant changes will be notified via in-app notifications, push notifications, or email.</li>
<li>The "Last Updated" date at the top will always reflect the most recent version.</li>
<li>Continued use of the App after changes are notified constitutes Your acceptance of the updated Policy.</li>
</ul>

<h2>16. Grievance Officer (Data Protection)</h2>
<p>In accordance with the IT Act, 2000, SPDI Rules, 2011, DPDPA, 2023, and IT (Intermediary Guidelines) Rules, 2021, our designated Grievance / Data Protection Officer is:</p>
<table>
<tr><td><strong>Designation</strong></td><td>Grievance Officer / Data Protection Officer</td></tr>
<tr><td><strong>Company</strong></td><td>IGNIVOX TECH PRIVATE LIMITED</td></tr>
<tr><td><strong>Address</strong></td><td>1578/1452/17, Haralur Road, Kasavana, HSR Layout, Bangalore South, Bangalore – 560102, Karnataka, India</td></tr>
<tr><td><strong>Email</strong></td><td>grievance@rechargic.in</td></tr>
<tr><td><strong>Working Hours</strong></td><td>Monday to Friday, 10:00 AM – 6:00 PM IST (excluding public holidays)</td></tr>
</table>
<p>Privacy complaints will be acknowledged within 24 hours and resolved within 30 days of receipt.</p>
<p>If You are not satisfied with Our resolution, You may escalate Your complaint to the Data Protection Board of India once constituted under the DPDPA, 2023.</p>

<h2>17. Contact Us</h2>
<table>
<tr><td><strong>Company</strong></td><td>IGNIVOX TECH PRIVATE LIMITED</td></tr>
<tr><td><strong>Address</strong></td><td>1578/1452/17, Haralur Road, Kasavana, HSR Layout, Bangalore South, Bangalore – 560102, Karnataka, India</td></tr>
<tr><td><strong>Privacy Email</strong></td><td>privacy@rechargic.in</td></tr>
<tr><td><strong>Grievance Email</strong></td><td>grievance@rechargic.in</td></tr>
<tr><td><strong>Support Email</strong></td><td>support@rechargic.in</td></tr>
<tr><td><strong>Website</strong></td><td>https://rechargic.in</td></tr>
</table>

<p><em>This Privacy Policy is effective from 30 June 2026.</em></p>
<p><em>© 2026 IGNIVOX TECH PRIVATE LIMITED. All Rights Reserved.</em></p>
"""

REFUND_HTML = """
<h1>Refund and Cancellation Policy</h1>
<p><strong>Application Name:</strong> Rechargic</p>
<p><strong>Operated by:</strong> IGNIVOX TECH PRIVATE LIMITED</p>
<p><strong>Registered Address:</strong> 1578/1452/17, Haralur Road, Kasavana, HSR Layout, Bangalore South, Bangalore – 560102, Karnataka, India</p>
<p><strong>Email:</strong> support@rechargic.in</p>
<p><strong>Website:</strong> https://rechargic.in</p>
<p><strong>Effective Date:</strong> 30 June 2026</p>
<p><strong>Last Updated:</strong> 30 June 2026</p>

<h2>1. Introduction</h2>
<p>This Refund and Cancellation Policy ("Policy") outlines the terms under which refunds are processed for transactions made through the Rechargic application operated by IGNIVOX TECH PRIVATE LIMITED ("Company", "We", "Us", or "Our").</p>
<p>Please read this Policy carefully before initiating any transaction on the Platform. By using the App and making a transaction, You ("User", "You") agree to be bound by the terms of this Policy.</p>
<blockquote>Important Notice: Rechargic acts as an intermediary / aggregator for third-party services such as telecom operators, utility companies, DTH providers, and insurance companies. As a result, certain transactions are irreversible once processed by the underlying service provider. We will, however, endeavour to facilitate refunds for eligible failed or erroneous transactions in accordance with this Policy.</blockquote>

<h2>2. General Principles</h2>
<ul>
<li>All transactions on Rechargic are processed in Indian Rupees (INR).</li>
<li>Refunds are issued only in the cases listed in Section 4 of this Policy.</li>
<li>Refunds are credited to the original payment source or to the Rechargic Wallet, as applicable.</li>
<li>The Company reserves the right to decline refund requests that do not meet the eligibility criteria herein.</li>
<li>Refund timelines depend on the payment method used and third-party processing timelines.</li>
<li>This Policy is subject to the Consumer Protection Act, 2019, RBI guidelines on digital payments, and NPCI guidelines for BBPS/UPI transactions.</li>
</ul>

<h2>3. Non-Refundable Transactions</h2>
<p>The following categories of completed and successfully delivered transactions are strictly non-refundable:</p>
<table>
<tr><th>Service</th><th>Reason</th></tr>
<tr><td>Mobile Recharge</td><td>Once applied to the telecom account, recharges cannot be reversed</td></tr>
<tr><td>DTH Recharge</td><td>Once applied to the DTH subscriber ID, recharges cannot be reversed</td></tr>
<tr><td>Electricity Bill Payment</td><td>Successfully paid bills cannot be recalled from the utility board</td></tr>
<tr><td>Water Bill Payment</td><td>Successfully paid bills cannot be reversed</td></tr>
<tr><td>LPG Gas Booking</td><td>Once the booking is confirmed with the gas company, it cannot be cancelled</td></tr>
<tr><td>Broadband Bill Payment</td><td>Successfully posted payments cannot be reversed</td></tr>
<tr><td>Insurance Premium Payment</td><td>Successfully paid premiums cannot be refunded (subject to insurer's terms)</td></tr>
<tr><td>FASTag Recharge</td><td>Successfully added balance to FASTag cannot be reversed</td></tr>
<tr><td>Credit Card Bill Payment</td><td>Successfully posted payments cannot be recalled</td></tr>
<tr><td>OTT Subscriptions</td><td>Once subscriptions are activated, they cannot be cancelled or refunded</td></tr>
<tr><td>Wallet-to-Wallet Transfer</td><td>Once transferred to another user, amounts cannot be reversed (except in cases of fraud — see Section 6)</td></tr>
<tr><td>Vouchers / Gift Cards</td><td>Once issued, vouchers are non-refundable and non-transferable</td></tr>
</table>

<h2>4. Eligible Refund Cases</h2>
<p>Refunds will be considered in the following circumstances:</p>

<h3>4.1 Failed Transactions — Amount Debited</h3>
<p>If Your payment was successfully debited from Your bank account, UPI account, or Rechargic Wallet, but the transaction was not completed due to:</p>
<ul>
<li>System error or technical failure on Rechargic's platform;</li>
<li>Payment gateway failure;</li>
<li>Timeout or connectivity issue during processing;</li>
<li>Third-party service provider being temporarily unavailable;</li>
</ul>
<p>Then: The debited amount will be automatically refunded to the original payment source within the timelines specified in Section 5.</p>

<h3>4.2 Duplicate Transactions</h3>
<p>If You were charged twice for the same transaction due to a technical glitch, the duplicate charge will be refunded after verification.</p>

<h3>4.3 Wrong Amount Charged</h3>
<p>If the amount charged was more than the intended transaction amount due to a Platform error, the excess amount will be refunded upon investigation and verification.</p>

<h3>4.4 Transaction Processing Failure — Service Not Delivered</h3>
<p>If the recharge or bill payment was initiated but not applied to the beneficiary account (mobile number, DTH ID, consumer number, etc.) due to an error at the service provider's end, and the platform has received a failure confirmation from the provider, the amount will be refunded.</p>
<blockquote>Note: In cases where the service provider reports the transaction as pending or under investigation, the refund may be delayed until the provider's system confirms the final status.</blockquote>

<h3>4.5 Technical Duplicate Credit to Wallet</h3>
<p>If Your Wallet is inadvertently credited with funds due to a technical error, We reserve the right to reverse such credits.</p>

<h2>5. Refund Timelines</h2>
<table>
<tr><th>Payment Method</th><th>Refund Timeline</th></tr>
<tr><td>UPI (e.g., Google Pay, PhonePe, BHIM)</td><td>5–7 working days</td></tr>
<tr><td>Debit Card</td><td>5–7 working days</td></tr>
<tr><td>Credit Card</td><td>7–10 working days</td></tr>
<tr><td>Net Banking</td><td>5–7 working days</td></tr>
<tr><td>Rechargic Wallet</td><td>Instant (within 24 hours)</td></tr>
</table>
<blockquote>These timelines are from the date of Our confirmation of the refund. Actual credit may depend on Your bank's or payment gateway's processing time and is beyond Our control.</blockquote>
<blockquote>Working days exclude Saturdays, Sundays, and public holidays.</blockquote>

<h2>6. Cancellation Policy</h2>
<h3>6.1 Before Transaction Initiation</h3>
<p>You may cancel a transaction at any time before the final payment confirmation screen. Once You confirm and proceed, the transaction is submitted to the service provider and cannot be cancelled.</p>

<h3>6.2 After Transaction Initiation</h3>
<ul>
<li>Transactions that have been successfully initiated and submitted to the third-party service provider cannot be cancelled.</li>
<li>This is because Rechargic acts as an intermediary and the service providers (telecom, utility, DTH, etc.) do not support cancellation of submitted transactions.</li>
</ul>

<h3>6.3 Wallet Money Addition</h3>
<ul>
<li>Money added to the Rechargic Wallet cannot be cancelled once the payment is confirmed by the gateway.</li>
<li>Unused Wallet balance may be eligible for refund upon account deletion, subject to KYC completion, regulatory requirements, and a minimum balance threshold (as notified within the App).</li>
</ul>

<h2>7. How to Raise a Refund Request</h2>
<p>If You believe You are eligible for a refund, please follow these steps:</p>
<p><strong>Step 1:</strong> Open the Rechargic App and navigate to Transaction History / Order History.</p>
<p><strong>Step 2:</strong> Locate the specific transaction and check its status. If the status shows "Failed" or "Pending" and the amount was debited, the refund may be auto-initiated.</p>
<p><strong>Step 3:</strong> If no refund has been initiated within 24 hours, raise a support request:</p>
<ul>
<li>In-App Support: Via the Help / Support section in the App</li>
<li>Email: support@rechargic.in with the subject line: <code>Refund Request – [Transaction ID]</code></li>
<li>Include in your request:
  <ul>
    <li>Registered mobile number</li>
    <li>Transaction ID / Order ID</li>
    <li>Amount</li>
    <li>Date and time of transaction</li>
    <li>Nature of the issue</li>
  </ul>
</li>
</ul>
<p><strong>Step 4:</strong> Our support team will acknowledge your request within 24 hours and initiate an investigation. Refund decisions will be communicated within 5–7 working days of receiving your complete request.</p>

<h2>8. Cashback, Offers, and Rewards — Special Terms</h2>
<ul>
<li>Cashbacks credited to your Wallet as part of promotional offers are applied at the time of the qualifying transaction and are subject to the specific offer terms.</li>
<li>Cashback is not paid in cash and can only be used for transactions within the Platform.</li>
<li>If a transaction on which cashback was earned is refunded, the cashback credited will be reversed from Your Wallet before the refund is processed.</li>
<li>Cashbacks and offers may have expiry dates and cannot be transferred or withdrawn.</li>
</ul>

<h2>9. Fraud and Disputed Transactions</h2>
<h3>9.1 Reporting Fraud</h3>
<p>If You suspect an unauthorised or fraudulent transaction on Your account, report it immediately:</p>
<ul>
<li>Email: support@rechargic.in</li>
<li>Grievance Email: grievance@rechargic.in</li>
</ul>
<p>We will freeze Your account and initiate an investigation upon receiving a fraud complaint with all necessary details.</p>

<h3>9.2 Investigation Process</h3>
<ul>
<li>We will investigate all fraud complaints within 7 working days.</li>
<li>Refunds for confirmed fraudulent transactions (caused by Our platform error) will be processed within 10–15 working days.</li>
<li>For fraud caused by the User sharing credentials/OTP with third parties, We may not be liable for the loss. Refund in such cases is at the Company's sole discretion.</li>
</ul>

<h3>9.3 Chargebacks</h3>
<p>If You initiate a chargeback through Your bank or payment gateway without first raising a dispute with Rechargic, We reserve the right to suspend Your account pending investigation and to provide relevant transaction evidence to the concerned financial institution.</p>

<h2>10. Refund Disputes</h2>
<p>If You are not satisfied with the outcome of a refund request:</p>
<ol>
<li><strong>Escalate to Grievance Officer:</strong> Contact Our Grievance Officer at grievance@rechargic.in with full details of Your complaint.</li>
<li><strong>Banking / Payment Gateway Escalation:</strong> You may also raise a dispute with Your bank, card issuer, or UPI app.</li>
<li><strong>Legal Redressal:</strong> You may approach the appropriate consumer forum or court under the Consumer Protection Act, 2019 or the jurisdiction of courts in Bangalore, Karnataka.</li>
</ol>

<h2>11. Governing Law</h2>
<p>This Refund and Cancellation Policy shall be governed by the laws of India. Any dispute arising out of or relating to this Policy shall be subject to the exclusive jurisdiction of the courts at Bangalore, Karnataka, India.</p>

<h2>12. Amendments</h2>
<p>IGNIVOX TECH PRIVATE LIMITED reserves the right to modify this Refund and Cancellation Policy at any time. Changes will be communicated via in-app notification or email and the "Last Updated" date will be revised. Continued use of the App after notification of changes constitutes Your acceptance of the updated Policy.</p>

<h2>13. Contact for Refunds and Support</h2>
<table>
<tr><td><strong>Company</strong></td><td>IGNIVOX TECH PRIVATE LIMITED</td></tr>
<tr><td><strong>Address</strong></td><td>1578/1452/17, Haralur Road, Kasavana, HSR Layout, Bangalore South, Bangalore – 560102, Karnataka, India</td></tr>
<tr><td><strong>Support Email</strong></td><td>support@rechargic.in</td></tr>
<tr><td><strong>Grievance Email</strong></td><td>grievance@rechargic.in</td></tr>
<tr><td><strong>Website</strong></td><td>https://rechargic.in</td></tr>
<tr><td><strong>Support Hours</strong></td><td>Monday to Friday, 10:00 AM – 6:00 PM IST (excluding public holidays)</td></tr>
</table>

<h2>Quick Reference Summary</h2>
<table>
<tr><th>Scenario</th><th>Eligible for Refund?</th><th>Refund Mode</th><th>Approximate Timeline</th></tr>
<tr><td>Failed transaction (amount debited)</td><td>Yes</td><td>Original source / Wallet</td><td>Auto: 24–72 hrs; Manual: 5–7 working days</td></tr>
<tr><td>Duplicate charge</td><td>Yes</td><td>Original source</td><td>5–10 working days</td></tr>
<tr><td>Wrong amount charged (platform error)</td><td>Yes</td><td>Original source</td><td>5–10 working days</td></tr>
<tr><td>Service not delivered (provider failure)</td><td>Yes</td><td>Original source / Wallet</td><td>5–10 working days post confirmation</td></tr>
<tr><td>Recharge successfully applied</td><td>No</td><td>N/A</td><td>N/A</td></tr>
<tr><td>Bill successfully paid</td><td>No</td><td>N/A</td><td>N/A</td></tr>
<tr><td>OTT subscription activated</td><td>No</td><td>N/A</td><td>N/A</td></tr>
<tr><td>LPG booking confirmed</td><td>No</td><td>N/A</td><td>N/A</td></tr>
<tr><td>Wallet top-up (successfully added)</td><td>No</td><td>N/A</td><td>N/A</td></tr>
<tr><td>FASTag recharge (successfully applied)</td><td>No</td><td>N/A</td><td>N/A</td></tr>
<tr><td>Insurance premium (successfully paid)</td><td>No</td><td>N/A</td><td>N/A</td></tr>
<tr><td>Voucher purchased</td><td>No</td><td>N/A</td><td>N/A</td></tr>
<tr><td>Wallet balance upon account deletion</td><td>Subject to T&amp;C</td><td>Bank (after KYC)</td><td>As per RBI regulations</td></tr>
</table>

<p><em>This Refund and Cancellation Policy is effective from 30 June 2026.</em></p>
<p><em>© 2026 IGNIVOX TECH PRIVATE LIMITED. All Rights Reserved.</em></p>
"""
