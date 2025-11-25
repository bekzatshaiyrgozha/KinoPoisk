# KinoPoisk Frontend

Modern React + TypeScript frontend for KinoPoisk movie platform.

## 🚀 Tech Stack

- **React 19** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router v7** - Routing
- **Axios** - HTTP client
- **React Icons** - Icons

## 📁 Project Structure

```
src/
├── components/           # React components
│   ├── ui/              # Reusable UI components (Button, Input, Card, etc.)
│   ├── layout/          # Layout components (Header, Footer, MainLayout)
│   ├── features/        # Feature-specific components
│   │   ├── movies/      # Movie components (MovieCard, MovieList, RatingStars)
│   │   ├── comments/    # Comment components
│   │   └── auth/        # Auth components
│   └── common/          # Shared components (ErrorBoundary, etc.)
│
├── pages/               # Page components
│   ├── Home/            # Home page with movie list
│   ├── MovieDetail/     # Movie detail page
│   ├── Login/           # Login page
│   └── Register/        # Register page
│
├── contexts/            # React Context providers
│   └── AuthContext.tsx  # Authentication context
│
├── hooks/               # Custom React hooks
│   ├── useMovies.ts     # Movies data fetching
│   ├── useMovie.ts      # Single movie fetching
│   ├── useComments.ts   # Comments fetching
│   ├── useDebounce.ts   # Debounce hook
│   └── ...
│
├── services/            # API services (READY FOR BACKEND!)
│   ├── api/
│   │   ├── api.client.ts    # Axios instance with interceptors
│   │   └── api.config.ts    # API configuration
│   ├── auth.service.ts      # Auth API calls
│   ├── movie.service.ts     # Movie API calls
│   ├── comment.service.ts   # Comment API calls
│   ├── rating.service.ts    # Rating API calls
│   └── like.service.ts      # Like API calls
│
├── types/               # TypeScript types (match backend models)
│   ├── entities/        # Backend entity types (User, Movie, Comment, etc.)
│   ├── api/             # API types (ApiResponse, ApiError, etc.)
│   └── common/          # Common types (Pagination, etc.)
│
├── utils/               # Utility functions
│   ├── cn.ts            # className utility (clsx + tailwind-merge)
│   ├── format.ts        # Formatting utilities (date, rating, etc.)
│   ├── validation.ts    # Validation functions
│   └── storage.ts       # LocalStorage helpers
│
├── constants/           # Constants
│   ├── routes.ts        # Route paths
│   ├── api.endpoints.ts # API endpoints
│   ├── genres.ts        # Movie genres
│   └── messages.ts      # UI messages
│
└── assets/              # Static assets (images, icons)
```

## 🏗️ Architecture Principles

### SOLID
- **Single Responsibility**: Each component/function has one purpose
- **Open/Closed**: Components are extensible via props
- **Liskov Substitution**: All components of same type are interchangeable
- **Interface Segregation**: Small, specific TypeScript interfaces
- **Dependency Inversion**: Depend on abstractions (interfaces)

### DRY (Don't Repeat Yourself)
- Shared UI components in `components/ui/`
- Reusable hooks in `hooks/`
- Utility functions in `utils/`
- Barrel exports (`index.ts`) for clean imports

### KISS (Keep It Simple, Stupid)
- Simple, straightforward components
- No over-engineering
- Clear, readable code

## 📦 Installation

```bash
# Install dependencies
npm install react-router-dom axios react-icons clsx tailwind-merge date-fns

# Start development server
npm run dev

# Build for production
npm run build
```

See [INSTALL.md](./INSTALL.md) for more details.

## 🔌 Backend Integration

**The frontend is READY for backend integration!**

### To connect to backend:

1. Create `.env.local` file:
```env
VITE_API_URL=http://localhost:8000/api
```

2. Start backend server

3. That's it! No code changes needed.

### How it works:
- All API calls centralized in `services/`
- Axios interceptors auto-add auth tokens
- Types match backend Django models exactly
- Endpoints match Django URLs

## 🎨 Components

### UI Components
- `Button` - Variants: primary, secondary, danger, ghost
- `Input` - With label, error, helper text
- `Card` - Container with padding/shadow
- `Loader` - Loading spinner
- `Badge` - Small label

### Feature Components
- `MovieCard` - Movie preview card
- `MovieList` - Grid of movies
- `RatingStars` - Interactive rating

### Layout
- `Header` - Site header
- `Footer` - Site footer
- `MainLayout` - Page wrapper

## 🪝 Custom Hooks

- `useAuth()` - Authentication state
- `useMovies(filters)` - Fetch movies
- `useMovie(id)` - Fetch single movie
- `useComments(movieId)` - Fetch comments
- `useDebounce(value)` - Debounce value
- `useLocalStorage(key)` - LocalStorage state
- `useClickOutside(ref)` - Click outside detector

## 🚀 Development

```bash
npm run dev      # Start dev server (http://localhost:5173)
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

## 🎯 Features Ready

✅ User Authentication (Login/Register)
✅ Movie Listing
✅ Movie Detail View
✅ Star Rating Component
✅ Responsive Design
✅ TypeScript Type Safety
✅ Error Handling
✅ Loading States
✅ Form Validation

## 🔮 Ready for Extension

- AI Chat widget
- Comment section
- User profiles
- Favorites/Wishlist
- Advanced search/filtering
- Real-time updates

All components designed for easy extension!

## 📝 License

Part of KinoPoisk platform.
