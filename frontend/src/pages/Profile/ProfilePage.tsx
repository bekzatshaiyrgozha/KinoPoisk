import { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, Loader, Button } from '@/components/ui';
import { useAuth } from '@/contexts';
import { ROUTES } from '@/constants';

export const ProfilePage = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      navigate(ROUTES.LOGIN);
    }
  }, [isAuthenticated, isLoading, navigate]);

  if (isLoading || (!user && isAuthenticated)) {
    return (
      <div className="container mx-auto px-4">
        <Loader size="lg" className="py-20" />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container mx-auto px-4 max-w-lg">
        <Card padding="lg">
          <div className="space-y-4 text-center">
            <p className="text-gray-700">Чтобы посмотреть профиль, авторизуйтесь.</p>
            <div className="flex justify-center gap-3">
              <Link to={ROUTES.LOGIN}>
                <Button variant="primary">Войти</Button>
              </Link>
              <Link to={ROUTES.REGISTER}>
                <Button variant="ghost">Регистрация</Button>
              </Link>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  const fullName = `${user.first_name ?? ''} ${user.last_name ?? ''}`.trim();

  return (
    <div className="container mx-auto px-4 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Профиль</h1>
        <p className="text-gray-600 mt-2">Данные вашей учетной записи</p>
      </div>

      <div className="grid gap-6">
        <Card padding="lg">
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-500">Email</p>
              <p className="text-lg font-semibold text-gray-900">{user.email}</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Имя</p>
                <p className="text-lg font-semibold text-gray-900">
                  {fullName || 'Не указано'}
                </p>
              </div>
              {user.date_joined && (
                <div>
                  <p className="text-sm text-gray-500">Дата регистрации</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {new Date(user.date_joined).toLocaleDateString('ru-RU', {
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric',
                    })}
                  </p>
                </div>
              )}
            </div>

            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm text-gray-500 mb-3">Статус аккаунта</p>
              <div className="flex flex-wrap gap-2">
                {user.is_active !== undefined && (
                  <span
                    className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                      user.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}
                  >
                    {user.is_active ? 'Активен' : 'Неактивен'}
                  </span>
                )}
                {user.is_staff && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                    Администратор
                  </span>
                )}
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};
