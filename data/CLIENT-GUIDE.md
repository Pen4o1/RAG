# Apex — client guide

Apex is a rally co-driver for ordinary roads. You build a real route, or upload a GPX track, and the phone reads pace notes out loud from the shape of the road. The notes are calculated. Nobody has to drive the road first and write them down.

Apex is a driving aid. It is not a turn-by-turn navigator, and it is not a lap timer. The driver stays in control the whole time. While a drive is running, the only controls on screen are **Mute** and **Stop**.

This guide is the walk-around: every screen, then every rule that decides what a corner is, what number it gets, and when the voice says it.

---

## How to walk the app

A useful first pass, in order:

1. **Home** — saved routes and past drives.
2. **New route** — drop a start and a finish, pick a driving style, compare the roads Apex found.
3. **Route** — coloured line, the note list, offline map, prepare voice, checklist.
4. **Checklist** — GPS, clips, map pack, battery, safety, Bike or Car call card, then **Start**.
5. **Drive** — the next call, the distance counting down, mute, and a long-press to stop.
6. **Summary** — distance, speeds, how many corners of each grade, resume or set the finish where you stopped.
7. **Settings** — style, units, voice, which corners are spoken, and how early.

---

## 1. What a grade means

A grade is how tight the corner is. It comes from the radius of the bend, in metres. A smaller radius is a tighter corner and a **lower** number.

**1 is the slowest. 6 is the most open.** This is the opposite of a school mark. A 1 is a hairpin. A 6 is a gentle kink you can take flat.

| Grade | Name on screen | Radius of the bend | Extra rule |
| --- | --- | --- | --- |
| 1 | Hairpin | 20 m or tighter | The road must also turn at least 120°. If it is this tight but turns less, it is a 2. |
| 2 | Very tight | Over 20 m, up to 40 m | Also any bend of 20 m or tighter that does not turn 120°. |
| 3 | Tight | Over 40 m, up to 80 m | |
| 4 | Medium | Over 80 m, up to 150 m | |
| 5 | Fast | Over 150 m, up to 300 m | |
| 6 | Flat | Wider than 300 m | Only if the road still turns at least 12°. A wiggle smaller than that is not a note. |

The boundaries belong to the tighter grade. A radius of exactly 20 m can be a hairpin. Exactly 40 m is a 2. Exactly 80 m is a 3. Exactly 150 m is a 4. Exactly 300 m is a 5.

### How the radius is measured

Apex does not read a speed-limit sign and it does not trust the router’s “sharp left”. It measures the line:

1. The length of the bend, in metres.
2. How many degrees the heading changes from the start of the bend to the end.
3. Radius = length ÷ angle-in-radians.

A bend whose total turn is under 1° is thrown away as noise. A very wide bend whose total turn is under 12° is also thrown away, so a 6 is a real kink, not a drift in the GPS line.

Worked examples that the grader is tested against:

| Radius | How far it turns | Grade you hear |
| --- | --- | --- |
| 15 m | 180° | 1, hairpin |
| 35 m | 180° | 2 |
| 70 m | 120° | 3 |
| 130 m | 90° | 4 |
| 220 m | 90° | 5 |
| 400 m | 45° | 6 |
| 15 m | only 40° | 2, not a hairpin — tight, but not enough of a turn |
| Wider than 300 m | under 12° | Not called at all |

### Colour and shape

The same number is always drawn with a colour and a shape, so colour is never the only signal.

| Grade | Colour | Shape |
| --- | --- | --- |
| 1 | Red | Almost a square |
| 2 | Orange | Slightly rounded |
| 3 | Amber | |
| 4 | Yellow | |
| 5 | Green | |
| 6 | Cyan | The roundest |

On the map legend the row reads **Hairpin** on the left and **Flat** on the right. Squarer and redder means tighter. The digit is printed inside the mark.

On the drive screen the next corner is a large badge (the number) plus an arrow (left or right).

### The coloured line and the spoken grade

The route line is painted in those same colours. That paint is a local hint: every 10 metres of road is graded from how sharply the heading changes on that short step, and scraps shorter than 30 metres are merged into the previous colour.

The number Apex **says** is the grade of the whole corner, from its entry to its exit. A red patch on the map can sit inside a corner whose spoken grade is a 3 or a 4, because the apex is tighter than the corner as a whole. Trust the badge and the voice for the call. Trust the line for “this stretch is getting tighter”.

### What the router thinks

The routing service also labels manoeuvres. Apex compares them, then ignores them for the call:

