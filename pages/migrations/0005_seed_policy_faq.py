from django.db import migrations


RETURNS_CONTENT = """
<p>We want you to love what you ordered. If something isn't right, here's how returns and refunds work.</p>
<h3>Return window</h3>
<p>You may request a return or exchange within <strong>7 days of delivery</strong>. Items must be unworn, unwashed,
and in their original condition with tags attached. For hygiene reasons, we can't accept returns on earrings or
other pierced accessories unless they arrived faulty.</p>
<h3>How to start a return</h3>
<p>Contact us via WhatsApp or the <a href="/contact/">contact page</a> with your order number and the reason for
the return. We'll confirm whether the item qualifies and arrange collection or drop-off.</p>
<h3>Refunds</h3>
<p>Once we've received and inspected the returned item, we'll process your refund by bank transfer to the account
you paid from, usually within 3–5 business days. You can see the status of any refund on your order's page under
<a href="/account/dashboard/">My Account</a>.</p>
<h3>Damaged or incorrect items</h3>
<p>If an item arrives damaged or isn't what you ordered, let us know within 48 hours of delivery with photos, and
we'll arrange a free replacement or full refund — no return shipping cost to you.</p>
<p class="small text-muted">This policy is a general guide — for anything not covered here, reach out and we'll
sort it out with you directly.</p>
""".strip()

PRIVACY_CONTENT = """
<p>This policy explains what information Swagcitybymercy collects when you shop with us, and how we use it.</p>
<h3>What we collect</h3>
<p>When you create an account, place an order, or contact us, we collect the details you provide — name, email,
phone number, delivery address, and (for bank transfer payments) a screenshot of your payment confirmation. We
also keep a record of your order history.</p>
<h3>How we use it</h3>
<p>We use your information to process and deliver orders, confirm payments, respond to enquiries, and — if you
subscribe — send occasional updates about new arrivals and offers. We do not sell or rent your personal
information to third parties.</p>
<h3>Payment proof screenshots</h3>
<p>Screenshots you upload to confirm a bank transfer are used solely to verify your payment and are only visible
to our team.</p>
<h3>Your choices</h3>
<p>You can update your account details at any time from <a href="/account/dashboard/">My Account</a>, unsubscribe
from marketing emails via the link in any newsletter, or contact us to request that your data be corrected or
deleted, subject to what we're legally required to keep (e.g. order records for tax purposes).</p>
<h3>Contact</h3>
<p>Questions about this policy? Reach us via the <a href="/contact/">contact page</a>.</p>
""".strip()

TERMS_CONTENT = """
<p>These terms and conditions ("Agreement") govern your use of the Swagcitybymercy website and any purchase you
make with us. By placing an order, you agree to them.</p>
<h3>Products and pricing</h3>
<p>All prices are listed in Nigerian Naira (₦) and may change without notice. We take care to describe and price
items accurately, but if a listing error occurs, we'll contact you before processing the order.</p>
<h3>Orders and payment</h3>
<p>Orders are currently paid for by direct bank transfer to the account shown at checkout. An order is confirmed
once we've verified your payment proof — until then it remains pending. We reserve the right to cancel an order
that can't be verified within a reasonable time.</p>
<h3>Shipping</h3>
<p>Delivery estimates shown at checkout are approximate and depend on your selected region. Risk in the goods
passes to you on delivery.</p>
<h3>Returns and refunds</h3>
<p>See our <a href="/returns-policy/">Return &amp; Refund Policy</a> for full details.</p>
<h3>Intellectual property</h3>
<p>All content on this site — including our logo, photography, and text — belongs to Swagcitybymercy and may not
be reproduced without permission.</p>
<h3>Limitation of liability</h3>
<p>We're not liable for indirect or consequential loss arising from use of this site or delayed delivery due to
circumstances outside our control.</p>
<h3>Governing law</h3>
<p>These terms are governed by the laws of the Federal Republic of Nigeria.</p>
<h3>Changes</h3>
<p>We may update these terms from time to time; the current version always applies to new orders.</p>
""".strip()

FAQ_ITEMS = [
    ("How do I place an order?", "Browse the shop, add your size to your bag, and check out. You'll enter your delivery details and see our bank account for payment before confirming."),
    ("What payment methods do you accept?", "We currently accept direct bank transfer only. After checkout, you'll see our account details and can upload a screenshot of your payment for quick confirmation."),
    ("How long does delivery take?", "Lagos deliveries typically take 1-2 working days, other regions in Nigeria 5-7 working days, and international orders vary by destination — exact estimates are shown at checkout for your selected region."),
    ("How do I track my order?", "Use the Track Order page with your order number and the email you checked out with, or check My Account if you have one — both show live status updates."),
    ("Can I return or exchange an item?", "Yes — unworn items with tags attached can be returned within 7 days of delivery. See our Return & Refund Policy for the full details."),
    ("What happens after I upload my payment proof?", "Our team verifies it against the bank account, usually within a few hours, and updates your order status — you'll see the change reflected on your order page."),
    ("Do you ship internationally?", "Yes, international shipping is available — delivery estimates and fees are calculated at checkout based on your address."),
    ("How do I contact customer support?", "Use the Contact page, WhatsApp us directly, or email us — links are in the site footer."),
]


def seed_policies_and_faq(apps, schema_editor):
    PolicyPage = apps.get_model("pages", "PolicyPage")
    FAQItem = apps.get_model("pages", "FAQItem")

    PolicyPage.objects.get_or_create(
        kind="returns", defaults={"title": "Return & Refund Policy", "content": RETURNS_CONTENT},
    )
    PolicyPage.objects.get_or_create(
        kind="privacy", defaults={"title": "Privacy Policy", "content": PRIVACY_CONTENT},
    )
    PolicyPage.objects.get_or_create(
        kind="terms", defaults={"title": "Terms & Conditions", "content": TERMS_CONTENT},
    )

    if not FAQItem.objects.exists():
        for i, (question, answer) in enumerate(FAQ_ITEMS):
            FAQItem.objects.create(question=question, answer=answer, order=i)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0004_faqitem_policypage"),
    ]

    operations = [
        migrations.RunPython(seed_policies_and_faq, noop_reverse),
    ]
