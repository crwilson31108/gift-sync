# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Gift Sync is a family gift management application with a Django REST Framework backend and Vue 3 frontend. Users create families, build wishlists, and track gift purchases within their family groups. The app prevents wishlist owners from seeing who purchased items to maintain gift surprises.

## Development Commands

### Backend (Django)

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser

# Run development server (default: http://localhost:8000)
python manage.py runserver

# Run specific tests
python manage.py test core.tests.TestClassName

# Collect static files (production)
python manage.py collectstatic --noinput
```

### Frontend (Vue 3 + Vite)

```bash
# Navigate to frontend directory
cd gift-wishlist-frontend

# Install dependencies
npm install

# Run development server (default: http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Architecture Overview

### Backend Structure

**Framework**: Django 5.0+ with Django REST Framework

**Key Models** (`backend/core/models.py`):
- `User`: Custom user model with email authentication (no username), profile picture, bio, date of birth
- `Family`: Container for multiple users via ManyToMany relationship
- `WishList`: Belongs to one owner and one family
- `WishListItem`: Automatically calculates size category from price (Stocking: $0-25, Small: $26-50, Medium: $51-100, Large: $100+). Has priority field for manual ordering and drag-to-reorder support
- `Notification`: Activity feed for new items, purchases, wishlist creation

**API Endpoints** (`backend/core/views.py`):
- `/api/token/` - JWT authentication (access + refresh tokens)
- `/api/users/me/` - Current user profile
- `/api/users/search/?q=query` - Search users (minimum 3 characters, only returns users in same families)
- `/api/families/` - CRUD families, add/remove members
- `/api/wishlists/` - CRUD wishlists, filter by `?family=id` or `?owner=id`
- `/api/wishlists/stats/` - User statistics (counts of wishlists, items, purchases, families)
- `/api/wishlists/recent_activity/` - Recent family activity excluding own wishlists
- `/api/wishlist-items/` - CRUD items
- `/api/wishlist-items/{id}/purchase/` - Mark item as purchased
- `/api/wishlist-items/{id}/unpurchase/` - Unmark purchase
- `/api/wishlist-items/scrape_url/` - Extract product data from URL using web scraper
- `/api/wishlist-items/reorder_items/` - Batch update item priorities for drag-and-drop
- `/api/notifications/` - User notifications
- `/api/password-reset/request_reset/` - Request password reset email (SendGrid)
- `/api/password-reset/reset_password/` - Confirm password reset with token

**Authentication**: JWT tokens with 7-day access token and 14-day refresh token lifetimes. Token rotation enabled with blacklist.

**Key Features**:
- **Purchase Privacy**: WishListItem serializer removes `is_purchased`, `purchased_by`, and `purchased_at` fields when serializing for the item's owner to maintain gift surprise
- **Multi-Tier Web Scraper** (`backend/core/utils/scraper.py`):
  - **Tier 1**: Meta tags & JSON-LD (OpenGraph, Twitter Card, Schema.org) - Fast, works on 80% of sites
  - **Tier 2**: Site-specific selectors for top retailers (Amazon, Etsy, Best Buy, Target, Walmart, Wayfair, Home Depot, eBay) - Fast, 95% success on supported sites
  - **Tier 3**: Playwright browser rendering for JavaScript-heavy sites - Slower but handles React/Vue/Angular apps (optional, controlled by `USE_PLAYWRIGHT` env var)
  - Returns `scrape_method` metadata to track which method succeeded
  - Graceful error handling with detailed messages and manual entry fallback
  - See `backend/SCRAPER_GUIDE.md` for complete documentation
- **Email Service** (`backend/core/utils/sendgrid_client.py`): SendGrid integration for password reset emails with environment-aware frontend URLs
- **Smart Item Save**: Prevents duplication of `image` and `image_url` fields
- **Auto-priority**: New items automatically get highest priority + 1

### Frontend Structure

**Framework**: Vue 3 + TypeScript + Vite

**Key Directories**:
- `src/router/` - Vue Router with authentication guards
- `src/stores/` - Pinia store for centralized state (current user, notifications, theme, token)
- `src/services/` - API service layer (auth, wishlists, families, users, notifications)
- `src/pages/` - Route components (LoginPage, WishlistDetail, FamilyDetail, etc.)
- `src/components/` - Reusable components
- `src/layouts/` - MainLayout (authenticated) and AuthLayout (login)
- `src/types/` - TypeScript interfaces

**State Management** (`src/stores/useAppStore.ts`):
- Pinia store with persistence (localStorage)
- Stores: `currentUser`, `token`, `notifications`, `isDarkTheme`, `itemOrder` (for drag-and-drop)
- Key actions: `initializeApp()`, `logout()`, `fetchNotifications()`, `setItemOrder()`
- Auto-logout on token expiration (401/403 with specific error messages)

**Routing** (`src/router/index.ts`):
- Authentication guard redirects unauthenticated users to `/login`
- Saves intended destination in localStorage for post-login redirect
- Public routes: `/login`, `/request-password-reset`, `/reset-password/:userId/:token`

**API Integration** (`src/services/api.ts`):
- Axios instance with `Authorization: Bearer {token}` header injection
- Response interceptor detects JWT expiration and triggers auto-logout
- Base URL from environment variables (`.env.development` vs `.env.production`)