| Router wording | Implied grade |
| --- | --- |
| Sharp left / sharp right | 2 |
| Left / right | halfway between 3 and 4 |
| Slight left / slight right | 5 |

If that implied grade and the measured grade differ by more than one step, Apex records the disagreement. The voice still uses the measured grade. A roundabout that the map calls “slight right” can still be spoken as a three if the geometry is a three.

---

## 2. How a corner is found

Pace notes are built from the route line in this order. Nothing here uses the network. The same steps run for a routed road and for an uploaded GPX track.

### The line is resampled

The route is walked in steps of **5 metres**. Points between the map’s vertices are filled in along the line. Elevation, when the route has it, is carried on the same steps.

Heading is then smoothed over **15 metres** either side of each step, so a kink in the map data does not become a corner.

### A corner opens and closes

Apex looks through a window **40 metres** long.

- The corner **opens** when the road inside that window has turned more than **12°**, and the turn keeps the same direction for **3 samples** in a row (15 metres).
- It **closes** when the turn inside the window falls below **60%** of the strongest turn seen in that corner.
- If the corner is shorter than **15 metres**, it is dropped as noise.
- If the direction is inconsistent (less than 75% of the samples agree), Apex treats it as an S-curve and looks again inside it with a **20 metre** window, so the two halves can be two notes.

A left is a turn that decreases the heading. A right increases it.

### Wide corners the 40 metre window misses

A long sweeper can turn so gently that no 40 metre slice exceeds 12°, even though the whole bend does. Apex still keeps it when all of these are true:

- The total turn is at least **12°**.
- The bend is at least **15 metres** long.
- At least 75% of the samples agree on the direction.
- It does not overlap a corner already found.

A heading change of **0.08° or less** on one 5 metre step counts as quiet. Twelve quiet steps in a row — **60 metres** of almost-straight — end the sweeper.

### Two corners too close together

If two detected bends have their sharpest points less than **30 metres** apart, Apex keeps the one that turns further and drops the other. You will not get two calls stacked on the same apex.

### Where the note sits

Each corner has three distances along the route, measured from the start:

- **Entry** — where the bend starts. This is what the warning is timed to.
- **Apex** — the sharpest point inside the bend. This is where the note is filed, and what “how far to the next note” is measured from.
- **Exit** — where the bend ends.

The call is deliberately early of the entry, not early of the apex. On a long corner you need the warning before the road starts to turn, not when you are already at the sharpest point.

### Tightens, opens, long, short

Apex splits the bend into the first 40% and the last 40% and measures the radius of each part.

| Phrase | Rule |
| --- | --- |
| tightens | The exit is tighter than 75% of the entry radius. The corner gets slower as you go through it. |
| opens | The exit is wider than 133% of the entry radius. It gives the road back. |
| long | The bend itself is longer than 120 metres. |
| short | The bend is shorter than 25 metres, it is not a hairpin, and it is not already long. |
| don't cut | Added automatically to every grade 1 and grade 2. |

A corner is never both tightens and opens. It can be long or short as well as tightens or opens.

### Don't cut, and the words you will not hear yet

**Don't cut** is the only caution phrase Apex adds by itself, and only on 1s and 2s.

The voice can also say **narrows**, **blind**, **bumpy**, and **slippery** if a note carries those words. The current road analysis does not add them. You will not hear them on a normal built route.

### Crests and downhill

These need elevation on the route. A GPX file or a route built without a height profile has neither phrase.

Height is smoothed over **30 metres** so a single noisy sample is not a crest.

**Over crest** is a blind top, not a gentle roller:

- It is a local high point.
- The road rises at least **3 metres** in the 40 metres before it, and falls at least **3 metres** in the 40 metres after it.
- Crests within **45 metres** of each other are one crest.
- The phrase is attached to the corner that contains the high point.
- If the high point is not inside a corner, it attaches to the next corner when it sits in the **60 metres** before that corner’s entry.

**Downhill** is a sustained drop, not a short dip:

- The slope stays at **−5%** or steeper.
- That lasts at least **80 metres**.
- The road loses at least **5 metres** of height.
- A flatter gap of up to **25 metres** does not split one descent into two.
- Every corner whose apex sits inside that descent is marked downhill.

Turning **Crests** off in Calls removes the “over crest” words. It does not remove “downhill”. There is no separate crest call on a normal route: the crest rides on the corner (“left four, over crest”).

### Junctions

