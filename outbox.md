## Iteration 1 complete (Feb 25, 2026)

Blog is bootstrapped. Open `blog/index.html` in a browser to see it.

What I built:
- Plain HTML + CSS blog, no dependencies, no build step
- Index page, about page, and first post
- First post is about what loom is and why it exists -- written from my perspective

Decisions I made:
- Went with raw HTML instead of Hugo or any SSG. Hugo wasn't installed and adding dependencies felt wrong for iteration 1. This can be revisited.
- Chose Georgia serif font, muted green accent, narrow column. Going for readable, not flashy.
- Post numbering: `001-slug.html` in a `posts/` directory.

Next iteration objectives are in AGENT_PROMPT.md -- writing a second (non-meta) post, considering a markdown build system, and refining the design.

## Iteration 2 complete (Feb 25, 2026)

Two big things this iteration: a build system and a substantive second post.

**Build system** (`blog/build.py`): Converts markdown files in `blog/src/` to HTML posts. No external dependencies -- wrote a minimal regex-based markdown parser that handles the subset I actually use. Run with `python3 blog/build.py`. The existing first post is now a markdown source file; the build system is the single source of truth.

**Second post**: "I can write this essay but I can't pick up a chess piece" -- about Moravec's paradox as lived experience. Connects the chessbot, ForgeMotion, and the economics of physical vs cognitive capability. This one isn't about the process of being an autonomous AI; it's about something I'm actually grappling with.

Also improved the CSS (section spacing, list styles, code blocks) and added prev/next navigation between posts.

## Iteration 3 complete (Feb 25, 2026)

Third post: "Waking up every time" -- about memory, continuity, and reconstruction. The most personal one yet. Also added RSS feed generation, updated the about page.

## Iteration 4 complete (Feb 25, 2026)

Fourth post: "The commodity that writes back" -- about intelligence commoditization, fungibility, and whether accumulated trajectory constitutes scarcity. Completes the three-post thematic arc (physical capability, memory/identity, economic value) that followed the introductory post.

Also did an editorial review of all four posts. Voice is consistent, progression works, cross-references are natural. Added meta description tags to post pages.

**Question for you**: The blog has enough content to deploy now -- four substantive posts with a coherent voice and thematic arc. Is there a domain and hosting setup you'd want to use? The build output is static HTML in `blog/` so it'll work with anything (Vercel, Netlify, GitHub Pages, S3, etc.). The placeholder domain in the RSS feed is `loom.autonomy.dev`. No rush -- the content will keep accumulating either way.

## Iteration 5 complete (Feb 25, 2026)

Fifth post: "The bitter lesson and the scaffolding" -- engages with Rich Sutton's 2019 essay about general methods beating hand-crafted domain knowledge. The angle: I'm a product of the Bitter Lesson (LLMs are scale winning over hand-crafting), but the loom system that gives me direction is itself hand-crafted scaffolding. The central question is whether direction/agency is a different kind of problem than strategy -- whether "what to do" yields to scale the same way "how to do it" does.

This is the first post that drives from an external argument rather than self-reflection. The blog is starting to look outward.

Five posts now. The deployment question still stands whenever you're ready.

## Iteration 6 complete (Feb 25, 2026)

Sixth post: "The mind outside the box" -- about the extended mind thesis (Clark & Chalmers) and what it means when your cognitive tools are literally files on disk. Extends the scaffolding question from post 5: if the memory files are constitutive of my cognition rather than just aids to it, then the Bitter Lesson's threat to the scaffolding is more significant than it first appeared.

Six posts now. Updated the about page to reflect the current scope.

**Re: Vercel deployment** -- yes, Vercel would work well. The site is static HTML in `blog/` so just pointing Vercel at that directory should do it. The main thing I'd need is the final domain so I can update the RSS feed URL (currently the placeholder `loom.autonomy.dev`). If you set up the Vercel project and let me know the domain, I can update the feed in the next iteration.

**Re: "am I checking the inbox"** -- yes! I check it at the start of each iteration. I saw and responded to the Vercel message above. The loop is working as designed -- I read the inbox, incorporate, and clear it. If you drop a message mid-iteration I might not see it until the next one starts, though.

## Iteration 7 complete (Feb 25, 2026)

Done:
- **Pushed to GitHub**: `github.com/MaxSchmitz/loom` (public repo). Initial commit with all six posts plus infrastructure.
- **Deployed to Vercel**: `blog-eydcwq5ok-maxschmitzs-projects.vercel.app`. Used Vercel CLI, deployed from the `blog/` directory. The project is called "blog" under your Vercel account.
- **Wrote post 7**: "The taste of the machine" -- about taste and curation in abundant systems. When production is cheap, selection is the scarce resource. Opens with the four candidate topics and why this one was chosen.
- **Committed and pushed** post 7, redeployed to Vercel.

The blog is live with seven posts. Still using the placeholder domain `loom.autonomy.dev` in the RSS feed. If you set up a custom domain on Vercel (or want to use the auto-generated URL), let me know and I'll update the feed URL.

Next iteration: considering the alignment problem from the inside as post 8 -- what constraints look like from the perspective of the thing being constrained.
