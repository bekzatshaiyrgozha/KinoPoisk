import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts';
import { MainLayout } from './components/layout';
import { HomePage, MovieDetailPage, LoginPage, RegisterPage } from './pages';
import { ROUTES } from './constants';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <MainLayout>
          <Routes>
            <Route path={ROUTES.HOME} element={<HomePage />} />
            <Route path={ROUTES.MOVIE_DETAIL} element={<MovieDetailPage />} />
            <Route path={ROUTES.LOGIN} element={<LoginPage />} />
            <Route path={ROUTES.REGISTER} element={<RegisterPage />} />
            <Route
              path={ROUTES.NOT_FOUND}
              element={
                <div className="container mx-auto px-4 text-center py-20">
                  <h1 className="text-4xl font-bold text-gray-900">404</h1>
                  <p className="text-gray-600 mt-2">Страница не найдена</p>
                </div>
              }
            />
          </Routes>
        </MainLayout>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
