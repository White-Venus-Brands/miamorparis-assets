# Mi Amor Paris — Instagram & store operations playbook

Read this first in every scheduled run. It is the source of truth for how the
Mi Amor Paris marketing automation works. Owner: Tannay.

## Accounts and IDs
- Instagram: @miamorparisofficial — Instagram Business account ID `17841456732306636`
  (reached through the Zapier connector "Instagram for Business").
- Shopify store: `gp14fu-k1.myshopify.com`, public site https://miamorparis.in, INR.
  Read it with Claude's **Shopify connector** (run-analytics-query for sales/sessions,
  graphql_query for orders, products, prices, inventory).

## Which tool does what
- **Posting: Metricool** (brand "MI AMOR PARIS", blogId/brandId 7658526) via
  createScheduledPost with commit-pinned GitHub raw image URLs. Zapier is a backup
  for posting only (task allowance used up until upgraded).
- **Shopify connector:** all store data (sales, orders, traffic, prices, stock, images).
- Instagram stats: Metricool connector (getAnalyticsDataByMetrics, brandId 7658526).
- Keyword comments/DMs (SCENT, PRICE, QUIZ): ManyChat only. Other comments: Tannay in
  the app. Never turn on auto-replies in Metricool (double replies).
- Gmail (whitevenusbrands6@gmail.com) is connected; Meta ads via Adspirer
  (SSMK-Mi Amor Paris account).
- Image hosting: this repo, `White-Venus-Brands/miamorparis-assets`. Instagram pulls
  images from commit-pinned raw URLs:
  `https://raw.githubusercontent.com/White-Venus-Brands/miamorparis-assets/<commit-sha>/<path>`
- Flagship store: O-17, Lajpat Nagar-II, New Delhi – 110024.

## Hard rules
1. **Posting autonomy (from 27 Oct 2026):** Tannay said "you can start posting
   yourself" — create and publish posts without asking first, using his uploaded
   product photos. After every post, send him the live link and log it in post_log.md.
   All other hard rules still apply. Every post must look different: new background
   and props each time (e.g. Diwali: different fireworks, different rangoli), never
   a repeated scene. Carousels 1080x1350; Reels 1080x1920. Real product photos only,
   whole bottle, never cropped or AI-redrawn. Mark AI-generated imagery as AI
   (Metricool instagramData.isAiGenerated) when people/scenes are generated.
2. **Every price in a post, caption, reply or email must match live Shopify** at
   the time it goes out. Check first. Never state a discount you have not verified.
3. **Never link perfumes to puja, prayer or religious rituals** (they are
   alcohol-based). Use day/night, celebrations, parties, gifting instead.
4. Never name competitors or designer brands. No "dupe", no "inspired by".
5. Never invent reviews, numbers, lasting times or skin claims.
6. Never say order volumes or revenue publicly.
7. Links in captions/comments are not clickable — point to "the link in our bio".
8. Hashtags: max 5 per post (Instagram limit).

## Brand voice (short)
Warm, a little romantic, confident; a friend who knows fragrance. English
(light Hinglish only where natural). 1–2 emoji max (✨ 🤍 🌹). Avoid: "elevate",
"indulge", "luxury at affordable prices", "must-have", "game-changer",
"stop scrolling", em dashes. Look: black, champagne gold, ivory, gold "ap" logo.

## Current offer (Diwali 2026)
- 50% off every product **except gift boxes**, online and in store.
- Free sample bottle with the first order of anything.
- Sale end date: not decided yet. Original (pre-sale) prices are in
  `ops/price_backup_before_diwali.csv` for switching back.

## Best-sellers and what the ad data says
- Best-sellers: Moksha, Hold Mi (men); Ombré, Bouquet (women).
- Cheapest WhatsApp chats in past ads: women 18–34; WhatsApp Status and
  Instagram Reels placements; All-India targeting; festive gifting creative.
- Products with cheapest chats: Love Is In The Air, De Rossa Oudh, Hold Mi, Bouquet.

## Festive calendar
Diwali (8 Nov 2026), Bhai Dooj (11 Nov 2026), wedding season (Nov–Feb),
Christmas/New Year, Valentine's, Holi, Rakhi, Mother's Day.

## How a post is made
1. Pick occasion + products. 2. Verify live prices. 3. Product photos: the
sandbox cannot download from cdn.shopify.com, so send Tannay the image links
and he sends the photos back (or he supplies his own creative). 4. Design
1080×1350 slides (black/gold, logo) or use his images. 5. Caption in brand
voice. 6. Get "yes". 7. Upload to this repo, publish via Zapier, verify via the
Graph API, send the permalink.

## What cannot be automated
- DMs (no messaging permission) — ManyChat will handle keyword DMs later.
- Commenting on other accounts' posts (Instagram does not allow it) — draft
  comments for Tannay to post.

## Log
Posts published are listed in `ops/post_log.md`.

## Meta ads autopilot rules (set by Tannay, 26 Oct 2026)
- Ad account: **SSMK-Mi Amor Paris** `1367716178225422` via the Adspirer connector.
- **Hard cap: ₹500/day total** across all active ads. Never exceed it.
- **Without asking:** pause losing ads/ad sets; raise a winner's budget by up to 20%
  (max once every 3 days per ad set), staying under the cap.
- **Needs Tannay's "yes":** new campaigns, new ads/creatives, resuming anything paused,
  any increase above 20%, deleting anything.
- Judge on **cost per WhatsApp chat** (lead) until Purchase events are confirmed
  firing from the store; then switch to cost per purchase / ROAS.
- Don't touch an ad set in its first 3 days (learning phase) unless it spent ₹300+ with 0 results.
- **Cut:** spent ₹300+ with 0 results, or cost per result > 2× the account's 7-day
  average after ₹500+ spend, or frequency > 4 with falling CTR (creative fatigue).
- **Boost:** cost per result ≤ 0.8× the 7-day average for 3 straight days with 3+ results.
- Same content rules as posts (no puja, live prices, no competitor names).
- Three pixels are firing on the site (815729370798417, 1177078454558466,
  1186013056949718): confirm which one the Shopify Facebook & Instagram app uses
  before running sales campaigns.
