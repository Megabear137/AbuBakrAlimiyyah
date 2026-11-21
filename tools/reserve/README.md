# Book reservations: the Google side

The site is static. When a reader presses **Reserve** in the cart, the page sends the reservation to
a Google Apps Script web app (`Code.gs`) that runs in a Google account. The script:

- records the reservation in a Google Sheet (the ledger), one row per book;
- emails the reader a receipt;
- emails the bookstore a copy.

Nothing is paid online. The reader pays and collects at the masjid, and the bookstore marks the row
*Collected*.

For now the script runs in a personal Google account. Moving it to the masjid's account later is
covered under *Moving it to another account* below.

## Setting it up (once, about ten minutes)

1. Sign in to the Google account that should own the reservations. Create a new Google Sheet and
   name it *Bookstore reservations*.
2. In the sheet, open **Extensions → Apps Script**. Delete what's in `Code.gs` and paste in this
   folder's `Code.gs`. Click **Save**.
3. Open **Project Settings** (the gear icon) and set the **Time zone** to the masjid's. Do the same in
   the sheet under **File → Settings**. Dates in the emails and the sheet follow these settings.
4. Back in the editor, pick **setup** in the function list at the top and click **Run**. Google asks
   for permission to use the sheet, send email as you and fetch web pages. Because the script is
   your own, Google calls it *unverified*: choose **Advanced → Go to … (unsafe)** and **Allow**.
   When it finishes, the sheet has two tabs: *Reservations* and *Settings*.
5. Click **Deploy → New deployment**. For the type (the gear icon) choose **Web app**, and set:
   - *Execute as*: **Me**
   - *Who has access*: **Anyone**

   Click **Deploy** and copy the **Web app URL**. It ends in `/exec`.
6. Put that URL in `content/bookstore.json` as `"reserveTo"`, or paste it into the bookstore
   editor's *Reservations address* box (`tools/admin_server.py`). Each priced book page now shows
   **Add to cart**.
7. Test it: add a book, reserve it with your own email, and check that the sheet has the row and
   that both emails arrived.

## Once the site is public

On the **Settings** tab, set `site` to the site's address, ending in `/` (for example
`https://example.org/`). From then on the script:

- checks every book, print and price against the live `content/bookstore.json`, so a tampered
  request can't change a price, and refuses a print marked sold out;
- adds the logo, the collection details (`pickup`, `hold`, `payWith`) and the masjid's contacts to
  the receipt.

While `site` is empty, the script trusts the titles and prices the page sends. That is fine for
testing, but don't leave it empty on the live site.

The other settings:

| Setting | What it does |
|---|---|
| `notify` | Where the bookstore's copy goes, and where readers' replies go. Empty: the account that runs the script. |
| `sender` | The name the emails come from. |
| `perDay` | The most reservations one email address can make in 24 hours (3). |
| `maxCopies` | The most copies of one print in one reservation (5, matching the cart). |

## Using the ledger

Each reservation adds one row per book, sharing a reference (R-1001, R-1002, …). The script fills
every column up to **Status**. After that the row belongs to the bookstore:

- set **Status** to *Collected* or *Cancelled*;
- put the date in **Collected**;
- write anything else in **Note**.

The sheet holds readers' names and email addresses, so share it only with the people who run the
bookstore.

To cancel a reservation, set its rows to *Cancelled* and reply to the reader. The copy email's
Reply-To is the reader's address.

## Changing the script

Paste the new `Code.gs` into the editor and save. Then open **Deploy → Manage deployments**, click
the pencil, choose **Version: New version** and click **Deploy**. The URL stays the same, so the
site needs no change. Saving alone does **not** update the live web app.

## Limits

A personal Google account can send about **100 emails a day**; Google Workspace allows 1,500. Each
reservation sends two emails, so that's about 50 reservations a day. When the quota runs out, the
script turns readers away with a message rather than taking reservations it can't confirm.

## Moving it to another account

Sign in to the new account. Either make a copy of the sheet (**File → Make a copy** also copies the
script), or set it up afresh with the steps above. Run **setup**, deploy it as a web app and put the
new URL in `reserveTo`. If you copied the sheet, the reference numbering carries on from the
script's own property `nextRef` (**Project Settings → Script properties**); set it to the old value
if the copy didn't keep it.
