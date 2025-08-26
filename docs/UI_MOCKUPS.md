# Interactive Debate Bingo - UI Mockups & Components

## 🖥️ Desktop Layout (1920x1080)

### Main Game Screen
```
┌────────────────────────────────────────────────────────────────────────┐
│ 🔴 LIVE  Democratic Primary Debate                     👥 247 Players  │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐  ┌─────────────────────┐  ┌──────────────────┐ │
│  │   MY BINGO CARD  │  │   LIVE ACTIVITY     │  │   SCOREBOARD     │ │
│  │                  │  │                     │  │                  │ │
│  │  ┌──┬──┬──┬──┬──┐│  │ 🔵 Sarah marked    │  │ 🥇 Mike      4/5 │ │
│  │  │✓ │  │✓ │  │  ││  │ "economy" (2s ago) │  │ 🥈 Sarah     4/5 │ │
│  │  ├──┼──┼──┼──┼──┤│  │                     │  │ 🥉 You       3/5 │ │
│  │  │  │✓ │  │  │✓ ││  │ 🟡 Mike is 1 away  │  │ 4. Tom       2/5 │ │
│  │  ├──┼──┼──┼──┼──┤│  │ from BINGO!        │  │ 5. Amy       2/5 │ │
│  │  │✓ │  │FREE│  │ ││  │                     │  │                  │ │
│  │  ├──┼──┼──┼──┼──┤│  │ 🔴 Jennifer called │  │ ┌──────────────┐ │ │
│  │  │  │  │✓ │✓ │  ││  │ BINGO! [VERIFY]    │  │ │ Your Stats   │ │ │
│  │  ├──┼──┼──┼──┼──┤│  │                     │  │ ├──────────────┤ │ │
│  │  │  │✓ │  │  │  ││  │ ⚠️ Tom disputed    │  │ │ Score: 340   │ │ │
│  │  └──┴──┴──┴──┴──┘│  │ Jennifer's call    │  │ │ Speed: #12   │ │ │
│  │                  │  │                     │  │ │ Accuracy:95% │ │ │
│  │  [CALL BINGO!]   │  │ 💬 Chat enabled     │  │ └──────────────┘ │ │
│  └──────────────────┘  └─────────────────────┘  └──────────────────┘ │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### Dispute Modal
```
┌─────────────────────────────────────────┐
│          ⚠️ DISPUTE IN PROGRESS         │
├─────────────────────────────────────────┤
│                                         │
│  Jennifer marked: "Candidate coughs"    │
│                                         │
│  Disputed by: Tom                      │
│  Reason: "Didn't happen"               │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │         VOTE TO RESOLVE          │   │
│  │                                  │   │
│  │    ✅ VALID        ❌ INVALID    │   │
│  │    (12 votes)     (8 votes)     │   │
│  │                                  │   │
│  │    [============      ] 60%      │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ⏱️ Time remaining: 23 seconds          │
│                                         │
│  [VOTE: VALID]    [VOTE: INVALID]      │
└─────────────────────────────────────────┘
```

## 📱 Mobile Layout (390x844 - iPhone 14)

### Tab Navigation View
```
┌─────────────────────────┐
│ 🔴 LIVE Debate          │
│ 👥 247 Players          │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ CARD │ FEED │ SCORE │ │
│ └─────────────────────┘ │
├─────────────────────────┤
│                         │
│    ┌──┬──┬──┬──┬──┐    │
│    │✓ │  │✓ │  │  │    │
│    ├──┼──┼──┼──┼──┤    │
│    │  │✓ │  │  │✓ │    │
│    ├──┼──┼──┼──┼──┤    │
│    │✓ │  │⭐│  │  │    │
│    ├──┼──┼──┼──┼──┤    │
│    │  │  │✓ │✓ │  │    │
│    ├──┼──┼──┼──┼──┤    │
│    │  │✓ │  │  │  │    │
│    └──┴──┴──┴──┴──┘    │
│                         │
│    [  CALL BINGO!  ]    │
│                         │
└─────────────────────────┘
```

### Activity Feed Tab
```
┌─────────────────────────┐
│ 🔴 LIVE Debate          │
│ 👥 247 Players          │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ CARD │ FEED │ SCORE │ │
│ └─────────────────────┘ │
├─────────────────────────┤
│ ┌─────────────────────┐ │
│ │ 🔵 Sarah • 2s ago   │ │
│ │ Marked "economy"     │ │
│ │ 👍 😂 🎯            │ │
│ └─────────────────────┘ │
│ ┌─────────────────────┐ │
│ │ 🟡 Mike • 15s ago   │ │
│ │ 1 square from BINGO! │ │
│ │ 😱 🔥 👀            │ │
│ └─────────────────────┘ │
│ ┌─────────────────────┐ │
│ │ 🔴 Jennifer • 30s   │ │
│ │ CALLED BINGO!        │ │
│ │ [VERIFY] [DISPUTE]   │ │
│ └─────────────────────┘ │
│                         │
│ [💬 Send Message...]    │
└─────────────────────────┘
```

## 🎨 Component Designs

### Bingo Card Square States
```
┌─────────────────────────────────────┐
│          Square States              │
├─────────────────────────────────────┤
│                                     │
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐   │
│  │    │  │ ✓  │  │⭐ │  │ 🔒 │   │
│  └────┘  └────┘  └────┘  └────┘   │
│  Empty   Marked   Free   Disputed  │
│                                     │
│  ┌────┐  ┌────┐  ┌────┐  ┌────┐   │
│  │ ⚡ │  │ 🏆 │  │ ❌ │  │ ⏳ │   │
│  └────┘  └────┘  └────┘  └────┘   │
│  Bonus   Winner  Invalid  Pending  │
└─────────────────────────────────────┘
```

### Live Activity Item
```
┌──────────────────────────────────┐
│  [Avatar] Sarah                  │
│  ├─ Marked "mentions economy"    │
│  ├─ 12 seconds ago               │
│  └─ 👍(5) 😂(2) 🎯(1)           │
│                                  │
│  [👍] [😂] [🎯] [🤔] [Reply]    │
└──────────────────────────────────┘
```

### Scoreboard Entry
```
┌──────────────────────────────────┐
│  🥇 1st Place         ↑ +2       │
│  ┌──┐                            │
│  │AV│ Mike_2024      ⚡ 4/5      │
│  └──┘                            │
│  Score: 450 | Speed: #1          │
│  [═════════════════   ] 80%      │
└──────────────────────────────────┘
```

### Dispute Notification Toast
```
┌──────────────────────────────────┐
│  ⚠️ DISPUTE ALERT                │
│  Tom disputed Jennifer's BINGO   │
│  Vote now to resolve!            │
│  [VOTE] [DISMISS]    (23s)       │
└──────────────────────────────────┘
```

## 🎭 Animation & Interaction States

### Square Mark Animation
```
1. User clicks square
2. Square pulses (scale 1.2x)
3. Checkmark fades in
4. Ripple effect outward
5. Activity feed notification slides in
```

### BINGO Call Animation
```
1. Confetti burst from button
2. Card highlights winning pattern
3. Modal slides up from bottom
4. Countdown timer starts
5. Other players notified
```

### Dispute Flow
```
User Journey:
┌────────┐     ┌──────────┐     ┌────────┐
│ See    │ --> │ Click    │ --> │ Submit │
│ Activity│     │ Dispute  │     │ Reason │
└────────┘     └──────────┘     └────────┘
     |              |                 |
     v              v                 v
