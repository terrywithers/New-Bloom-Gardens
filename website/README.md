# New Bloom Gardens website

Three pages, one stylesheet, no build step:

| File | Page |
|---|---|
| `index.html` | Home: homeowners and overview, services, before/after sliders, areas |
| `commercial.html` | Commercial grounds maintenance (content from the commercial brochure) |
| `book.html` + `book.js` | Booking / quote request form |
| `style.css` | All styling. One font (Poppins), brand crimson `#b83555` and green `#628052` |
| `img/` | Photos and logo taken from the brochure and completion reports |

## Status
- [x] Company number (16328264) added to every footer
- [x] Facebook link added
- [x] Photo permission confirmed
- [x] Booking form connected to Netlify Forms. Requests are emailed to you once hosted on Netlify (below).

## Why not Google Sites?
Google Sites doesn't let you upload your own pages, fonts or forms. Custom code can only go in small embedded boxes. To get this design, the booking form and one consistent font, the site needs a proper (free) host. **Netlify** is the simplest. Your domain stays the same; only where it points changes.

## Going live on Netlify (free, about 20 minutes)
1. Go to **app.netlify.com** and sign up with GitHub.
2. **Add new site → Import an existing project → GitHub →** choose `New-Bloom-Gardens`. The settings are already in `netlify.toml`, so just click **Deploy**.
3. You get a test address like `newbloom-xyz.netlify.app`. Check it on your phone and send a test booking.
4. **Booking emails:** in Netlify go to **Forms → booking → Form notifications → Add notification → Email** and enter `info@newbloomgardens.co.uk`. The free plan includes 100 submissions a month.
5. **Point your domain at Netlify:** **Domain management → Add a domain →** `newbloomgardens.co.uk`. Netlify shows the DNS records to set.
   - Find where the domain is registered. Google Sites domains are often with **Squarespace Domains** (formerly Google Domains), GoDaddy or 123-reg. Log in there, open DNS settings and **replace** the `www` record (currently pointing at `ghs.googlehosted.com`) with the one Netlify gives you, plus the record for the bare domain.
   - Netlify adds the free HTTPS certificate automatically, usually within an hour.
   - **At 123-reg:** log in → choose `newbloomgardens.co.uk` → **Manage** → **Manage DNS** → **Advanced DNS** tab. Then:

     | Type | Hostname | Destination | Action |
     |---|---|---|---|
     | A | `@` | `75.2.60.5` | Edit the existing `@` A record (or add one). Delete any other `@` A records |
     | CNAME | `www` | `your-site-name.netlify.app` (from step 3) | Edit the existing `www` record that points to `ghs.googlehosted.com` |

     **Don't touch the MX or TXT records.** They run your info@newbloomgardens.co.uk email.
6. Once the new site loads on your domain, **unpublish the old Google Site** (Google Sites → Settings → Custom domains → remove), so Google doesn't index two versions.

Every change pushed to this repository then updates the live site automatically, so when you ask me to change something, it goes live as soon as it's pushed.

## After launch
- Add the site to **Google Search Console** and submit `https://www.newbloomgardens.co.uk/`
- Make sure the website link on your Google Business Profile, Facebook and Instagram goes to `https://www.newbloomgardens.co.uk/`
- Put `https://www.newbloomgardens.co.uk/book.html` as the "Book" link on Google Business Profile and the button on Instagram
