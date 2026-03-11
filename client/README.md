# Placement Portal - Frontend

Vue 3 single-page application for the Placement Portal. Provides role-based dashboards for **Students**, **Companies**, and **Admin**.

## Tech Stack

- **Vue 3** - Composition API
- **Vue Router 4** - Client-side routing with role-based navigation guards
- **Pinia** - State management
- **Axios** - REST API client
- **Vite** - Dev server and build tool

## Project Structure

```
src/
├── api/            # Axios wrappers per role (auth, admin, company, student)
├── components/     # Reusable UI components (AppButton, AppModal, etc.)
│   ├── admin/
│   ├── common/
│   ├── company/
│   └── student/
├── layouts/        # Per-role layout shells (AdminLayout, CompanyLayout, StudentLayout)
├── router/         # Vue Router config with auth guards
├── stores/         # Pinia stores (auth, admin, company, student)
├── styles/         # Global CSS design system
├── utils/          # Constants, formatters, validators
└── views/          # Page-level components
    ├── admin/
    ├── auth/
    ├── company/
    ├── shared/
    └── student/
```

## Setup

### Prerequisites

- [Bun](https://bun.sh) (recommended) or Node >= 20.19

### Install dependencies

```bash
bun install
# or: npm install
```

### Development server

```bash
bun dev
# or: make run
```

Runs on **http://localhost:5173** by default. The backend API is expected at `http://localhost:5000`.

### Production build

```bash
bun run build
```

Output is placed in `dist/`.

### Preview production build

```bash
bun preview
```

### Lint & format

```bash
bun lint      # ESLint + oxlint (auto-fix)
```

## Environment

The API base URL is configured in `src/api/axios.js`. For a custom backend URL, update that file or proxy via `vite.config.js`.

## IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue - Official](https://marketplace.visualstudio.com/items?itemName=Vue.volar) extension (disable Vetur if installed).