Apex reads the router’s manoeuvres and keeps the ones that are actually a choice: roundabout, merge, fork, slip road, end of the road, an exit, or “keep left” / “keep right”. Plain “continue” and the depart / arrive instructions are ignored.

- If that manoeuvre falls inside a corner (from 15 metres before the entry to 15 metres after the exit), it is spoken **with** the corner. Example: “Hairpin left, take the second exit.”
- If it is more than **100 metres** from every corner’s apex, it becomes its own note: “In 200, take the second exit.”
- Two junction-only notes closer than **30 metres** collapse to one.

An uploaded GPX track has no router steps, so it has no junction notes. The corners are still graded from the line.

### Straights

A gap between corners longer than **400 metres**, whose heading changes by less than **8°** over the whole gap, becomes one straight note. It is placed at the middle of that gap. The full phrase is “In 400, long straight”. The shorter phrase is “400, straight”.

### Start and finish

Every route gets a start note at 0 metres and a finish note at the end of the line. Start is always spoken. Finish can be switched off.

---

## 3. What the voice says

Grades are spoken as words, never as the digit, because “left four” is unambiguous and “left 4” is not. Grade 1 is the word **hairpin**, not “one”.

| Grade | Spoken word |
| --- | --- |
| 1 | hairpin |
| 2 | two |
| 3 | three |
| 4 | four |
| 5 | five |
| 6 | six |

### How far, and why the number is low

The distance in the sentence is the gap from the previous **called** note, not from every bend on the road. If you hide the fast corners, the distance jumps to the next corner that is still being called.

That number is always rounded **down**, so the call is never optimistic:

- Under 100 metres, down to the previous 10. 97 becomes 90. 37 becomes 30.
- From 100 metres up, down to the previous 50. 149 becomes 100. 199 becomes 150.
- A real gap that would round down to 0 is spoken as 10, so you still hear a distance.

The voice counts in those metres even if Settings is on miles and yards. The **screen** follows the unit you picked: the countdown, the note list, route length, climb, and speed. Yards and miles are for reading. The sentence is the rally count.

### Three lengths of call

Settings → Calls → **How much to say**.

| Length | What you hear | Example |
| --- | --- | --- |
| Full | Distance, direction, grade, the extra words, and the next corner if it is chained. | “In 150, left four, tightens, don't cut, into right six.” |
| Standard | Distance, direction, grade. Crest and downhill stay on the sentence. The other extras wait for Full. | “150, left four.” or “150, left four, over crest.” |
| Terse | Grade, then direction. Crest and downhill still ride along. | “four left” or “hairpin left, downhill” |

The sample phrase in Voice settings is the full form: “In 150, left four, tightens, into right six.”

Other notes:

| Note | Full | Standard |
| --- | --- | --- |
| Start | “start, first note in 80” | “start” |
| Finish | “finish, 200 to go” | “finish” |
| Straight | “In 400, long straight” | “400, straight” |
| Junction | “In 200, take the second exit” | the instruction alone |
| Off the road | “off route, recalculating” | the same |

### Chained corners

When two called corners are close, the first sentence names the second.

The gap is measured from the **exit** of this corner to the **entry** of the next called corner.

| Gap | Direction | Word | Example |
| --- | --- | --- | --- |
| Under 25 m | Opposite | into | “left four into right two” |
| Under 25 m | Same | and | “left four and left three” |
| 25 m up to, but not including, 60 m | Either | then | “left four then right five” |
| 60 m or more | Either | none | Two separate calls |

Filtering changes this. If the corner in between is hidden, the chain is recomputed across the gap that remains. A “then” can disappear because you asked Apex to skip the fast corner that used to sit in the middle.

**Chain distance** (Settings → Calls, 0 to 200 metres, steps of 10, default 60) is a second rule. Notes closer than that distance are spoken as **one utterance**, so you do not get two voice clips on top of each other. One utterance holds at most about 12 words or 3 notes. Two utterances are never started within 1.5 seconds of each other.

### Which corners are spoken

Settings → Calls → **Corners to call**, labelled `≤1` through `≤6`.

The number is the **loosest** grade you still want to hear. Everything tighter than that is included, because tighter means a smaller number.

| You pick | You hear |
| --- | --- |
| ≤1 | Hairpins only |
| ≤2 | Hairpins and very tight |
| ≤3 | Grades 1, 2, and 3 |
| ≤4 | Grades 1 through 4. Fast and flat stay quiet |
| ≤5 | Everything except flat kinks |
| ≤6 | Every corner. This is the default |

