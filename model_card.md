# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Tessy's VibeMatch 1.0

---

## 2. Intended Use  

It suggests songs based on what genre, mood, and energy level a user likes. It assumes the user knows their preferences going in, like "I want jazz, relaxed, low energy." It's just for class, not a real product.

---

## 3. How the Model Works  

It looks at each song and checks how well it fits the user. If the genre matches, it gets 2 points. If the mood matches, 1 point. Then it checks how close the song's energy is to what the user wants and gives up to 1.5 points for that. If the user likes acoustic music and the song is acoustic enough, it gets a small bonus. Add it all up, sort highest to lowest, return the top 5.

I also ran an experiment where I halved the genre weight and doubled the energy weight to see how much genre was controlling the results. It was a lot.

---

## 4. Data  

There are 20 songs in songs.csv. The genres include jazz, lofi, rock, pop, synthwave, country, folk, ambient, metal, blues, kpop, gospel, latin, soul, and electronic. Moods range from chill and happy to aggressive and melancholic. I didn't add or remove any songs. Some moods like sad and aggressive only show up once, which makes it hard for the system to ever match a user who wants those.

---

## 5. Strengths  

It works best when a user's preferences are well represented in the catalog. The jazz profile and the synthwave profile both returned results that made sense right away. The scoring is also easy to read — you can see exactly why a song was picked, which is more than most real apps give you.

---

## 6. Limitations and Bias 

The biggest weakness is the genre filter bubble. Genre gets the highest score weight, so once you set a favorite genre, almost every result comes from that genre — even if a song from a different genre fits your energy and mood way better. Testing a "classical" user made this obvious: classical isn't in the catalog, so the genre bonus never fired and every score was noticeably lower. The system also silently ignores valence even though it's listed as a user preference, and it never penalizes acoustic songs for users who don't want them. In a real app, these gaps would quietly push users into narrower and narrower taste bubbles over time.

---

## 7. Evaluation  

I tested seven profiles total — three normal ones (Late Night Jazz, Synthwave Night Drive, Nostalgic Country Road) and four adversarial ones (Sad Bangers, Genre Ghost, Acoustic Metalhead, Valence Blindspot).

The most surprising result was Sad Bangers. I expected high-energy songs to dominate since the target energy was 0.95, but Broken Clock Blues — a slow blues track at energy 0.45 — still ranked near the top because the genre and mood match outweighed the energy penalty. The fixed bonuses dominate more than I expected.

Genre Ghost was also telling. With no genre match ever firing, all scores were noticeably lower, meaning the system quietly ranks users with niche or missing genres as lower-confidence matches — not because their taste is harder to serve, just because of the math.

The weight-shift experiment (halving genre, doubling energy) made cross-genre songs climb the rankings, which felt more accurate for profiles where energy proximity really drives the vibe.

---

## 8. Future Work  

I'd add valence to the scoring since it's already in the data but does nothing right now. I'd also add a small penalty for songs the user definitely wouldn't want, like high acousticness when they said they don't like acoustic. Some randomness in the results would help too so you're not always getting the exact same 5 songs every time. And the catalog needs way more songs — 20 is too small to feel real.

---

## 9. Personal Reflection  

The biggest learning moment was seeing how much one weight can shut everything else out. Genre being worth 2 points meant the other features barely got a say. I didn't notice until I ran the adversarial profiles and watched it happen — that's when it actually clicked for me.

AI tools helped me move faster, especially for generating test profiles and spotting biases I wouldn't have thought to try. But I still had to check the output myself. A couple of suggestions didn't line up with the actual data in songs.csv, so I had to go back and verify before trusting them.

What surprised me most was how the results felt real even though the algorithm is just adding up a few numbers. When the jazz profile returned Coffee Shop Stories as number one it genuinely felt right. The system has no idea what music is, but it still passes the gut-check most of the time. That's kind of wild.

If I kept going I'd add valence to the score since it's already in the data and doing nothing. I'd also want a much bigger catalog — with only 20 songs the same tracks keep appearing no matter what profile you use and it stops feeling like a real recommender pretty fast.
