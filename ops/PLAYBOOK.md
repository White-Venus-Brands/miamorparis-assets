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
   whole bottle, never cropped or AI-redrawn. From 28 Oct: STATIC CAROUSELS ONLY (1080x1350). No AI-generated people, no AI video/Reels; Tannay deleted the Diwali film for looking fake. Mark AI-generated imagery as AI
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

## Comment replies (from 28 Oct 2026)
Tannay approved: Claude may reply publicly to comments on @miamorparisofficial posts as the Mi Amor Paris marketing team, aiming to drive sales, without asking each time. Rules: live Shopify prices only; no invented claims (lasting time, notes, skin); complaints/sensitive/spam -> no public reply, flag to Tannay; never link perfumes to puja; point to link in bio / Lajpat Nagar-II store. Send Tannay a summary after each check.
BLOCKER (28 Oct): Zapier task limit reached for the billing period, so the Instagram Graph API route (Zapier 'Instagram for Business' raw request) is unavailable until Zapier is upgraded/renews. Metricool MCP has no comment tools.

## Daily Stories (from 28 Oct 2026)
Tannay: "start doing stories too", then (28 Oct) "2 stories everyday 12 hours apart". Posted via Metricool (instagramData.type STORY, no text, autoPublish true):
- **11:00 IST: This or that** (two scent moods, rules below).
- **23:00 IST: Today's Star** — one product highlighted (perfume, body wash, cream, candle…), name + mood/benefits from the listing + live price and was-price. `make.star()` in ops/stories/make.py, example batch `stars1.py`. Rotate categories; never the same product two nights running.
- **Always compare two different scent MOODS, not product names** (e.g. "FRESH & CITRUSY" vs "FRUITY & FLORAL", "LIGHT & BREEZY" vs "WARM & WOODY") so people choose by feel. Product name + live price appear small under each mood.
- Scent words come only from the Shopify listing's notes/family. Prices checked live before each batch.
- Generator: `ops/stories/make.py` (+ `week1.py` as the example batch). Real bottle cutouts in `assets/cutouts/` (mraqua, missaqua, moksha, liita, derossa). No photo yet for Ombre, Bouquet, Flora 5, Miss Poem, Smuggler, Hold Mi, Marhaba perfumes: ask Tannay; never AI-draw a bottle.
- Vary the pair, the question and the background every day; don't repeat the exact same pair two days running.
- Instagram API can't add polls/quiz/link stickers to Stories; the Story asks people to "Reply 1 or 2" (replies arrive as DMs).
- Weekly scheduled task builds and books the next 7 days every Sunday, logs them in `ops/post_log.md`, and messages Tannay the week's sheet.

## Daily feed post (from 28 Oct 2026)
Tannay: "1 post everyday for upcoming festivals … something new everyday, we have more than 180 products, choose a new set or combination everyday for festive gifting posts."
- One feed post a day (static carousel 1080x1350, ~19:30 IST) themed on the next festival: Diwali (8 Nov), Bhai Dooj (11 Nov), wedding season, Christmas, New Year, Valentine's...
- **Never repeat a product set.** Before building, check `ops/feed_used.md` and pick products/combinations not used yet. Rotate categories: perfumes, body wash, moisturisers, handwash, 1-wick & 3-wick candles (zodiac / chakra / oud / numerology), diffuser oils + stands, incense (30 pcs: Bhakti, Gokul, Guggal, Himalayan Oudh, Moksh, Rajnigandha, Sanatan, Vanya, chakra lines), 8 ml testers, combos.
- Real photos from Drive "All Products Images & Videos" (id 1wp0tAaKCqvVSeLH-emfuZxQwgDADXUYL). Category folders: Perfume 1_8ir-xnEDUvb6Rsk_olpzUx4SFt78NXi (several perfume subfolders are EMPTY), BODY WASH 18JQ7kFDX_PS3N5QzgQN6MfydKcw_mi9E, Moisturizer 1lOlCChtw5yD6fky7RCj6HcTQ3JTc4KVU, Handwash 1JmKgAYAJZMpiKuy20DjOUVUjoXZfmz73, 1 Wick Candles 1ACnwsiA2rRQJ51sblPny2qGiTrjWGZtD (Zodiac 1GsL78DVudpIJVGYA_VpNfXInWg7LrZYP, Chakra 1xDgfX0BTCtK6seKaOGixhm7GEfFD9fCp, Oud 120kFVcepxNBfEC5HFijr2vAbQDxJJgfA, Numerology 1NM3ocaiNN9rTabzUpK3xt4fykZzblypt), 3 Wick Candles 19FyJdCsFmPQ1dyZRqwBWx7JSimfntg7n, Diffuser Oils 1iSoOWGIYIWsODI9SJl9md1_Z5b3Miy8L, Diffuser Stand 10NJZh7yWUGRp-kzvNSn5bvMDhS4zpmJZ, 30 Pcs Incense 1k0s9T_tVXqovQ5MVHsvMQIRX2wIw9ccT, Incense Sticks 1mDqpVjHsL5RGnQeJqPIO8N9ug8PMWych, 8 Ml Testers 1UmKgMelKVhTZ00p9zlC3DIm4tdyZOtP4. Each product folder holds 1.jpg… (1000x1000 lifestyle/studio). Download with the Drive connector (download_file_content → base64).
- Show whole products only (no cropping of the product), live Shopify prices, no puja link for perfumes (candles/incense may appear in festive home settings), max 5 hashtags.

## Automation
- Scheduled task "Mi Amor Paris daily posts and Stories" (trig_01Efxt4X4UpSjwZ9kqXEpcov) runs daily 14:37 IST: books tomorrow's 11:00 This-or-that Story, 23:00 Today's Star Story and 19:30 feed carousel, skipping anything already booked, then messages Tannay. Approved by Tannay 28 Oct.
