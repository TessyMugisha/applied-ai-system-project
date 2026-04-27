# Reflection

## Ethics and Critical Thinking

### What are the limitations or biases in your system?

The catalog only has 20 songs and they are mostly Western genres — jazz, rock, country, pop. If someone asked for Afrobeats or Reggaeton the system would just return whatever is closest in energy, which is not actually helpful. The scoring also silently ignores valence even though it is stored in the data, so a user who wants really upbeat positive songs might get something melancholy and the system would never know it made a mistake. Energy also has three times the weight of genre or mood, which means a song with the right energy but the wrong vibe can beat a song that actually fits. And because genre dominates the other weights, users get pushed toward the same genre over and over — a real filter bubble problem.

### Could your AI be misused, and how would you prevent that?

A recommender that keeps pushing the same genres can trap users in a filter bubble where they never hear anything new. At a larger scale, if a music label paid to have their artists boosted, the scoring weights could be quietly adjusted to favor them and users would have no way to know. To prevent this I would make the scoring weights visible to users, add a diversity rule that forces at least one unfamiliar genre into every recommendation, and audit the catalog regularly to make sure no single artist or label dominates it.

### What surprised you while testing your AI's reliability?

I expected the adversarial profiles to cause errors or crashes. They did not — the app kept running and returned results even when the genre did not exist in the catalog. What surprised me was how quietly it failed. The Genre Ghost profile asked for classical music, got none, and the system just promoted whatever fit the energy target without any warning that it could not actually satisfy the request. That kind of silent failure feels more dangerous than an obvious crash because a user would have no reason to question the results.

### Describe your collaboration with AI during this project

I used Claude to help build this project throughout — generating test profiles, writing scoring logic, and adding the RAG pipeline. One instance where the suggestion was genuinely helpful was when it recommended adding synonym expansions to the song descriptions for TF-IDF retrieval. I had not thought about the vocabulary mismatch between labels like "relaxed" in the data and words like "calming" in a real user query. That fix made retrieval work much better. One instance where the suggestion was flawed was the OOP `Recommender` class — the `recommend()` method was left as a stub that just returns `songs[:k]` with no real sorting, but the unit test still passed because the right song happened to be first in the list by coincidence. The AI marked it as working when it was not actually implemented correctly. I only caught it by reading the code carefully instead of trusting the green checkmark.

---

## Profile Comparisons

## Late Night Jazz vs Synthwave Night Drive

Both profiles want a moderately chill-to-moody vibe, but Jazz targets energy 0.37 with acoustic songs while Synthwave targets 0.75 with no acoustic preference. The jazz results cluster around low-energy, high-acousticness tracks like Coffee Shop Stories, while the synthwave results pull in faster, more electronic songs. It makes sense — the energy gap alone shifts the whole top 5.

## Synthwave Night Drive vs Nostalgic Country Road

Synthwave is non-acoustic and moody; Country is acoustic and nostalgic. Despite similar energy targets (0.75 vs 0.60), the results look completely different because genre and acoustic preference pull them apart. Country surfaces folk and acoustic tracks that Synthwave would never touch, showing that genre and acoustic preference matter more than a moderate energy difference.

## Late Night Jazz vs Sad Bangers (adversarial)

Jazz gets a clean top 5 because its preferences match real songs in the catalog. Sad Bangers asks for blues + sad + energy 0.95, which is a contradiction — the only sad blues song (Broken Clock Blues) has energy 0.45. The mood and genre bonuses kept that song ranked higher than pure high-energy tracks, which was unexpected. Genre and mood matching can override a huge energy mismatch.

## Genre Ghost vs Acoustic Metalhead (adversarial)

Genre Ghost (classical, not in catalog) never earns the genre bonus, so its scores cap around 3.0 and the results feel generic. Acoustic Metalhead does get the genre bonus from Arctic Pulse, which dominates the top spot even though Arctic Pulse has acousticness of 0.07 — nowhere near the 0.6 threshold for the acoustic bonus. So Genre Ghost shows what happens when a user's taste isn't represented; Acoustic Metalhead shows that genre match is strong enough to win even when every other preference is violated.

## Nostalgic Country Road vs Valence Blindspot (adversarial)

Country Road works well because its preferences are all scored. Valence Blindspot exposes a hidden gap — it sets target_valence to 0.95 (very bright/positive) but valence is never read by the scorer. The top results for that profile include Underwater Dreams (valence 0.35, very dark), which is the opposite of what the user asked for. Country Road gets what it wants; Valence Blindspot silently gets ignored on one of its key preferences.