┌────────┐     ┌──────────┐     ┌────────┐
│ Toast  │     │ Modal    │     │ Vote   │
│ Appears│     │ Opens    │     │ Starts │
└────────┘     └──────────┘     └────────┘
```

## 🎨 Color Scheme

### Light Mode
```css
--primary: #3B82F6;      /* Blue */
--success: #10B981;      /* Green */
--warning: #F59E0B;      /* Yellow */
--danger: #EF4444;       /* Red */
--background: #FFFFFF;
--surface: #F3F4F6;
--text: #111827;
--text-secondary: #6B7280;
```

### Dark Mode
```css
--primary: #60A5FA;
--success: #34D399;
--warning: #FBBF24;
--danger: #F87171;
--background: #111827;
--surface: #1F2937;
--text: #F9FAFB;
--text-secondary: #9CA3AF;
```

## 📊 Real-Time Visual Indicators

### Connection Status
```
🟢 Connected (latency: 12ms)
🟡 Reconnecting...
🔴 Disconnected
```

### Player Activity Indicators
```
⚡ Active (marking squares)
👁️ Watching (no recent activity)
💤 Idle (>5 min inactive)
🏆 Winner
```

### Score Trends
```
📈 Climbing (moved up 3+ spots)
📉 Falling (moved down 3+ spots)
➡️ Steady (no change)
🚀 On fire! (5+ squares in 30s)
```

## 🔔 Notification Types

### Visual Notifications
```
┌─────────────────────────────┐
│ 🎯 Pattern Complete!        │
│ You completed a diagonal    │
│ +75 points                  │
└─────────────────────────────┘

┌─────────────────────────────┐
│ ⚡ Speed Bonus!             │
│ First to mark this square   │
│ +5 points                   │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 🏆 New Leader!              │
│ Mike just took 1st place    │
└─────────────────────────────┘
```

## 🎮 Interactive Elements

### Hover States
- Square: Show phrase text + who else marked it
- Player name: Show mini profile card
- Activity: Show full timestamp + reactions

### Click Actions
- Square: Mark/unmark with animation
- Player: View their card
- Activity: Expand details/add reaction

### Long Press (Mobile)
- Square: Show dispute option
- Activity: Show reaction menu
- Player: Show quick actions

## 📱 Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 640px) {
  /* Single column, tabs */
}

/* Tablet */
@media (min-width: 641px) and (max-width: 1024px) {
  /* Two columns: Card + Feed */
}

/* Desktop */
@media (min-width: 1025px) {
  /* Three columns: Card + Feed + Scoreboard */
}

/* Large Desktop */
@media (min-width: 1440px) {
  /* Enhanced spacing, larger text */
}
```

## 🚀 Performance Considerations

### Virtualization
- Activity feed: Virtual scroll for 100+ items
- Scoreboard: Virtual list for 50+ players
- Chat messages: Lazy load older messages

### Optimistic Updates
- Mark square immediately, sync later
- Show reactions instantly
- Update score optimistically

### Debouncing
- Search: 300ms debounce
- Typing indicators: 1s debounce
- Hover tooltips: 500ms delay

---

This comprehensive UI mockup guide provides detailed layouts, components, and interaction patterns for the interactive multiplayer Debate Bingo experience.