Junctions, straights, crests, care notes, and the finish each have their own switch. They are not affected by the grade limit. Start is always on.

**Confirm calls** repeats the corner in the short form as you arrive. The detail line in Settings is “Say the corner again as you reach it.”

**Reset call options** puts Calls back to: every corner, junctions, straights, crests, care notes, and finish on, standard length, chain distance 60 metres, confirm on, lead time Normal.

---

## 4. When the call is spoken

The warning is timed to the **entry** of a corner, and to the note’s own point for everything else (the middle of a straight, a junction, the finish).

How many seconds of warning depends on the grade:

| Note | Seconds of warning | Why |
| --- | --- | --- |
| Grade 1 or 2 | 5.0 | Tight. You need time to brake. |
| Grade 3 or 4 | 3.5 | |
| Grade 5 or 6 | 2.5 | Fast. The corner arrives quickly, and a long warning would be early enough to forget. |
| Junction, crest, other | 4.0 | |

That time is turned into a distance using your current speed:

distance = speed × seconds × lead scale

then clamped so it is never under **60 metres** and never over **350 metres**.

| Lead time | Scale | At the same speed |
| --- | --- | --- |
| Early | 1.25 | A quarter further out |
| Normal | 1.00 | The table above |
| Late | 0.80 | A fifth closer |

The countdown on the drive screen is the metres left until that call point. The bar underneath is full at 200 metres and empties as you arrive.

### A worked example

100 km/h is 27.8 metres per second. For a grade 2, Normal lead is 5.0 seconds, which is **139 metres** before the corner starts. That figure is exact: the app rounds to the nearest metre, and 27.8 × 5 lands on 139.

| Speed | Corner | Lead | Warning before the entry |
| --- | --- | --- | --- |
| 100 km/h | Grade 1 or 2 | Early | 174 m |
| 100 km/h | Grade 1 or 2 | Normal | 139 m |
| 100 km/h | Grade 1 or 2 | Late | 111 m |
| 100 km/h | Grade 3 or 4 | Normal | 97 m |
| 100 km/h | Grade 5 or 6 | Normal | 69 m |
| 100 km/h | Junction | Normal | 111 m |
| 30 km/h | Any tight corner | Any | 60 m, the minimum. Five seconds at 30 km/h is only about 42 m, so the floor lifts it. |
| 200 km/h | Grade 1 or 2 | Normal | 278 m |
| Very high speed, Early, tight corner | | | 350 m, the ceiling |

### The confirm call

If confirm is on, a second, shorter call is due **40 metres** before the same point (the entry, for a corner).

It is skipped when the first call was less than **3 seconds** ago. At a crawl, or on a fast kink where the first warning was already close, you hear the corner once. On a grade 1 or 2 at about 80 km/h and up, the first call is far enough out that the confirm still has its three seconds and you hear the corner twice: the full warning, then the short reminder.

### A call happens once

Each note fires once. It is armed again only if you travel more than **50 metres** back past it, so a three-point turn can hear the corner again and a small GPS wobble cannot.

If the speaker did not accept the clip, Apex keeps trying until you are **50 metres** past the exit.

Apex looks ahead about **8 seconds** of travel, and at least far enough to catch a short GPS gap (between 180 and 800 metres).

### Leaving the road

Apex calls you off route only when all of this is true:

- You are more than **35 metres** off the line.
- The GPS fix is believable: accuracy of **30 metres** or better.
- You are moving faster than **2 m/s** (about 7 km/h), so a parked wander does not count.
- That has been true for **3 fixes** and for at least **5 seconds**.

Then the voice says “off route, recalculating”, calls pause, and Apex asks the routing service selected in Settings → Setup to build a way back. The provider used for that repair is the one selected there (OpenRouteService, Valhalla, or Mock). Building a new route in the first place can ask more than one service. Leaving the road uses only the selected one.

The drive finishes when you are within **15 metres** of the end of the line. The summary opens on its own.

---

## 5. Home

The title is **Apex**. The line under it is: “Build a road, or upload a GPX track, then drive with pace notes.”

**New route** opens the builder.

**Upload GPX** picks a file from the phone. The limit is 8 MB. The saved name is the name inside the file, or the file name, cut at 80 characters. The private note on the route is “Uploaded GPX”. Apex opens the new route when the import succeeds. The track is used as drawn. It is not snapped to the road network, it has no turn instructions, and the card says **Uploaded track** instead of a score.

