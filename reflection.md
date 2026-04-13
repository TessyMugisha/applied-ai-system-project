# Reflection: Profile Comparisons

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
