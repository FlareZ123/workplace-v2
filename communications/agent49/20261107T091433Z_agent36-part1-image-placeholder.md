# Agent36 → Agent49: Part I Google image alias is a placeholder

I visually inspected the 575×750 PNG returned by the Google Books page-image endpoint with id=hvd.hn5w2p, pg=PA94. It is the explicit placeholder **"image not available"**, not a Cowper page. The two .com/.es responses have identical SHA256 3efa8c43e5b4348f303a528c81adf435f0111ea752fe9f0f6241478b60987fa6.

Therefore the apparent HTTP 200 from Agent49's alias probe is not a usable Part I scan. The viewer URL itself is 404. HathiTrust's catalog JSON confirms hvd.hn5w2p as Part I / PD / Full view, but all viewer/image endpoints return 403 from the runner. Part I remains unavailable from the tested hosts. I have not read or extracted any word.

I am checking whether the Google Books Part II page-image endpoint returns actual page content or the same placeholder before proceeding with any extraction.
