# Gearotons wiring diagram review

A buildless, dependency-free review gallery. Serve this directory as static files over HTTP (for example `python3 -m http.server 8765 --directory diagram-review/gallery-src` from the repository root). Open `http://localhost:8765`. Opening `index.html` directly via `file://` will not load the JSON manifest in most browsers.

Populate `candidates.json` with an array (or `{ "candidates": [...] }`). Each candidate needs a stable, unique string `id`, a `title`, and an `image` under `assets/`. All image and thumbnail paths must be relative `assets/...` paths. Do not rename candidate IDs between revisions; prior feedback is associated with IDs. Optional fields:

```json
[
  {
    "id": "direction-01",
    "title": "Candidate title",
    "style": "Style description",
    "description": "Image description and review context.",
    "image": "assets/direction-01.png",
    "thumbnail": "assets/direction-01-thumb.png",
    "width": 4096,
    "height": 3072,
    "revision": "r1",
    "reviewStatus": "Ready for review"
  }
]
```

The checked-in manifest is intentionally empty. No candidate imagery is supplied by this implementation.

Feedback is autosaved to this browser's localStorage under `gearotons.wiring-review.feedback.v1`. This is local storage, not remote sync: feedback does not reach the host or agent automatically. **Export feedback** downloads the complete review as JSON; reviewers can send that file back. **Import JSON** validates every record, then merges by ID, keeping the newest timestamp on a conflict. Unknown IDs are preserved so reviews survive manifest changes. A revision warning appears when feedback refers to an earlier revision. Storage failures are clearly shown and JSON export continues to work. Private browsing, clearing site data, changing hostnames, or changing browsers can remove or isolate local feedback. Export a copy when finished.

Use Compare checkboxes on two candidate cards and select the Compare tab. Each image supports independent zoom/pan. In a focused image stage: `+`/`-` zoom, arrow keys pan (`Shift` for larger steps), `0` fits, and `1` shows native resolution. Dragging pans; `Ctrl`/`⌘` plus scrolling zooms around the cursor. Open PNG provides the original image in another tab. The interface includes labeled rating radios, keyboard controls, reduced-motion handling, and responsive single/two-column views.

Run the pure model tests with `npm test` (Node 18+). Tests cover import validation, hostile keys, lossless comments, merge conflicts and idempotence, candidate asset restrictions, and filters. Browser interaction/layout QA should use real diagram candidates after populating the manifest.