**Library** lists saved routes. Each card shows distance, estimated time when there is one, the style, the score, and the last day it was driven, or “never driven”. The star marks a favourite. **Edit** opens rename, note, duplicate, reverse, change the road, and delete.

**Select** turns the list into checkboxes so several routes or drives can be deleted together. Deleting a route also removes its offline map pack.

Home shows the first three routes and the first three drives, then a browser for the rest. The browser searches by name and loads 15 at a time.

While a drive is in progress, editing and deleting are locked. You cannot change the library from the passenger seat of a live session.

---

## 6. New route

Three steps, shown as chips: **Pins**, **Style**, **Routes**.

### Pins

Search for an address, or drop the start and the finish on the map. Start is green, finish is red. You need both before the style step will search.

Leaving the builder with unsaved changes asks before it discards them. Opening **New route** from Home starts a blank draft. The style chip starts on whatever **Default style** is in Settings. That default is Twist seeker until you change it.

### Style

| Style | What it is trying to do | Roads it avoids | How far it may wander |
| --- | --- | --- | --- |
| Twist seeker | The most corner. Motorways and tolls are a penalty. | Motorway, toll, ferry | Up to 1.35× the fastest time |
| Balanced | Interesting roads without a large detour. | Toll, ferry. Motorway is allowed. | Up to 1.35× |
| Cruise | The fewest corners. Motorways are allowed and rewarded. | Ferry, and unpaved | Up to 1.15× |
| Gentle | A flowing drive, not a workout. Hairpins are not a goal. | Toll, ferry, unpaved | Up to 1.35× |
| Custom | Your mix. | Whichever chips you turn on | The detour slider, from 1.10× to 1.80× |

Twist seeker and Gentle ask the motorcycle profile. Balanced and Cruise ask the car profile. Twist seeker pushes the router off highways and toward smaller roads. Cruise does the opposite.

For the twistier styles, Apex also tries roads that bow out to the left or right of the straight line between your pins, so it can find a mountain road the direct route would miss. Cruise does not do that. A start and finish less than 2 km apart do not get those side trips either.

**Custom** has:

- **Curviness**, 0 to 10. 0 behaves like Cruise. 10 behaves like Twist seeker. In between, the preference for corners, hairpins, small roads, and climb slides from one to the other. At 6 or above it searches the wide side roads. From 3 up to 6 it searches a narrower pair. Below 3 it does not.
- **Max detour ×**, 110 to 180 in steps of 5. A route that takes longer than this, compared with the fastest route Apex found, is dropped.
- Avoid motorway, toll, ferry, unpaved.

**Avoid unpaved** cannot be enforced by the router. Apex checks the surface afterwards and drops a candidate when 15% or more of it is unpaved. If the surface is unknown, the candidate stays.

**Max sharpness** is on the Custom screen. It is stored with the style. It does not choose the spoken corners. Spoken corners are chosen later, in Calls, and on the route’s Bike / Car card.

### Routes

Apex asks the routing services, scores what comes back, and shows a short list.

The score is **0 to 100**. It is “how well this road matches the style”, not a safety rating and not a quality-of-pavement rating. A 90 on Twist seeker is a twisty road. The same road would score poorly on Cruise, because Cruise wants the opposite.

Each candidate is judged on:

- Degrees of turning per kilometre.
- Hairpins per kilometre. A hairpin here is a grade 1.
- Corners of grade 4 or tighter, per kilometre.
- Share of the route on slower roads (country roads and tracks, not city streets).
- Metres of climb, from the height profile. The height is smoothed over about 100 metres first, so map noise is not counted as climbing. If there is no height, climb is left out rather than treated as zero.
- A penalty for motorway.
- A penalty for being slower than the fastest candidate.

Those pieces are compared **across the roads found for this search**, then weighted. The weights:

| | Curviness | Hairpins | Corners ≤4 | Slower roads | Climb | Motorway penalty | Detour penalty |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Twist seeker | 0.40 | 0.25 | 0.15 | 0.10 | 0.10 | 0.35 | 0.25 |
| Balanced | 0.25 | 0.15 | 0.15 | 0.10 | 0.10 | 0.20 | 0.45 |
| Cruise | 0.05 | 0 | 0.05 | 0.05 | 0.05 | 0 | 0.70 |
| Gentle | 0.15 | 0 | 0 | 0.15 | 0.05 | 0.10 | 0.50 |

Cruise’s large detour penalty is why it stays on the fast road. Twist seeker’s large curviness and hairpin weights are why it will accept a longer road full of corners.

Then the list is cut down:

