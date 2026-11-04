# Mi Amor Paris — Instagram & store operations playbook

> **HOLD (Tannay, 4 Nov 2026): STORIES ONLY.** No Reels or feed posts are created, scheduled or un-drafted until Tannay lifts this. Drafts on hold: Office Reel (5 Nov), Bhai Dooj Reel (6 Nov), Flora 5 carousel (5 Nov), Delhi checklist Reel, De Rossa Reel, Marhaba carousel, gift-box post.


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

## Gift boxes (Tannay, 3 Nov)
- Offer wording: "Buy one perfume, get the whole Diwali set" (do NOT say 50% off on gift-box creative). Delhi NCR delivery within 2-3 hours* with "*During office hours".
- Gift Box For Her = Flora 5, Love Is In The Air, Miss Poem, Bouquet. For Him boxes: coming soon (Tannay will send photos).
- Body wash + extrait de parfum + moisturizer gift box, available in 10 scents (all except Ombré and Miss Aqua) ("get the whole routine"). Not listed on Shopify yet: sell via DM / store, prices by DM.

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

## Daily Stories (from 4 Nov 2026, replaces This-or-that and Today's Star)
Tannay 4 Nov: "a new story everyday for diwali, a fact about diwali and why it's celebrated and then how we should gift our loved ones... no more star product and comparisons."
- **Timing (4 Nov, from Metricool audience data: followers most active 17:00-20:00, peak 18:00-19:00; activity falls ~35% by 22:00 and ~60% by 23:00):** Tannay chose (4 Nov): **09:00 IST** and **21:00 IST** every day. A DIFFERENT gift set in every Story until Diwali (fact Story shows 'Today's pick: <set>' with a big box photo). 5-8 Nov pre-booked by ops/stories/diwali_plan_nov5_8.py (Miss Poem, De Rossa, Love Is In The Air, Hold Mi, Flora 5, Smuggler, Marhaba, Moksha). Answer GIFT DMs fast 21:00-22:30.
- **09:00 IST: Diwali fun fact** `fact(n)` in ops/stories/diwali.py. One small TRUE fact (meaning of Deepavali, Amavasya night, five days, many faiths, why we gift, rangoli, Bhai Dooj), then a soft gifting tie-in with a real gift-box photo and "Reply 'GIFT' for prices". Facts live in the FACTS list; use the next number not yet in ops/post_log.md. Add new facts only if you can verify them; keep them respectful and never link perfume to puja.
- **21:00 IST: Diwali gift idea** `gift(n)`: a witty "For the sister who 'borrows' your perfume" style line on the real gift-box photo, set name + scent words from the listing, offer + delivery* + "REPLY 'GIFT' FOR PRICES". Next GIFTS number not yet used.
- `--days N` puts a big "DIWALI IN N DAYS" pill on top (Tannay 4 Nov wording; 1 = DIWALI TOMORROW, 0 = HAPPY DIWALI). Diwali is 8 Nov 2026.
- Facts (Tannay 4 Nov): only CONFIRMED facts that celebrate Diwali (knowledge, records, global recognition). Nothing that could offend any religion: no comparisons between faiths, no claims about rituals. Sources in ops/stories/diwali_sources.md; verify any new fact by web search before using it. No ₹ prices on Stories either.
- After Bhai Dooj (11 Nov): same two-story format for the next occasion (wedding season, Christmas, New Year): a light fact or tradition at 11:00 and a "for the ... who ..." gift idea at 23:00. Extend the lists in diwali.py (or a new module) with real product photos.
- Old generator ops/stories/make.py (This-or-that / Star) is retired.
- Instagram API can't add stickers; replies arrive as DMs (ManyChat keyword GIFT).

## Daily feed post (from 28 Oct 2026)
Tannay: "1 post everyday for upcoming festivals … something new everyday, we have more than 180 products, choose a new set or combination everyday for festive gifting posts."
- One feed post a day (static carousel 1080x1350, ~19:30 IST) themed on the next festival: Diwali (8 Nov), Bhai Dooj (11 Nov), wedding season, Christmas, New Year, Valentine's...
- **Never repeat a product set.** Before building, check `ops/feed_used.md` and pick products/combinations not used yet. Rotate categories: perfumes, body wash, moisturisers, handwash, 1-wick & 3-wick candles (zodiac / chakra / oud / numerology), diffuser oils + stands, incense (30 pcs: Bhakti, Gokul, Guggal, Himalayan Oudh, Moksh, Rajnigandha, Sanatan, Vanya, chakra lines), 8 ml testers, combos.
- Real photos from Drive "All Products Images & Videos" (id 1wp0tAaKCqvVSeLH-emfuZxQwgDADXUYL). Category folders: Perfume 1_8ir-xnEDUvb6Rsk_olpzUx4SFt78NXi (several perfume subfolders are EMPTY), BODY WASH 18JQ7kFDX_PS3N5QzgQN6MfydKcw_mi9E, Moisturizer 1lOlCChtw5yD6fky7RCj6HcTQ3JTc4KVU, Handwash 1JmKgAYAJZMpiKuy20DjOUVUjoXZfmz73, 1 Wick Candles 1ACnwsiA2rRQJ51sblPny2qGiTrjWGZtD (Zodiac 1GsL78DVudpIJVGYA_VpNfXInWg7LrZYP, Chakra 1xDgfX0BTCtK6seKaOGixhm7GEfFD9fCp, Oud 120kFVcepxNBfEC5HFijr2vAbQDxJJgfA, Numerology 1NM3ocaiNN9rTabzUpK3xt4fykZzblypt), 3 Wick Candles 19FyJdCsFmPQ1dyZRqwBWx7JSimfntg7n, Diffuser Oils 1iSoOWGIYIWsODI9SJl9md1_Z5b3Miy8L, Diffuser Stand 10NJZh7yWUGRp-kzvNSn5bvMDhS4zpmJZ, 30 Pcs Incense 1k0s9T_tVXqovQ5MVHsvMQIRX2wIw9ccT, Incense Sticks 1mDqpVjHsL5RGnQeJqPIO8N9ug8PMWych, 8 Ml Testers 1UmKgMelKVhTZ00p9zlC3DIm4tdyZOtP4. Each product folder holds 1.jpg… (1000x1000 lifestyle/studio). Download with the Drive connector (download_file_content → base64).
- **No prices in feed posts (Tannay, 3 Nov, "from now on"):** no ₹ amounts on slides or in captions. The LAST slide always says "DM for prices & Diwali deals" (or the current occasion's deals). Price checks still matter for DM/comment replies.
- **Never use plain white-background product shots on a slide (Tannay, 3 Nov)**, not even inside a frame/panel. Theme the whole post to the scent (e.g. Marhaba = Arabian nights: dark, saffron, rose, oud, brass, pointed-arch frame). Don't call posts "the X edit". Marhaba is positioned as UNISEX. Include every product of the line that has photos (Tannay asked where the Marhaba moisturizer was).
- **Backgrounds (Tannay, 3 Nov):** every product picture gets a nice background that looks REAL, not flat colour panels or obvious graphics. Best method: cut the real product out of its studio shot and stand it in a real photoshoot set (e.g. his Flora 5 8 ml set, see posts/2026-11-04-flora5-ritual/build.py) with contact shadow and matching warm light. His styled photoshoot images are real photos: don't mark them AI.
- Show whole products only (no cropping of the product), live Shopify prices, no puja link for perfumes (candles/incense may appear in festive home settings), max 5 hashtags.

## Automation
- Scheduled task "Mi Amor Paris daily posts and Stories" (trig_01Efxt4X4UpSjwZ9kqXEpcov) runs daily 14:37 IST: books tomorrow's 09:00 fact Story, 21:00 gift-idea Story and 19:30 feed carousel, skipping anything already booked, then messages Tannay. Approved by Tannay 28 Oct.

## Reels (Tannay, 3 Nov): every WEDNESDAY and SATURDAY evening, 20:00 IST
- On top of the daily feed post. Built by Claude from real product photos (no AI people, no AI-drawn products), 1080x1920, 12–25 s, original music/SFX.
- **The hook is everything:** a witty, relatable line or situation in the first second that makes people stay to see "what's happening here" (e.g. "POV: the Diwali party is in 2 hours and you forgot the gift"; "Things that disappear by Bhai Dooj: kaju katli, sone papdi, your bonus. Things that don't…"; "Rate my Diwali gift"). Product + payoff by the end; 3-second view rate was only 22% on the first Reel, so open on motion + text, never a slow logo.
- No ₹ prices (DM for prices), offer wording per the gift-box rules, *During office hours on any delivery promise. Reference builds: posts/2026-11-04-de-rossa-ramp-reel (3D set + real bottle), scratchpad-style gift reel (kinetic text + product flashes).
- Log every Reel in ops/post_log.md and ops/feed_used.md like feed posts.

### Reel hook bank (unused ones first; mark used in post_log)
- USED 4 Nov: "POV: Diwali party in 2 hours. You forgot the gift."
- USED 7 Nov: "POV: Delhi girl ki Diwali checklist" (Tannay: premium, no Sarojini/Chandni Chowk, no forced slang)
- NEXT (Tannay filming): street interviews "Is Diwali aapne khud ke liye kuch liya?" (women buying for themselves). Edit his raw clips: best answer first, Hinglish captions, end card.
- USED 6 Nov: "Diwali card party pe aunty ke sawaal" (Tannay stills). Ideas: "Bonus aaya. Pehla gift? Khud ko.", "Nobody says gents CEO". Women-empowerment tone: everyday moments, funny, never preachy or anti-men. (countdown clock running all video)
- "Things that disappear by Bhai Dooj: kaju katli, sone papdi, your bonus. Things that don't: this scent." (Bhai Dooj, 11 Nov)
- "Rate my Diwali gift /10" then reveal box contents one by one, score climbs each item
- "Guess the scent from 3 notes" mini-quiz, answer revealed at the end (keeps them to the last second)
- "Your zodiac's Diwali gift" fast cuts, one sign per 0.8 s, "pause to find yours"
- "Gifts that say 'I tried' vs gifts that say 'I tried less'" side-by-side
- "Wedding season starter pack for guests who are always late" (post-Diwali)
- "Red flags in a gift: it came with a price tag. Green flags: ..."
Rules: hook text on screen in frame 1, something moving, a running device (clock, score, quiz) that only pays off at the end.
- Pacing (Tannay 3 Nov): hold every on-screen line long enough to read it, about 1 s per short line, before the next beat. Fast cuts are fine for photos, not for text.
- Music: Metricool can attach Instagram library audio to Reels (instagramData.audioConfiguration, numeric audioId; search terms return candidates). The business account only gets the commercially licensed library, not chart hits. Use an upbeat library track at audioVolume 85 / videoVolume 25 so our SFX still land. Facebook gets our own soundtrack.
- Desi tracks found in the IG library (4 Nov): Retro Bollywood (Instrumental) 1452932673133804, Bollywood Night 694594640077937, Royal Wedding Vibes (Adil-Prashant) 638523664186966, Punjab (Instrumental) 637386112678990, Dance Off (Dhruv Goel) 1372960953297547, Maya Maya (Instrumental) 823145229909724. Prefer these for Indian-audience Reels.
- HOLD (4 Nov): Delhi checklist Reel (Sat 7 Nov 20:00) is a DRAFT in Metricool pending Tannay's changes. Do not publish it, do not book another Reel in that slot without asking him.
- Voices (4 Nov): Creative Claw (ElevenLabs v4) is connected. Saved Character "Delhi Aunty" ee07b4cf-6614-43bc-9b07-2c241c867315; young woman = stock Simran 9w21nMuk8CWXIME31V1S. Write Hindi in Devanagari, English words in Latin. Generate dialogue in one call (extras.dialogue, timestamps) and cut shots to voiceSegments; mix with add_audio_to_video (mix, start_offset). The shell cannot download cdn.creativeclaw.co files, so mixing happens in Creative Claw. Credits are limited (about 87 left on 4 Nov).
- Pronunciation (Tannay 4 Nov): Bouquet = "boo-kay" (a bouquet of flowers). Saved in Creative Claw pronunciations (hi: बुके, en: Boo-kay).
- HOLD (4 Nov): Marhaba carousel and De Rossa thrusters Reel are drafts in Metricool on Tannay's instruction. Do not publish them without asking.
- Pronunciation (Tannay 4 Nov): Miss Poem = "Miss Pome" (one syllable, English). Saved in Creative Claw (hi: मिस पोम, en: Miss Pome).
