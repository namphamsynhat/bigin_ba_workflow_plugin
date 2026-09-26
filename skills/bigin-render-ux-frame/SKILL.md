---
name: bigin-render-ux-frame
description: Render pure, modular UX design frames for a specified feature (UX-###) directly from the requirements vault (UX specs, navigation map, ENTITIES.md, use cases, business rules). Plans every screen in the screen inventory (1 screen = 1 frame), then generates multiple standalone HTML files (1 HTML file = 1 frame) without outer page layouts (no sidebar, no masthead, no footer) for seamless downstream prototype assembly.
argument-hint: "<UX-###> [--screen <id>] [--state <name>] [--design-system <id>]"
triggers:
  - "bigin-render-ux-frame"
  - "render frame"
  - "render ux frame"
  - "render-ux-frame"
  - "ux frame"
od:
  mode: prototype
  surface: web
  platform: desktop
  scenario: design
  category: prototype
  design_system:
    requires: true
  preview:
    type: html
---

# bigin-render-ux-frame

> [!IMPORTANT]
> **ZERO-QUESTION RESEARCH MANDATE**
> - **DO NOT ask the user clarifying questions or collect discovery briefs.**
> - **ALL ARCHITECTURE, DATA SCHEMAS, AND FLOWS ARE FULLY DEFINED IN THE VAULT.**
> - Read the vault files directly on disk using your file-reading tools (`read_file`, `list_files`, `find_by_name`, `grep_search`).

Render **pure, modular UX design frames** for a single feature specification (`UX-###`) by planning every screen in the Screen Inventory and generating **1 standalone HTML file per screen frame (1 HTML = 1 Frame)** with **ZERO outer page layout** (no sidebar, no header, no footer).

---

## 🎯 The Core Philosophy: 1 HTML File = 1 Frame (Pure Main Workspace Only)

### The Anti-Pattern That Must NEVER Happen:
❌ **DO NOT combine multiple screens into one HTML file with navigation, sidebars, or headers.**
In previous runs, agents mistakenly generated a single HTML file containing an app masthead, a left sidebar menu, and JavaScript toggling between screens. **This corrupts prototype assembly** because combining features later causes duplicate sidebars, clashing headers, and mixed user roles.

### The Golden Rule:
✅ **1 SCREEN IN INVENTORY = 1 STANDALONE HTML FILE = 1 PURE DESIGN FRAME**
If a feature has $N$ screens in `## 2. Screen Inventory`, you MUST write **$N$ separate HTML files** named with both the **UX ID and Screen ID**:
- `ux-<ux_id>-scr-01-<screen-1-slug>.html` (contains ONLY Screen 1)
- `ux-<ux_id>-scr-02-<screen-2-slug>.html` (contains ONLY Screen 2)
- `ux-<ux_id>-scr-03-<screen-3-slug>.html` (contains ONLY Screen 3)
- ...
- `ux-<ux_id>-scr-0N-<screen-n-slug>.html` (contains ONLY Screen $N$)

*(Example for UX-001: `ux-001-scr-01-role-selection.html`, `ux-001-scr-02-registration-form.html`, etc.)*

❌ **FORBIDDEN: NEVER USE BARE NUMBER PREFIXES LIKE `01-<slug>.html` OR `02-<slug>.html`.**
Even if prior turns or assistant responses in the chat history used `01-...`, you MUST ALWAYS use the full `ux-<ux_id>-scr-<screen_id>-<slug>.html` format in the Plan Table, file writes, and `<artifact identifier="...">` tags.

Each HTML file represents **ONLY the inner main content area** highlighted in the red box below:

```
┌────────────────────────────────────────────────────────────────────────┐
│ ❌ STRICTLY FORBIDDEN: Outer App Masthead / Topbar                    │
│    (Brand title, portal name, global search, user avatar, logout)      │
├─────────────┬──────────────────────────────────────────────────────────┤
│ ❌          │                                                          │
│ STRICTLY    │  ✅ ONLY GENERATE THIS INNER MAIN CONTENT FRAME:          │
│ FORBIDDEN:  │  ┌────────────────────────────────────────────────────┐  │
│ Outer Left  │  │ ← Back to [Parent Screen] (if drill-down)          │  │
│ Navigation  │  │ Screen Title & Description                         │  │
│ Sidebar /   │  │ Step Wizard Indicator / Stepper (if wizard)        │  │
│ Menu        │  │ Sub-tabs (if parallel view for same actor)         │  │
│             │  │ Form Cards / Data Grids / Filter Toolbars          │  │
│             │  │ Action Buttons ([Next Step →], [Submit])           │  │
│             │  │ In-screen Modals / Drawers                         │  │
│             │  └────────────────────────────────────────────────────┘  │
│             │                                                          │
├─────────────┴──────────────────────────────────────────────────────────┤
│ ❌ STRICTLY FORBIDDEN: Outer Page Footer                               │
└────────────────────────────────────────────────────────────────────────┘
```

### What Each Individual HTML File Contains:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Frame [N]: [Screen Name]</title>
  <!-- Design system tokens & styles -->
  <style>
    /* Frame & component styles ONLY */
    body {
      margin: 0;
      padding: 32px;
      background: var(--surface-background, #f8fafc);
      font-family: var(--font-body);
    }
    .screen-frame {
      max-width: 1200px;
      margin: 0 auto;
    }
  </style>
</head>
<body>
  <section id="view-<feature-slug>-<screen-slug>" 
           class="screen-frame screen-view" 
           data-ux="UX-###" 
           data-screen="<Screen Name>" 
           data-role="<Role>" 
           data-type="<Primary|Drill-down|Wizard|Tab>">
    <!-- 1. Breadcrumb / Back button (mandatory if Drill-down) -->
    <!-- 2. Screen Header (Title, description, primary action buttons) -->
    <!-- 3. Stepper (if Wizard) or local sub-tabs (if Tab) -->
    <!-- 4. Main Workspace (Form cards, dense tables, filter toolbars) -->
    <!-- 5. Action Buttons ([Next Step →], [Submit], [Save Draft]) -->
    <!-- 6. Screen-Owned Dialogs (Modals, slide-out drawers) -->
  </section>
</body>
</html>
```

### What Each Individual HTML File NEVER Contains:
- ❌ **NO Left Navigation Sidebar**: Never include `<aside class="sidebar">`, navigation menu items, or portal links.
- ❌ **NO Top Masthead / App Header**: Never include portal title, global search bar, user profile pill, or "Log out" button.
- ❌ **NO Outer Page Footer**: Never include global copyright or portal footers.
- ❌ **NO Other Screens**: Never include HTML for another screen inside this file.
- ❌ **NO Switcher / Toggler**: Never include tabs or buttons to switch between different screens.

---

## 📋 Phase 1 — Screen Inventory Planning & Calculation

Before writing any HTML files, the agent MUST read the target UX specification and formulate an explicit **Screen Frame Generation Plan**.

### 1. Ingest Vault Specifications
Read the following files from the workspace:
1. `04-UIUX/UX-### <Feature>.md` (or `04-UIUX/UX-###.md`):
   - `## 1. Actor & Scope`: Discover target user role(s) and record scope (`own:one`, `all:many`).
   - `## 2. Screen Inventory`: Extract the complete list of screens to generate.
   - `## 3. Screen Specs`: Layout wireframe regions, form fields, tables, drawers, modals, status chips.
   - `## 4. Flows`: Step-by-step $S\#$ Success paths, $A\#$ Alternative branches, and $E\#$ Exception states.
2. `04-UIUX/_ux/navigation-map.md`:
   - Note whether each screen is a `(Landing)` screen or a `(Drill-down)` screen.
   - Note the parent landing screen for every drill-down screen to wire the `← Back to [Parent]` button.
3. `01-Requirements/ENTITIES.md` and `01-Requirements/_entities/EN-### *.md`:
   - Read all field names, types, required flags, and allowed enum options for referenced `EN-###` entities.
4. `01-Requirements/_ucs/UC-### *.md`:
   - Read interaction steps, validation triggers, and confirmation dialogs.
5. `01-Requirements/_brs/BR-### *.md`:
   - Read business rules, calculations, and disabled-with-reason conditions.

### 2. Calculate Total Screens & Assign Standalone HTML File Names
- Count the total number of screens declared in `## 2. Screen Inventory`: **$N$ screens**.
- **Mandate**: **$N$ Inventory Screens = Exactly $N$ Separate HTML Files**.
- Assign each screen an unambiguous, sequentially indexed file name embedding both the **UX ID** and **Screen ID** (`SCR-01`, `SCR-02`, ...):
  - **Naming Pattern**: `ux-<ux_id>-scr-<screen_id>-<screen-slug>.html`
  - Screen 1: `ux-###-scr-01-<screen-1-slug>.html` (Screen ID: `SCR-01`)
  - Screen 2: `ux-###-scr-02-<screen-2-slug>.html` (Screen ID: `SCR-02`)
  - ...
  - Screen $N$: `ux-###-scr-0N-<screen-n-slug>.html` (Screen ID: `SCR-0N`)

### 3. Output the Screen Frame Generation Plan
Print the structured plan before generating files:

```markdown
### 📐 Screen Frame Generation Plan (UX-###)

- **Total Screens in Inventory**: N
- **Total HTML Frame Files to Generate**: N
- **Target Role(s)**: [Role A, Role B, ...]

| # | Screen ID | Screen Name | Target HTML File | View ID | Screen Type | Role | Key Entities | Layout Components |
|---|---|---|---|---|---|---|---|---|
| 1 | SCR-01 | [Screen 1] | `ux-###-scr-01-<slug>.html` | `view-<slug>-<screen-1>` | Primary | [Role] | EN-001 | Filter bar, data table, pagination |
| 2 | SCR-02 | [Screen 2] | `ux-###-scr-02-<slug>.html` | `view-<slug>-<screen-2>` | Drill-down | [Role] | EN-001, EN-003 | Back button, detail review card |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
| N | SCR-0N | [Screen N] | `ux-###-scr-0N-<slug>.html` | `view-<slug>-<screen-n>` | Wizard | [Role] | EN-004 | 5-step stepper, input fields, Next Step |

**Plan Calculation Assertion**: Total Inventory Screens (N) == Target HTML Files (N) -> PASS.
**Isolation Check**: 1 HTML File per Frame | Zero Sidebars | Zero App Headers -> PASS.
```

---

## 🎨 Phase 2 — Frame Generation: 1 HTML Frame per Screen

For every screen in the plan (from $1$ to $N$), generate its dedicated standalone HTML frame using Open Design's native `<artifact>` block mechanism (see Phase 3).

### 1. View ID, Screen ID & Machine Metadata
Every screen frame section MUST include:
```html
<section id="view-<feature-slug>-<screen-slug>" 
         class="screen-frame screen-view" 
         data-ux="UX-###" 
         data-screen-id="SCR-01"
         data-screen="<Screen Name>" 
         data-view-id="view-<feature-slug>-<screen-slug>"
         data-role="<Role>" 
         data-type="<Primary | Drill-down | Wizard | Tab>">
```

### 2. The 4 Screen Types
Structure each frame according to its screen type:
- **`Primary`**: Main entry screen (queue, catalog, dashboard, directory). Filter toolbar, search input, dense data table/cards, batch action bar.
- **`Drill-down`**: In-flow inspection, record review, or editing screen. **Mandatory** `← Back to [Parent Screen]` breadcrumb button at top of frame.
- **`Wizard`**: Multi-step creation or intake process. Horizontal progress stepper indicator (`Step 1 of 5`), fieldsets, `[ Next Step → ]`, `[ ← Previous ]`, `[ Submit ]`.
- **`Tab`**: Parallel view under the same landing context for the same actor. In-frame sub-navigation tabs toggling sub-panels within this screen.

### 3. 100% Entity Field Fidelity
- Render **EVERY declared field** from `ENTITIES.md` and `_entities/EN-### *.md` as an interactive input, select dropdown, textarea, or table column.
- Never use placeholder `lorem ipsum`. Use realistic domain data matching the project context.
- In primary lists or queues, generate a minimum of **6–8 diverse mock records** to demonstrate filtering, sorting, and edge cases.

### 4. Interactive Flows & State Transitions
- Wire button clicks, form validations, step advances, and modals in lightweight in-memory JavaScript inside that frame.
- **Disabled-With-Reason (DESIGN-PRINCIPLES #4)**: Any action blocked by a business rule (`BR-###`) MUST display an explanatory tooltip or message.

### 5. Universal Flexbox Viewport & Table Container CSS
Apply standard container styling in the `<style>` block of each HTML file:
```css
.screen-frame {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
  padding: 24px 32px;
  background: var(--surface-background, #f8fafc);
}

.cds-table-container {
  flex: 1;
  min-height: 420px;
  overflow: auto;
  border: 1px solid var(--border-soft, #e2e8f0);
  border-radius: var(--radius-md, 8px);
  background: var(--surface-card, #ffffff);
}

.cds-table thead th {
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--surface-subtle, #f1f5f9);
  font-weight: 600;
  border-bottom: 2px solid var(--border-soft, #e2e8f0);
}
```

---

## 💾 Phase 3 — Delivering Separate Frame Files in Open Design

❌ **NEVER combine all screens into a single `index.html` or `feature.html`.**
❌ **NEVER generate a demo switcher bar, role toggler dropdown, or navigation sidebar.**
❌ **NEVER call `write_file` for screens.** Calling `write_file` and then emitting `<artifact>` tags causes Open Design to duplicate the files with a `-2.html` suffix.

You MUST deliver each screen frame as its own distinct artifact matching the Screen Inventory count ($N$ screens = $N$ distinct files) using Open Design's native artifact stream:

### Delivery Rule: Native `<artifact>` Blocks Only (Zero Duplication)
Emit exactly $N$ separate, sequential source-code `<artifact>` blocks in your response—one for every screen in the inventory:

```html
<artifact identifier="ux-###-scr-01-<screen-1-slug>" type="text/html" title="UX-### SCR-01: <Screen 1 Name>">
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>UX-### SCR-01: <Screen 1 Name></title>
  <style>...</style>
</head>
<body>
  <section id="view-<feature-slug>-<screen-1-slug>" 
           class="screen-frame screen-view" 
           data-ux="UX-###" 
           data-screen-id="SCR-01" 
           data-screen="<Screen 1 Name>" 
           data-view-id="view-<feature-slug>-<screen-1-slug>" 
           data-role="<Role>" 
           data-type="Primary">
    <!-- Pure Screen 1 Workspace Content ONLY (Zero sidebars, Zero headers) -->
  </section>
</body>
</html>
</artifact>

<artifact identifier="ux-###-scr-02-<screen-2-slug>" type="text/html" title="UX-### SCR-02: <Screen 2 Name>">
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>UX-### SCR-02: <Screen 2 Name></title>
  <style>...</style>
</head>
<body>
  <section id="view-<feature-slug>-<screen-2-slug>" 
           class="screen-frame screen-view" 
           data-ux="UX-###" 
           data-screen-id="SCR-02" 
           data-screen="<Screen 2 Name>" 
           data-view-id="view-<feature-slug>-<screen-2-slug>" 
           data-role="<Role>" 
           data-type="Drill-down">
    <!-- Pure Screen 2 Workspace Content ONLY (Zero sidebars, Zero headers) -->
  </section>
</body>
</html>
</artifact>
```

Open Design's engine will automatically parse each `<artifact>` tag, create the corresponding standalone `.html` files in the project workspace (named `ux-###-scr-01-<slug>.html`, etc.), and display interactive preview cards in the chat.

> [!WARNING]
> **PREVENT DUPLICATION MANDATES:**
> - **DO NOT call `write_file` or filesystem tools for the HTML frames**: Open Design automatically extracts each `<artifact>` tag into its own file. If you call `write_file` first and then output `<artifact>` tags, Open Design sees the file already on disk and renames the artifact to `*-2.html`.
> - **DO NOT emit duplicate `<artifact>` tags** for the same screen.
> - **DO NOT wrap `<artifact>` inside markdown code fences (` ```html `)**: Emit raw `<artifact ...> ... </artifact>` tags directly in the response text.

---

## ✅ Pre-Delivery Quality Checklist

Before completing execution, verify:
- [ ] **Exact File Count & Naming Match**: Total `<artifact>` blocks emitted equals total screens in `## 2. Screen Inventory` ($N$ screens = $N$ HTML files), each named with `ux-<ux_id>-scr-<screen_id>-<slug>.html` (e.g. `ux-001-scr-01-role-selection.html`).
- [ ] **Artifact Titles**: Every `<artifact>` title includes the UX and Screen ID (`UX-### SCR-01: <Screen Name>`).
- [ ] **Zero Duplication**: No `*-2.html` files generated; each screen is emitted in exactly one `<artifact>` block without calling `write_file`.
- [ ] **1 HTML = 1 Frame**: Each HTML file contains exactly one `<section class="screen-frame">`. No screen mixing.
- [ ] **Zero Page Layout (Red-Box Isolation)**:
  - [ ] NO outer left sidebar / navigation menu in any file.
  - [ ] NO top app masthead / portal header in any file.
  - [ ] NO global outer footer in any file.
  - [ ] NO demo switcher bar, queue mode selector, or role toggler.
- [ ] **Breadcrumb / Back Button**: Every `Drill-down` frame includes a prominent `← Back to [Parent]` button.
- [ ] **Stepper Indicators**: Every `Wizard` frame features a horizontal progress stepper matching the UX flow.
- [ ] **100% Entity Coverage**: All fields from `ENTITIES.md` and referenced `_entities/EN-###` are present in forms and tables.
- [ ] **Realistic Mock Data**: Tables have 6–8 diverse records; no `lorem ipsum` or placeholder text.
- [ ] **Disabled-With-Reason**: Inactive actions display explanatory tooltips/badges.
- [ ] **Traceability & Screen ID Machine Metadata**: All `data-ux="UX-###"`, `data-screen-id="SCR-##"`, `data-view-id="view-..."`, `data-screen="<Name>"`, `data-role="<Role>"` exist as machine attributes, NEVER as leaked visible text.
- [ ] **Separate Delivery**: Each frame was emitted as its own distinct `<artifact>` tag.