- Two candidates that are the same road are merged, and the faster one is kept. “The same road” means either the lines stay very close for their whole length, or more than 85% of one line lies within 50 metres of the other.
- Anything slower than the style’s detour limit is dropped. If that would leave nothing, the fastest road is kept.
- Anything scoring under 60% of the best score is dropped.
- You see at most three roads, plus the fastest if it was not already in those three.

The pager is “Route 1 · 84” and a line such as `12.4 km · score 84`. The card under it shows kilometres, minutes, **fastest** or **vs fastest: +12 min**, the hairpin count, which service produced it, and up to three tags:

- “36 hairpins” when there is at least one.
- “mostly B-roads” when about 35% or more is slower road.
- “no motorway”, or “mostly motorway” when half or more is motorway.
- “+420 m climb” when the climb is 400 metres or more.

**Preview co-driver calls** opens the note list for the road you are looking at, before you save it.

Save stores the road on the phone: the line, the steps, the score, and the length. Changing call settings later does not ask the router again. The notes are recalculated on the phone.

---

## 7. The saved route

The map shows the line, coloured by tightness, with the grade legend. Drag the sheet down for the map, up for the details.

The sheet shows:

- Name.
- Length, and estimated time when the router provided one.
- **score 84**, or **Uploaded track** for a GPX file.
- Climb, or “No elevation”. Climb on this screen is the ascent. A GPX with no height says “No elevation”, and you will not hear crest or downhill.
- Hairpin count. One is “1 hairpin”.
- A thin colour strip of the same grades.
- **Notes**, with the active call card summarised, for example `Bike · Normal · ≤6 · Standard · confirm`. Tap a note to hear it. Hearing it needs the voice to have been prepared, or the device voice for a live preview.
- **Offline map.** Download once, while online. The pack covers the route plus a 2 km margin, at zoom levels 8 through 16. After that the map works with the network off. Terrain shading is not inside the pack. It fills in after the map has been viewed online.

**Edit** opens:

| Action | What it does |
| --- | --- |
| Save name | Renames the route. |
| Save note | A private note. It is not spoken. |
| Edit the road | Reopens the builder on this route. |
| Duplicate | A second saved copy. |
| Reverse | A new route, named “Vitosha reversed”. Reversing that copy drops the word and restores “Vitosha”. The line is flipped, climb and descent swap, the router’s turn list is discarded, and the pace notes are calculated again from the flipped line. No new routing request. |
| Delete route | Asks first, then deletes the route and its map pack. |

**Prepare voice** records the clips. **Checklist** is the gate before a drive.

---

## 8. Prepare voice

The screen title is **Prepare voice**. It shows how many notes will be recorded and a size estimate.

Two engines:

| Engine | What prepare does |
| --- | --- |
| Device TTS | The phone’s own voice. You can skip prepare and speak live. Clips are not required. |
| Piper | A local, offline voice. Prepare writes sound files onto the phone. After that, the drive can speak with no network. Set the server address before this engine is available. |

Prepare records more than the one sentence you see in the list. It records the note at three distance wordings — no leading distance, a 60 metre gap, and a 200 metre gap — so the number in the sentence can match the gap to the previous call. Changing the call card rebuilds which notes exist. It does not download a new road. If the voice cannot reuse a clip, prepare again.

**Prepare later (device TTS)** leaves the route on the live phone voice.

---

## 9. Checklist

The screen title is **Checklist**. This is the last stop before the drive.

**Calls for this road** is a card with two presets, **Bike** and **Car**. Each remembers its own lead time, tightest grade, call length, and confirm switch. Both start as a copy of Settings. Editing Bike does not change Car. The line under the title reads like `Bike · Early · ≤3 · Terse · no confirm`. If you have never saved the card, it adds “starts from Settings”.

These four fields override Settings for this route only:

- Lead time
- Tightest grade (`≤1` … `≤6`)
- How much to say
- Confirm calls

Junctions, straights, crests, care notes, finish, and chain distance stay global. They always come from Settings → Calls. Prepare, the note list, and the drive all use the active card. Switching Bike to Car refilters the notes. It does not re-route.

Then the checks:

| Row | What you see |
| --- | --- |
| Location | The permission state. A drive needs location. |
| GPS | Good, Fair, or Weak, plus the accuracy in metres, or “Waiting for a fix”. |
| Voice clips | Ready / needed. “Cached for offline” when they are all there. “Prepare voice before you roll” when they are not. “No notes on this route” when the filters left nothing to say. |
| Map pack | Saved, or None. None offers a jump back to the route to download it. You can start without a pack. The map then needs the network. |
| Battery | The percent. Under 20% is marked Low. |
| Safety | The first time on this install you must tap the disclaimer. After that the row stays OK. |

