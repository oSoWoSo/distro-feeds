# Personal feeds site (FeedsFetcher)
This is an empty repo with feeds source for feeds fetcher to read and pull content and build static feeds site  
Using https://github.com/llun/feeds  
Fork of sample [repository](https://github.com/llunbot/personal-feeds)  

Another sample sites:
- https://feeds.llun.dev/
- https://llun.github.io/feeds/

## Releases page

`scripts/generate_releases.py` builds `releases.html`, `releases.xml` (an Atom
feed consumed as the "Releases" category in `feeds.opml`) and
`releases.cache.json` from DistroWatch. Run it from the repo root:

    python3 scripts/generate_releases.py

Homepages are scraped from each DistroWatch distribution page and cached in
`releases.cache.json`; `homepages.cfg` holds manual overrides keyed by
DistroWatch slug and always wins over the scraped value.
