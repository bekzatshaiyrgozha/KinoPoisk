import { Link, useNavigate } from 'react-router-dom';
import { FaFilm, FaUser, FaSignOutAlt, FaSearch } from 'react-icons/fa';
import { Button } from '@/components/ui';
import { useAuth } from '@/contexts';
import { ROUTES } from '@/constants';

export const Header = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate(ROUTES.LOGIN);
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to={ROUTES.HOME} className="flex items-center gap-2">
            <FaFilm className="text-primary-600 text-2xl" />
            <span className="text-xl font-bold text-gray-900">KinoPoisk</span>
          </Link>

          <nav className="flex items-center gap-6">
            <Link
              to={ROUTES.SEARCH}
              className="flex items-center gap-2 text-gray-700 hover:text-primary-600 transition-colors font-medium"
            >
              <FaSearch />
              <span>Поиск</span>
            </Link>
          </nav>

          <div className="flex items-center gap-4">
            {isAuthenticated ? (
              <>
                <Link
                  to={ROUTES.PROFILE}
                  className="flex items-center gap-2 text-gray-700 hover:text-primary-600 transition-colors"
                >
                  <FaUser />
                  <span>{user?.username}</span>
                </Link>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleLogout}
                  className="flex items-center gap-2"
                >
                  <FaSignOutAlt />
                  <span>Выход</span>
                </Button>
              </>
            ) : (
              <>
                <Link to={ROUTES.LOGIN}>
                  <Button variant="ghost" size="sm">
                    Войти
                  </Button>
                </Link>
                <Link to={ROUTES.REGISTER}>
                  <Button variant="primary" size="sm">
                    Регистрация
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