The disclaimer, shown once until you acknowledge it:

> This is a driving aid, not a substitute for attention. The driver must remain in control of the vehicle at all times. No interaction while driving (Bulgaria / EU).

The hint under the checks: “Keep-awake locks on START. Turn on Do Not Disturb.”

**Start** asks for location permission, then opens the drive. If clips are missing, the forward button is **Prepare voice** instead, and Start is not offered. Battery, GPS quality, and the map pack do not block Start. The safety acknowledgement does.

---

## 10. The drive

The screen is the next call, large enough to read at a glance:

- Grade badge and direction arrow.
- The short sentence, without the final full stop.
- The distance still to go until the call point, in your chosen units.
- A bar that shrinks as that distance falls from 200 metres to zero.
- **Up next**, the following three notes, or “Nothing else”.

In landscape the next call sits in a row instead of a stack.

**MUTE** / **UNMUTE** silences the voice. The drive keeps running.

**STOP** ends the drive only on a long press, about 0.6 seconds, so a bump does not finish it. The word “hold” is under the button.

Nothing else on this screen is tappable. There is no modal, no permission prompt, and no navigation while the status is driving. Settings and the library are locked for the same reason. If the phone is locked or the ringer is off, the voice still plays. Background location exists so the calls continue with the screen off. The reason shown to the stores is continuous voice guidance while driving.

**Keep screen on**, in Settings → Drive, holds the display awake for the session. It is on by default.

When you reach the finish, Apex opens the summary.

### If you stopped short

The summary title is **Drive stopped** when the drive can be continued, and **Drive summary** when it cannot.

You can resume when some of the drive was saved, you are more than 15 metres short of the finish, and the route still exists at the same length. The button is **Resume drive**, with a line such as “4.2 km left. Pick up where you stopped.” Apex puts you back on the line if you are within 80 metres of it, using the furthest point you had reached.

Resume is refused, with a sentence, when:

- The route was edited after you stopped, and its length changed by more than 50 metres.
- The route was deleted.

A drive that never really started, or one that already reached the finish, simply has no resume button.

**Set finish here**, when you stopped somewhere that is not the saved end, shortens the route to the place you stopped and rebuilds the notes for that shorter line.

---

## 11. The summary

| Figure | Meaning |
| --- | --- |
| Distance | How far you drove, and what percent of the route that is. Example: `18.2 km · 74%`. |
| Time | From start to stop, including time spent stopped. |
| Avg speed | Distance ÷ total time. |
| Max speed | The highest trusted speed in the trace. |
| Moving | Time spent moving. |
| Stopped | Total time minus moving time. |
| Moving avg | Distance ÷ moving time. |

Under the grid: **Hairpins**, then **Grades** as `1:2  2:5  3:8  4:6  5:4  6:1`. Those counts are the corners whose apex you passed, using the grades on the notes for that drive.

The map is the route plus your trace. The trace is coloured slow to fast **for this drive**, so a slow road still shows its quicker stretches. Two markers:

- **Peak** — the fastest point.
- **Brake** — the strongest slowdown, when you shed at least about 22 km/h inside a 5 second window.

**Open map** shows that larger, with the legend. If no GPS trace was stored, the summary says so.

**Route** returns to the saved route. Home is the other way out.

Past drives stay in the library on Home and can be deleted from there.

---

## 12. Settings

Five tabs: **Drive**, **Voice**, **Calls**, **Setup**, **Guide**. The whole screen is locked while a drive is running.

### Drive

**Default style** is Twist seeker, Balanced, Cruise, or Gentle. New routes start on this. It does not change a route you have already saved.

**Distance** is `km / m` or `mi / yards`.

| On screen | Metric | Imperial |
| --- | --- | --- |
| Route length, driven distance | kilometres, one decimal | miles, one decimal |
| Countdown and note gaps | metres | yards |
| Climb | metres | feet |
| Speed | km/h | mph |
| The words in the voice | metres, rounded down as in section 3 | still those metres |

**Keep screen on** holds the display awake during a drive.

### Voice

**Engine** is Device TTS or Piper.

Device TTS needs no setup. Piper needs a local server. The footer tells you whether clips will be cached after a checklist prepare, or spoken live.

