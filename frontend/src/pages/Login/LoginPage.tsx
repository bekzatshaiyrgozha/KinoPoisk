import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, Input, Button } from '@/components/ui';
import { useAuth } from '@/contexts';
import { ROUTES, MESSAGES } from '@/constants';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login({ email, password });
      navigate(ROUTES.HOME);
    } catch (err: any) {
      setError(err.message || MESSAGES.ERROR.GENERIC);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 max-w-md">
      <Card padding="lg">
        <h1 className="text-2xl font-bold text-center mb-6">Вход</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{error}</p>
            </div>
          )}

          <Input
            label="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Введите email"
            required
            fullWidth
          />

          <Input
            label="Пароль"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Введите пароль"
            required
            fullWidth
          />

          <Button
            type="submit"
            variant="primary"
            fullWidth
            isLoading={isLoading}
            disabled={isLoading}
          >
            Войти
          </Button>

          <div className="text-center text-sm text-gray-600">
            Нет аккаунта?{' '}
            <Link to={ROUTES.REGISTER} className="text-primary-600 hover:underline">
              Зарегистрироваться
            </Link>
          </div>
        </form>
      </Card>
    </div>
  );
};
