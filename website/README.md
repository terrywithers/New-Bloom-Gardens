# New Bloom Gardens website

Three pages, one stylesheet, no build step:

| File | Page |
|---|---|
| `index.html` | Home: homeowners and overview, services, before/after sliders, areas |
| `commercial.html` | Commercial grounds maintenance (content from the commercial brochure) |
| `book.html` + `book.js` | Booking / quote request form |
| `style.css` | All styling. One font (Poppins), brand crimson `#b83555` and green `#628052` |
| `img/` | Photos and logo taken from the brochure and completion reports |

## Before it goes live
1. **Company number.** Replace `[COMPANY NO.]` in the footer of all three pages. The brochure says `04866832` and the completion reports say `16328264`, so check which is right on Companies House.
2. **Facebook link.** In `index.html`, replace `https://www.facebook.com/` with your page's real address.
3. **Photo permission.** The before/after photos come from client completion reports. Check the clients are happy for them to be used. No names or addresses are shown.
4. **Connect the form to your email** (below).

## Getting booking requests by email (free)
At the moment, when someone fills in the form, it gives them a pre-filled WhatsApp message to send you. That works with no setup. To also get every request by email:

1. Sign up free at **formspree.io** with `info@newbloomgardens.co.uk`. The free plan covers 50 submissions a month.
2. Create a form. Formspree gives you a URL like `https://formspree.io/f/abcdwxyz`.
3. In `book.html`, find `data-endpoint=""` and paste the URL between the quotes.

From then on each request arrives in your inbox. If Formspree is ever down, the customer still gets the WhatsApp option, so no lead is lost.

## Hosting
Any static host works. Free options:
- **Netlify** (drag and drop the `website` folder at app.netlify.com/drop), then point `newbloomgardens.co.uk` at it
- **Cloudflare Pages** or **GitHub Pages**, both of which can publish straight from this repository

If your current site is on Wix, Squarespace or GoDaddy, you'd move the domain's DNS to the new host. Do this at a quiet time, and keep the old site until the new one is confirmed working.

## After launch
- Add the site to **Google Search Console** and submit `https://www.newbloomgardens.co.uk/`
- Make sure the website link on your Google Business Profile, Facebook and Instagram goes to `https://www.newbloomgardens.co.uk/`
- Put `https://www.newbloomgardens.co.uk/book.html` as the "Book" link on Google Business Profile and the button on Instagram