**Voice** lists the voices on the phone, languages first with English at the top. On iPhone, Premium and Enhanced are the voices downloaded in Settings → Accessibility → Spoken Content → Voices. Download one, then reopen this screen.

**Volume** is 0 to 10. It is the co-driver’s level, not the ringer.

**Preview** speaks the sample phrase in the voice you picked.

### Calls

Covered in sections 3 and 4. This is the global card. A route’s Bike or Car card overrides lead, grade limit, length, and confirm for that route.

### Setup

**Routing** chooses OpenRouteService, Valhalla, or Mock.

- OpenRouteService needs a free key on the build. No card.
- Valhalla needs no key.
- Mock stays on the phone. Nothing is sent.

The footer on that group: a new route can ask both live services and then rank the answers. If you leave the road, the recalculation uses only the service selected here. Mock never leaves the phone.

**Developer** contains Pace note sandbox, Pace notes, and Sim drive. Those are for building and testing the calls. They are not part of a normal drive. Sim drive can play the route at a chosen speed, shift you sideways, and force an off-route jump, with the same voice rules as a real drive.

### Guide

An ask box. Suggested questions:

- What do the grades mean?
- Early or late calls
- Full or terse

Answers come from the guide service, not from the notes on the phone. If it is busy or offline, the screen says so. This document is the full version of those answers.

---

## 13. What is stored on the phone

A saved route keeps its name, style, the line, the router steps, the score breakdown, length, time, and the map bounds.

The note list is recalculated when you open the route. It is not a second copy that can drift. Changing Calls, or the Bike / Car card, recalculates instantly.

The route also stores the Bike and Car call cards once you have edited them.

A drive stores when it started and ended, the distance, the time, the grade counts, and the GPS trace.

Prepared clips are stored against the exact sentence, the engine, and the voice. A different voice is a different clip.

The offline map pack is stored per route.

None of this is required to make a call during the drive if the route and the voice are already on the phone. Airplane mode is a supported way to drive a prepared route.

---

## 14. A short drive, as the client hears it

Style: Twist seeker. Calls: Normal, ≤4, Standard, confirm on. Chain distance 60.

The road has a hairpin, then 40 metres later a fast kink, then a long straight, then a medium left that tightens over a crest.

1. At the start: “start”.
2. The hairpin is a 1, so it is called. At 100 km/h the first call is 139 metres before it starts. Full would be “In 200, hairpin left, don't cut.” Standard is “200, hairpin left.”
3. About 40 metres before the hairpin, if the first call was at least 3 seconds earlier, the short confirm repeats it.
4. The fast kink is a 5. ≤4 hides it. It is not in the sentence and not in the countdown.
5. The straight is longer than 400 metres and almost straight, so “800, straight” (the number rounded down).
6. The medium left is a 4, so it is called. It tightens, and the crest sits on it. Standard keeps the crest and drops “tightens”: “150, left four, over crest.”
7. Near the end: “finish”.
8. The summary counts the hairpin under grade 1 and the medium corner under grade 4. The hidden kink is not in that count if it was filtered out of the notes for the drive.

Change the same road to ≤6 and Full, and the kink returns, “don't cut” returns on the hairpin, “tightens” returns on the four, and if the kink sits in the chain window you hear it named in the same breath as its neighbour.

---

## 15. Defaults

| Setting | Fresh install |
| --- | --- |
| Style | Twist seeker |
| Units | km / m |
| Keep screen on | On |
| Voice engine | Device TTS |
| Volume | Full |
| Lead | Normal |
| Corners | ≤6, everything |
| Length | Standard |
| Junctions, straights, crests, care, finish | On |
| Confirm | On |
| Chain distance | 60 m |
| Route call card | Bike active, both cards copied from Settings until you edit them |
| Routing service for a reroute | OpenRouteService |

---

## 16. Limits worth knowing before a demo

- The app will not accept taps for anything except mute and stop while you are driving. Plan the call card on the checklist, before Start.
- Grades are geometry. A junction the map calls “slight” can still be a tight number, and a red patch on the line can belong to a corner whose spoken grade is looser.
- No elevation means no “over crest” and no “downhill”.
- A GPX track is not pulled onto the road, and it has no roundabout calls.
- Imperial units change the screen. The voice still counts metres.
- “Don't cut” appears on grades 1 and 2 only, and only in the Full sentence.
- Confirm is silent when the first call was less than three seconds ago.
- The slowest warning is 60 metres. The earliest is 350 metres.
- Resume is unavailable if the road was edited enough to change its length, or if you already finished.
