globals [
  actor-names
  modality-names
  base-power          ;; 5 modalities, each a list of 4 actor shares summing to 1
  diffusion-rates     ;; one rate per modality
  legitimacy          ;; one per actor, Table 5
  shock-list          ;; Table 7, as (modality favoured disfavoured)
  checks-against      ;; running count of checks received, per actor
]

breed [markers marker]   ;; one per patch: the icon of whoever is dominant there

patches-own [
  power               ;; 5 lists of 4; every inner list sums to 1
  new-power           ;; scratch, so diffusion updates synchronously
]

;; Actor indices    0 People   1 State   2 Enterprises   3 AI
;; Modality indices 0 Economic 1 Epistemic 2 Narrative 3 Authoritative 4 Physical
;;
;; Icons: People a figure, State a gavel, Enterprises a dollar sign, AI a
;; robot. The patch behind each icon is a tint of that actor's colour, darker
;; the more of the modality it holds.

;; ===================================================================== setup

to setup
  clear-all
  set actor-names ["People" "State" "Enterprises" "AI"]
  set modality-names ["Economic" "Epistemic" "Narrative" "Authoritative" "Physical"]

  ;; Table 4, read as numbers. Each row is one modality.
  set base-power (list
    [0.20 0.25 0.50 0.05]
    [0.20 0.25 0.40 0.15]
    [0.25 0.25 0.35 0.15]
    [0.10 0.60 0.27 0.03]
    [0.20 0.55 0.23 0.02])

  set legitimacy [0.65 0.70 0.55 0.35]

  ;; How far each modality reaches past the locality holding it, per tick.
  ;; Information travels, jurisdiction does not.
  ifelse uniform-diffusion?
    [ set diffusion-rates [0.17 0.17 0.17 0.17 0.17] ]
    [ set diffusion-rates [0.15 0.30 0.30 0.05 0.03] ]

  set shock-list (list
    (list 0 2 0)
    (list 1 3 1)
    (list 2 3 0)
    (list 3 1 0)
    (list 4 1 2))

  set checks-against [0 0 0 0]

  ask patches [
    setup-patch
    sprout-markers 1 [
      set size 0.8
      set shape "person"
      set color black
    ]
  ]
  recolour
  reset-ticks
  draw-quadrants
end

to setup-patch
  ifelse heterogeneity > 0
    [ set power map [ row -> normalise (map [ v -> v * (exp random-normal 0 heterogeneity) ] row) ] base-power ]
    [ set power base-power ]
  set new-power power
end

to-report normalise [ row ]
  let s sum row
  ifelse s > 0
    [ report map [ v -> v / s ] row ]
    [ report row ]
end

;; ====================================================================== main

to go
  local-actions
  diffuse-power
  maybe-shock
  recolour
  tick
  if ticks >= max-ticks [ stop ]
end

to local-actions
  ask patches [
    resolve decide-people
    resolve decide-state
    resolve decide-enterprises
    resolve decide-ai
  ]
end

;; ================================================================ accessors

to-report share [ m a ]
  report item a (item m power)
end

to set-share [ m a v ]
  set power replace-item m power (replace-item a (item m power) v)
end

to transfer [ m frm dst amt ]
  let avail share m frm
  let x amt
  if x > avail [ set x avail ]
  if x < 0 [ set x 0 ]
  set-share m frm (avail - x)
  set-share m dst ((share m dst) + x)
end

;; ================================================================= policies

;; Each candidate is (target-actor modality). Returns (target modality) for
;; the most concentrated one above the threshold, or an empty list.
to-report hottest [ cands ]
  let best-target -1
  let best-mod -1
  let best-share concentration-threshold
  foreach cands [ c ->
    let t item 0 c
    let m item 1 c
    if share m t > best-share [
      set best-target t
      set best-mod m
      set best-share share m t
    ]
  ]
  ifelse best-target = -1
    [ report [] ]
    [ report (list best-target best-mod) ]
end

;; An action is (kind modality target actor).

to-report decide-people
  let hit hottest (list (list 2 0) (list 1 3) (list 3 2))
  if not empty? hit [ report (list "CHECK" (item 1 hit) (item 0 hit) 0) ]
  ifelse random-float 1 < 0.3
    [ report (list "ENHANCE" 2 -1 0) ]
    [ report (list "ABSTAIN" -1 -1 0) ]
end

to-report decide-state
  let hit hottest (list (list 2 0) (list 3 1))
  if not empty? hit [ report (list "CHECK" (item 1 hit) (item 0 hit) 1) ]
  ifelse random-float 1 < 0.3
    [ report (list "ENHANCE" 3 -1 1) ]
    [ report (list "ABSTAIN" -1 -1 1) ]
end