**UI Framework**:
- Vuetify 3 with custom theme (primary: red #D32F2F, secondary: green #388E3C, accent: gold #FFD700)
- Tailwind CSS 3.4 for utility styling with dark mode support
- Material Design Icons via `@mdi/font`
- Toast notifications via `vue-toastification`

**Key Pages**:
- `WishlistDetail.vue`: Shows wishlist items with drag-to-reorder mode for owners, purchase buttons for family members
- `FamilyDetail.vue`: Displays family members and their wishlists
- `HomePage.vue`: Dashboard with statistics and recent activity
- `NotificationsPage.vue`: Activity feed for purchases, new items, new wishlists

### Critical Workflows

**Item Reordering**:
1. Owner clicks "Arrange Items" on wishlist detail page
2. Drag items to new positions
3. On drop, frontend updates `itemOrder` in Pinia store
4. Frontend sends `POST /api/wishlist-items/reorder_items/` with `{ wishlist_id, item_ids: [...] }`
5. Backend sets each item's priority to match array index
6. Click "Exit Arrange Mode" to finalize

**Purchase Flow**:
1. Family member views another member's wishlist
2. Clicks "Purchase" button on item
3. Frontend: `POST /api/wishlist-items/{id}/purchase/`
4. Backend sets `is_purchased=True`, `purchased_by=current_user`, `purchased_at=now()`
5. Backend serializer hides purchase fields from wishlist owner (surprise protection)
6. Notification created for wishlist owner
7. Family member can unpurchase if needed

**URL Scraping**:
1. User pastes retail URL in item creation form
2. Clicks "Scrape URL" button
3. Frontend: `POST /api/wishlist-items/scrape_url/` with URL
4. Backend ProductScraper uses multi-tier approach:
   - Tries meta tags & JSON-LD first (fast)
   - Falls back to site-specific selectors if available
   - Uses Playwright browser rendering if enabled and needed
   - Returns detailed error with `scrape_method` metadata
5. Frontend populates form fields with scraped data
6. If scraping fails, form stays populated with URL and user can enter details manually
7. User can edit before saving

**Token Validation**:
- Frontend calls `initializeApp()` on app load
- Validates token via `GET /api/users/me/`
- On 401/403 with token expiration error, triggers `logout()` and redirects to `/login`
- Saves current route to localStorage for post-login redirect

## Environment Configuration

**Backend** (`backend/.env`):
```
SECRET_KEY=<django-secret-key>
DEBUG=True
DATABASE_URL=<postgresql-url-for-production>
FRONTEND_URL=http://localhost:5173  # or https://gift-sync.vercel.app
SENDGRID_API_KEY=<sendgrid-api-key>
USE_PLAYWRIGHT=true  # Optional: Enable Playwright browser rendering for scraping (default: true if installed)
```

**Scraper Configuration**:
- `USE_PLAYWRIGHT=true`: Enable Playwright for JavaScript-heavy sites (requires `python -m playwright install chromium`)
- `USE_PLAYWRIGHT=false`: Disable Playwright, use only requests-based scraping (Tier 1 & 2)
- If Playwright is not installed, it's automatically disabled regardless of env var

**Frontend**:
- `.env.development`: `VITE_API_BASE_URL=http://localhost:8000/api`
- `.env.production`: `VITE_API_BASE_URL=https://gift-sync-production.up.railway.app/api`

## Deployment

**Backend**: Railway (https://gift-sync-production.up.railway.app)
- Uses PostgreSQL database
- Procfile: `python manage.py collectstatic --noinput && python manage.py migrate && gunicorn backend.wsgi`
- WhiteNoise serves static files
- Auto-migrates on deploy

**Frontend**: Vercel (https://gift-sync.vercel.app)
- Vite build output to `dist/`
- SPA routing configured in `vercel.json`
- Environment variable: `VITE_API_BASE_URL`

## Important Patterns

**Security**:
- CORS whitelist (no wildcard): `http://localhost:5173`, `http://localhost:3000`, `https://gift-sync.vercel.app`
- JWT with HS256, token rotation, blacklist on rotation
- Custom User model with email authentication (no username field)
- Family-based data isolation (users only see data from their families)

**Data Visibility**:
- WishListItem serializer has special logic: removes `is_purchased`, `purchased_by`, `purchased_at` when serializing for the wishlist owner
- This ensures gift surprises are maintained (owners don't see who bought their items)

**Image Handling**:
- WishListItem automatically downloads `image_url` to local `image` field on save
- Image Download Utility (`backend/core/utils/image_downloader.py`): Downloads, validates, optimizes images
- Clears `image_url` after successful download to prevent external URL issues
- Falls back to `image_url` if download fails
- Frontend prefers local `image` over `image_url` when displaying
- Frontend supports FormData for file uploads
- Management command available: `python manage.py download_wishlist_images [options]`
  - `--dry-run`: Preview changes without executing
  - `--rescrape`: Auto re-scrape product pages when image download fails (recommended for backfilling)
  - `--force`: Re-download all images even if local copy exists
- Re-scraping: If image download fails and item has a `link`, automatically re-scrapes the product page to get a fresh image URL

**Size Calculation**:
- WishListItem automatically sets `size` based on price:
  - Stocking: $0-25
  - Small: $26-50
  - Medium: $51-100
  - Large: $100+

**Priority Management**:
- New items get `priority = max(existing_priorities) + 1`
- Drag-and-drop reorder updates all item priorities in batch via `reorder_items` endpoint
- Items ordered by `priority` DESC, then `created_at` DESC

**Password Reset**:
- Uses Django's `default_token_generator` for secure one-time tokens
- SendGrid sends HTML email with reset link: `{FRONTEND_URL}/reset-password/{user_id}/{token}`
- Token validation happens in backend before allowing password change
