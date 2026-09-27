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
DistroWatch slug and always wins over the scraped value. The cache is read
back from the `public` branch on GitHub, because the feeds action force-pushes
that branch and deletes the generated files it does not own.

## Workflow order

`.github/workflows/feeds.yml` runs two jobs back to back:

1. `releases` - checks out `public`, generates the three release files there
   and pushes them.
2. `feeds` (`needs: releases`) - runs the llun/feeds action, which rebuilds
   and force-pushes `public` from scratch, dropping the release files, then
   restores them from the artifact uploaded by the first job.

That order matters: `feeds.opml` points the "Releases" category at the raw
`releases.xml` on the `public` branch, so the feed has to be committed before
the action fetches it, otherwise the category is published empty and only fills
in on a later run.