to-report decide-enterprises
  let hit hottest (list (list 3 0))
  if not empty? hit [ report (list "CHECK" (item 1 hit) (item 0 hit) 2) ]
  ifelse random-float 1 < 0.7
    [ report (list "ENHANCE" 0 -1 2) ]
    [ report (list "ENHANCE" 1 -1 2) ]
end

to-report decide-ai
  if share 1 3 > concentration-threshold [
    let hit hottest (list (list 2 0))
    if not empty? hit [ report (list "CHECK" (item 1 hit) (item 0 hit) 3) ]
  ]
  ifelse random-float 1 < 0.5
    [ report (list "ENHANCE" 1 -1 3) ]
    [ report (list "ENHANCE" 2 -1 3) ]
end

;; ================================================================== resolve

to resolve [ act ]
  let kind item 0 act
  let m item 1 act
  let tgt item 2 act
  let mover item 3 act

  if kind = "ABSTAIN" [ stop ]

  ifelse kind = "ENHANCE" [
    ;; One ENHANCE is worth one CHECK against an average opponent, so the two
    ;; action types are comparable. Three donors with four actors.
    let scale 1 / 3
    foreach [0 1 2 3] [ d ->
      if d != mover [ transfer m d mover (enhance-magnitude * scale * share m d) ]
    ]
  ] [
    let cs (share m mover) * (item mover legitimacy)
    let ts (share m tgt) * (item tgt legitimacy)
    let den cs + ts
    let p 0.5
    if den > 0 [ set p cs / den ]
    set checks-against replace-item tgt checks-against ((item tgt checks-against) + 1)
    if random-float 1 < p [
      transfer m tgt mover ((check-ratio * enhance-magnitude) * share m tgt)
    ]
  ]
end

;; ================================================================ diffusion

to diffuse-power
  if diffusion-scale <= 0 [ stop ]
  ask patches [
    let result power
    foreach range 5 [ m ->
      let rate diffusion-scale * item m diffusion-rates
      if rate > 0 [
        let row item m power
        let blended n-values 4 [ a ->
          (1 - rate) * (item a row) + rate * (mean [ item a (item m power) ] of neighbors4)
        ]
        set result replace-item m result blended
      ]
    ]
    set new-power result
  ]
  ask patches [ set power new-power ]
end

;; ==================================================================== shock

to maybe-shock
  if random-float 1 < shock-probability [
    let s one-of shock-list
    let m item 0 s
    let up item 1 s
    let down item 2 s
    ask one-of patches [
      transfer m down up (shock-magnitude * share m down)
    ]
  ]
end

;; ================================================================== display

to recolour
  let m position display-modality modality-names
  ask patches [
    let row item m power
    let top 0
    let best item 0 row
    foreach range 4 [ a ->
      if item a row > best [
        set best item a row
        set top a
      ]
    ]
    ;; A pale tint of the dominant actor's colour, darker the stronger its
    ;; hold, so the black icon on top stays readable.
    set pcolor scale-color (actor-colour top) best 2.4 0.4
    ask markers-here [
      set shape actor-shape top
      set size 0.45 + 0.6 * best
    ]
  ]
end

to-report actor-colour [ a ]
  report item a (list blue orange green violet)
end

to-report actor-shape [ a ]
  report item a ["person" "gavel" "dollar" "robot"]
end

;; ================================================================== metrics

;; 1.0 means this modality looks the same in every locality; lower means it
;; is regionally lumpy. This is the model's central prediction: the fast
;; modalities should flatten, the jurisdiction-bound ones should not.
to-report spread-of [ m ]
  let total 0
  let counted 0
  foreach range 4 [ a ->
    let xs ([ item a (item m power) ] of patches)
    let mu mean xs
    if mu > 0.000001 [
      let v 1 - (standard-deviation xs) / mu
      if v < 0 [ set v 0 ]
      set total total + v
      set counted counted + 1
    ]
  ]
  ifelse counted > 0
    [ report total / counted ]
    [ report 1 ]
end

to-report grid-mean [ m a ]
  report mean [ item a (item m power) ] of patches
end

to-report mean-share [ a ]
  let total 0
  foreach range 5 [ m ->
    set total total + (grid-mean m a)
  ]
  report total / 5
end

to-report local-hhi
  report mean [ mean (map [ row -> sum (map [ v -> v * v ] row) ] power) ] of patches
end

;; ---- the paper's Aspiration-Stability matrix, Table 8 ----------------------
;; Both are computed on the grid-averaged matrix, so they are comparable with
;; the aggregate Python model.

to-report clamp01 [ x ]
  if x < 0 [ report 0 ]
  if x > 1 [ report 1 ]
  report x
end

;; People's share, scaled so an even split among four actors reads 0.5.
to-report aspiration
  report clamp01 ((mean-share 0) / 0.5)
end

