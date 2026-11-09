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
| Bahishti Zewar (بہشتی زیور) | 2nd | yes, and it's featured on the home page |
| Muwatta Imam Malik (مؤطا امام مالک) | 7th | yes |
| Tarjamat al-Qur'an | 5th | no (no price) |
| Shama'il al-Tirmidhi | 7th | no (no price) |

Photograph each book's front cover, straight on and filling the frame. A 3:4 shape works best.

## 2. Prices

Every book on the price list has a price. Two curriculum books aren't on the list, so they aren't
in the bookstore:

- **Tarjamat al-Qur'an** (5th Year)
- **Shama'il al-Tirmidhi** (7th Year)

Send prices for these to add them to the bookstore, or confirm they shouldn't be sold.

**Editions all share one price.** Where the bookstore sells several editions of a book, each
edition uses the list's single price. If any edition costs more or less, give its price:

| Book | Price | Editions |
|---|---|---|
| Tasheel al-Nahw | $9 | blue (version 2.2); maroon (Jamiah Islamiyah Abu Bakr) |
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

No book has a Stripe Payment Link yet, so no book page has a Buy button. Each of the 67 postings
needs its own link (one per edition). The steps are in CLAUDE.md under *Selling books*.

## 5. Curriculum text to review

- **Descriptions I wrote.** Each of the 20 books added from the price list has a short description
  I wrote. Please check these: Urdu ka Asan Qaida, Ta'lim al-Islam, Urdu Khushkhati, Tajweed Made
  Easy, Asan Nahw, Ilm al-Sarf (Awwalin and Akhirin), Bahishti Zewar, Tajweed for Beginners,
  al-Fiqh al-Muyassar, Ilm al-Nahw, Zad al-Talibin, Jamal al-Qur'an, Mukhtasar al-Quduri, Ilm
  al-Sigha, Hidayat al-Nahw, Mabadi al-Usul, Khulasat al-Bayan, al-Siraji and Nur al-Idah. I also
  reworded Durus al-Lugha (now the complete course), Sharh al-Aqida al-Tahawiyya and Taysir
  Mustalah al-Hadith.
- **Longer descriptions (optional).** These books have only the short description, so their full
  view repeats it. A longer description of a paragraph or two would fill it out, like the older
  books have. This applies to all 20 new books listed above.
- **Authors (optional).** Where no author is given, the author line is left off. The authors are
  missing for Achhi Baatein, Urdu ka Asan Qaida, Durus al-Lugha, Urdu Khushkhati, Qasas
  al-Nabiyyin, Tasheel al-Nahw, Tasheel al-Sarf, Tajweed Made Easy, Asan Nahw, Riyad al-Salihin,
  Ilm al-Sigha, Hidayat al-Nahw, al-Hidaya, Tarjamat al-Qur'an, Usul al-Shashi, al-Fawa'id
  al-Makkiyya, al-Muqaddima al-Jazariyya, Mu'in al-Fara'id, Nur al-Yaqin, Nafhat al-Arab, Durus
  al-Balagha, Ghazv-i Fikri, the six books of hadith, Sharh Ma'ani al-Athar, Shama'il al-Tirmidhi
  and both Muwattas.
- **Qasas al-Nabiyyin:** which part or parts are studied? The price list just says "قصص النبیین".

## 6. Photographs of books not on the price list

These were photographed but aren't on the price list, so they aren't on the site. Send prices and
years for any that should be added. Those marked *(saved)* are already cut to
`assets/img/books/<name>.jpg`, ready to use:

- Faiz-e-Siddiq (فیض صدیق) *(saved: faiz-e-siddiq)*
- Asan Sarf, parts 1 and 3 (آسان صرف) *(saved: asan-sarf, asan-sarf-part-3)*
- al-Qira'a al-Wadiha, part 1 (القراءة الواضحة) *(saved: al-qiraa-al-wadiha)*
- Tamrin al-Nahw, part 2 (تمرين النحو) *(saved: tamrin-al-nahw)*
- Kitab al-Nahw (كتاب النحو) *(saved: kitab-al-nahw)*
- Ta'lim al-Haq (تعليم الحق) *(saved: talim-al-haq)*
- Tarikh-e-Islam (تاریخ اسلام) *(saved: tarikh-e-islam)*
- Tadrib al-Nahw (تدريب النحو) *(saved: tadrib-al-nahw)*
- Arabi ka Mu'allim, part 4 (عربی کا معلم) *(saved: arabi-ka-muallim)*
- Asan Mantiq / Taysir al-Mantiq (آسان منطق / تیسیر المنطق)
- Ta'lim al-Arabiyya, al-Kitab al-Asasi, Book 2, Part 1
- Matn al-Aqida al-Tahawiyya (the list has the Sharh, which was added)
