# What's missing: curriculum and bookstore

As of 24 October 2026. The books, years and prices come from *Madresa Book Price List 2024.xlsx*
(headed 2026/27), and the photographs from *Bookstore.zip*.

## 1. Photographs

*bookstore_2.zip* (9 November 2026) added Jami' al-Tirmidhi, Nafhat al-Arab, al-Siraji, Qasas
al-Nabiyyin, Asan Nahw (part 1 only), Ilm al-Sarf Awwalin, Urdu Khushkhati and Tasheel al-Sarf.
These books still have no photograph, so the site draws a plain binding in their place:

| Book | Year | In the bookstore? |
|---|---|---|
| Tajweed Made Easy | 1st | yes |
| Muwatta Imam Malik (مؤطا امام مالک) | 7th | yes |

Photograph each book's front cover, straight on and filling the frame. A 3:4 shape works best.

## 2. Prices

Every book on the price list has a price. Tarjamat al-Qur'an (4th and 5th Years) and Shama'il al-Tirmidhi
(7th Year) are taught but have no book of their own, so they aren't sold. The photographed books
that aren't on the list are in the bookstore priced TODO (section 6).

**Editions all share one price.** Where the bookstore sells several editions of a book, each
edition uses the list's single price. If any edition costs more or less, give its price:

| Book | Price | Editions |
|---|---|---|
| Tasheel al-Nahw | $9 | blue (version 2.2); maroon (Jāmiʿah Islāmiyah Abū Bakr) |
| Jamal al-Qur'an | $3 | Qira'at Academy; Zinat al-Furqan notes (Maktaba Rahmaniyya) |
| Durus al-Balagha | $7 | blue and white; blue and cream; leather-look |
| Usul al-Shashi | $10 | light blue; wood-grain; brown leather-look; lilac |
| al-Fawz al-Kabir | $5 | paperback; hardcover |
| Tafsir al-Jalalayn | $35 | dark leather-look; grey |
| Mishkat al-Masabih | $30 | black and gold (Ashrafi Book Depot); navy (al-Bushra); brown (al-Bushra) |
| Sahih al-Bukhari | $60 | brown; green |
| Sahih Muslim | $50 | green; brown; black |
| Sunan Abi Dawud | $40 | red and gold; green; grey |
| Sunan Ibn Majah | $35 | blue; pink |
| Sharh Ma'ani al-Athar | $25 | black (al-Bushra); black and gold (Ashrafi Book Depot) |

**Is the price for the whole set?** Several of these books come in more than one volume (Bukhari,
Muslim, Mishkat, Hidaya, Jalalayn, Durus al-Lugha...). Please confirm whether each price is for the
full set or for one volume.

## 3. Bookstore text

- **The bookstore page's intro line** (`lede`) is still a placeholder: what the bookstore stocks,
  and where and when books can be bought.
- **The pickup paragraph** (`pickup`) on every book's page is still a placeholder: where and when
  to collect a book, and that the emailed receipt must be shown.
- **Edition labels** mostly describe the cover colour, because that's what the photos show.
  Publisher names would be more useful where you know them.

## 4. Online payment

No book has a Stripe Payment Link yet, so no book page has a Buy button. Each of the 79 postings
needs its own link (one per edition). The steps are in CLAUDE.md under *Selling books*.

## 5. Curriculum text to review

- **Descriptions I wrote.** Each of the 18 books added from the price list has a short description
  I wrote. Please check these: Urdu ka Asan Qaida, Ta'lim al-Islam, Urdu Khushkhati, Tajweed Made
  Easy, Asan Nahw, Ilm al-Sarf (Awwalin and Akhirin), Tajweed for Beginners,
  al-Fiqh al-Muyassar, Ilm al-Nahw, Zad al-Talibin, Jamal al-Qur'an, Mukhtasar al-Quduri, Ilm
  al-Sigha, Hidayat al-Nahw, Mabadi al-Usul, al-Siraji and Nur al-Idah. I also
  reworded Durus al-Lugha (now the complete course), Sharh al-Aqida al-Tahawiyya and Taysir
  Mustalah al-Hadith.
- **Longer descriptions (optional).** These books have only the short description, so their full
  view repeats it. A longer description of a paragraph or two would fill it out, like the older
  books have. This applies to all 18 new books listed above.
- **Authors (please check).** Authors were added to the curriculum and the bookstore on
  22 November 2026, most read off the covers of the masjid's photographs, the rest the classical
  authors. Where no author is given, the author line is left off. Still without one: Tasheel
  al-Sarf (the cover names only the Jāmiʿah), Urdu ka Asan Qaida and Urdu Khushkhati (publishers
  only), Tajweed Made Easy (no photograph; which book is it?), Ta'lim al-Haq (no author on the
  cover), Hidayat al-Nahw (its authorship is disputed) and Tarjamat al-Qur'an. Ghazv-i Fikri's
  photograph is of Maulana Muhammad Ismail Rehan's *Nazariyati Jang ke Usul* (Usul al-Ghazw
  al-Fikri), and that is the author given: is that the book taught?
- **Qasas al-Nabiyyin:** which part or parts are studied? The price list just says "قصص النبیین".

## 6. Photographed books not on the price list

These were photographed but aren't on the price list. They're in the bookstore with the price TODO
and no year, so they show only under *All years*. For each, send its price and the years it's taught
in, or say it shouldn't be sold:

- Asan Sarf, part 1 (آسان صرف)
- Asan Sarf, part 3
- al-Qira'a al-Wadiha, part 1 (القراءة الواضحة)
- Tamrin al-Nahw, part 2 (تمرين النحو)
- Kitab al-Nahw (كتاب النحو)
- Tadrib al-Nahw (تدريب النحو)
- Arabi ka Mu'allim, part 4 (عربی کا معلم)
- Ta'lim al-Arabiyya, al-Kitab al-Asasi, Book 2, Part 1 (تعليم العربية)
- Asan Mantiq / Taysir al-Mantiq (آسان منطق / تیسیر المنطق)
- Matn al-Aqida al-Tahawiyya (متن العقيدة الطحاوية); the Sharh is already sold
- Ta'lim al-Haq (تعليم الحق)
- Tarikh-e-Islam (تاریخ اسلام)
- Faiz-e-Siddiq (فیض صدیق)

Descriptions are wanted for Kitab al-Nahw, Tadrib al-Nahw, Asan Mantiq, Ta'lim al-Haq,
Tarikh-e-Islam and Faiz-e-Siddiq (they read "TODO: description."). The others have a short one I
wrote; please check them.