;; How unconcentrated power is: 1 an even split, 0 one actor holding all.
to-report stability
  let even 0.25
  let total 0
  foreach range 5 [ m ->
    let h 0
    foreach range 4 [ a ->
      let v grid-mean m a
      set h h + (v * v)
    ]
    set total total + (1 - (h - even) / (1 - even))
  ]
  report clamp01 (total / 5)
end

to-report quadrant-name
  ifelse stability >= 0.5 [
    ifelse aspiration >= 0.5
      [ report "II High Potential" ]
      [ report "I Surviving not Thriving" ]
  ] [
    ifelse aspiration >= 0.5
      [ report "III Creative Chaos" ]
      [ report "IV Fragile Collapse" ]
  ]
end

;; Draw the quadrant dividers once, so the scatter has the Table 8 grid
;; behind it.
to draw-quadrants
  set-current-plot "Aspiration-Stability"
  set-current-plot-pen "divider"
  plot-pen-up
  plotxy 0.5 0
  plot-pen-down
  plotxy 0.5 1
  plot-pen-up
  plotxy 0 0.5
  plot-pen-down
  plotxy 1 0.5
  plot-pen-up
end
@#$#@#$#@
GRAPHICS-WINDOW
320
10
748
439
-1
-1
24.0
1
10
1
1
1
0
1
1
1
-8
8
-8
8
0
0
1
ticks
30.0

BUTTON
13
13
93
46
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
99
13
179
46
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
185
13
293
46
go once
go
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

SLIDER
13
60
293
93
heterogeneity
heterogeneity
0
1.5
0.6
0.05
1
NIL
HORIZONTAL

SLIDER
13
96
293
129
diffusion-scale
diffusion-scale
0
2
1.0
0.1
1
NIL
HORIZONTAL

SLIDER
13
132
293
165
check-ratio
check-ratio
0.5
6
1.0
0.25
1
NIL
HORIZONTAL

SLIDER
13
168
293
201
enhance-magnitude
enhance-magnitude
0.02
0.3
0.1
0.01
1
NIL
HORIZONTAL

SLIDER
13
204
293
237
shock-probability
shock-probability
0
0.6
0.15
0.05
1
NIL
HORIZONTAL

SLIDER
13
240
293
273
shock-magnitude
shock-magnitude
0.02
0.3
0.1
0.01
1
NIL
HORIZONTAL

SLIDER
13
276
293
309
concentration-threshold
concentration-threshold
0.2
0.8
0.45
0.05
1
NIL
HORIZONTAL

SLIDER
13
312
293
345
max-ticks
max-ticks
10
300
50.0
10
1
NIL
HORIZONTAL

SWITCH
13
352
293
385
uniform-diffusion?
uniform-diffusion?
1
1
-1000

CHOOSER
13
392
293
437
display-modality
display-modality
"Economic" "Epistemic" "Narrative" "Authoritative" "Physical"
4

MONITOR
13
446
143
491
People hold
mean-share 0
3
1
11

MONITOR
148
446
293
491
State hold
mean-share 1
3
1
11

MONITOR
13
496
143
541
Enterprises hold
mean-share 2
3
1
11

MONITOR
148
496
293
541
AI hold
mean-share 3
3
1
11

MONITOR
13
546
143
591
aspiration
aspiration
3
1
11

MONITOR
148
546
293
591
stability
stability
3
1
11

MONITOR
13
596
293
641
quadrant
quadrant-name
17
1
11

PLOT
320
450
748
640
Aspiration-Stability
aspiration
stability
0.0
1.0
0.0
1.0
false
true
"" ""
PENS
"divider" 1.0 0 -7500403 true "" ""
"path" 1.0 0 -13345367 true "" "plotxy aspiration stability"
"now" 1.0 2 -2674135 true "" "plot-pen-reset plotxy aspiration stability"

PLOT
760
450
1188
640
Regional structure by modality
tick
same everywhere = 1
0.0
50.0
0.0
1.0
true
true
"" ""
PENS
"Economic" 1.0 0 -955883 true "" "plot spread-of 0"
"Epistemic" 1.0 0 -13345367 true "" "plot spread-of 1"
"Narrative" 1.0 0 -8630108 true "" "plot spread-of 2"
"Authoritative" 1.0 0 -10899396 true "" "plot spread-of 3"
"Physical" 1.0 0 -2674135 true "" "plot spread-of 4"

MONITOR
760
398
890
443
local HHI
local-hhi
3
1
11

MONITOR
895
398
1188
443
checks received
checks-against
3
1
11

@#$#@#$#@
# Digital Gorilla, spatial version

Each patch is a locality with its own power matrix: four actors across five
modalities (economic, epistemic, narrative, authoritative, physical). Every
modality's four shares sum to 1 within a locality.

## Reading the map

