# Mi Amor Paris — Instagram & store operations playbook

Read this first in every scheduled run. It is the source of truth for how the
Mi Amor Paris marketing automation works. Owner: Tannay.

## Accounts and IDs
- Instagram: @miamorparisofficial — Instagram Business account ID `17841456732306636`
  (reached through the Zapier connector "Instagram for Business").
- Shopify store: `gp14fu-k1.myshopify.com`, public site https://miamorparis.in, INR
  (Zapier connector "Shopify").
- Image hosting: this repo, `White-Venus-Brands/miamorparis-assets`. Instagram pulls
  images from commit-pinned raw URLs:
  `https://raw.githubusercontent.com/White-Venus-Brands/miamorparis-assets/<commit-sha>/<path>`
- Flagship store: O-17, Lajpat Nagar-II, New Delhi – 110024.

## Hard rules
1. **Never publish an Instagram post without Tannay's explicit "yes"** in the chat,
   unless a scheduled task says he already approved that exact post.
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
