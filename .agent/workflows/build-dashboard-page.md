# Workflow: Build Dashboard Page

Use this workflow to add a new page to the React frontend.

## Step 1: Check UI Style Guidelines
- Use Tailwind CSS.
- Ensure the design is dark, professional, and SOC-style (e.g., TailAdmin).
- Avoid generic colors; use predefined design system tokens.

## Step 2: Define Data Hooks
- Check if the required API endpoint exists in `apps/backend/`.
- If not, use mock JSON data first before requesting backend changes.
- Create or update a custom React hook in `apps/frontend/src/hooks/` to fetch data.

## Step 3: Build Components
- Break the page into reusable pieces (e.g., tables, charts, cards) in `apps/frontend/src/components/`.
- Ensure charts use Recharts or Chart.js and have readable tooltips.

## Step 4: Assemble the Page
- Create the page inside `apps/frontend/src/pages/`.
- Wire up the hooks and components.
- Add the route to the main router.

## Step 5: Test
- Run `npm run lint`.
- Verify the page renders correctly in dark mode.
- Add a basic e2e test if it's a core workflow.