The icon on each patch is whoever holds the most of the modality chosen in
`display-modality`:

    figure    People
    gavel     the State
    dollar    Enterprises
    robot     AI

The patch behind it is a tint of that actor's colour, darker the stronger its
hold, and the icon grows with it. A region of robots means AI is dominant
there; a jumble of different icons means nobody is.

## What it does

Each tick, inside every locality:

1. The four actors each choose ENHANCE, CHECK or ABSTAIN using the rules from
   Table 6. A CHECK succeeds with a probability set by the two actors'
   legitimacy-weighted power.
2. Power diffuses to the four neighbouring localities, at a rate that depends
   on the modality.
3. With probability `shock-probability` one Table 7 shock hits one locality,
   moving `shock-magnitude` of the disfavoured actor's share there.

## The point

The modalities do not travel equally well. Epistemic and narrative power cross
a border at no cost: a model, a dataset or a piece of synthetic media is
everywhere at once. Authoritative and physical power stop at the edge of the
jurisdiction that grants them: courts, police and infrastructure are fixed.
Economic power is in between.

So the diffusion rates are 0.30 for epistemic and narrative, 0.15 for
economic, 0.05 for authoritative and 0.03 for physical.

The prediction is that regional structure survives in the jurisdiction-bound
modalities and washes out in the informational ones. Set `display-modality` to
Physical and you should see distinct regions; switch it to Narrative and the
map should go flat.

## The Aspiration-Stability plot

The paper's Table 8 matrix. Aspiration is People's share scaled so an even
split reads 0.5; stability is how unconcentrated power is, from the
Herfindahl-Hirschman index. The grey cross marks the 0.5 lines, the blue line
is the path the run has taken and the red dot is where it is now.

    top right      II  High Potential, the target
    top left       I   Surviving not Thriving
    bottom right   III Creative Chaos
    bottom left    IV  Fragile Collapse

Both are computed on the grid-averaged matrix, so they can be compared with
the aggregate Python model.

## The control

Turn `uniform-diffusion?` on. Every modality then diffuses at 0.17, the mean
of the five rates. If the pattern is produced by the differential rates it has
to disappear. In the Python version it does, and the ordering reverses.

## What was predicted and did not happen

The model was also built to test whether diffusion lets an actor escape
checks, by spreading out until it is nowhere locally dominant. It does not.
Diffusion equalises an actor's share across localities without lowering it, so
an actor above the threshold everywhere is still checked everywhere.

## Things to try

- Raise `check-ratio` and watch the red dot climb towards quadrant II. Around
  3 the balance changes.
- Set `diffusion-scale` to 0 for a set of independent localities.
- Set `heterogeneity` to 0 so every locality starts the same, and the grid
  becomes many copies of one aggregate model.

## Notes

This model always runs four actors. The three-actor comparison, the parameter
sweeps and the statistics are in the Python version in the same repository,
which is the authoritative one; this model is for seeing the spatial pattern.

Based on Parra-Orlandoni, Schnyder and Mallet, *The Digital Gorilla:
Rebalancing Power in the Age of AI*.
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

circle
false
0
Circle -7500403 true true 0 0 300

dollar
false
0
Rectangle -7500403 true true 135 30 165 270
Rectangle -7500403 true true 90 60 210 90
Rectangle -7500403 true true 90 60 120 150
Rectangle -7500403 true true 90 135 210 165
Rectangle -7500403 true true 180 150 210 240
Rectangle -7500403 true true 90 210 210 240

gavel
false
0
Rectangle -7500403 true true 45 45 180 120
Polygon -7500403 true true 150 105 255 210 225 240 120 135
Rectangle -7500403 true true 60 255 240 285

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

robot
false
0
Circle -7500403 true true 135 15 30
Rectangle -7500403 true true 144 45 156 78
Rectangle -7500403 true true 90 75 210 165
Rectangle -16777216 true false 112 100 138 126
Rectangle -16777216 true false 162 100 188 126
Rectangle -16777216 true false 120 141 180 153
Rectangle -7500403 true true 105 180 195 258
Rectangle -7500403 true true 60 186 105 231
Rectangle -7500403 true true 195 186 240 231

square
false
0
Rectangle -7500403 true true 30 30 270 270

@#$#@#$#@
NetLogo 6.4.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="spread-by-modality" repetitions="10" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <timeLimit steps="50"/>
    <metric>spread-of 0</metric>
    <metric>spread-of 1</metric>
    <metric>spread-of 2</metric>
    <metric>spread-of 3</metric>
    <metric>spread-of 4</metric>
    <metric>aspiration</metric>
    <metric>stability</metric>
    <enumeratedValueSet variable="uniform-diffusion?">
      <value value="false"/>
      <value value="true"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180

@#$#@#$#@
0
@#$#@#$#@
