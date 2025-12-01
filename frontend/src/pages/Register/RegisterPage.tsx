import { useState, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card, Input, Button } from '@/components/ui';
import { useAuth } from '@/contexts';
import { ROUTES, MESSAGES } from '@/constants';
import { isEmail, isPasswordValid } from '@/utils';

export const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.username) {
      newErrors.username = MESSAGES.VALIDATION.REQUIRED;
    }

    if (!formData.email) {
      newErrors.email = MESSAGES.VALIDATION.REQUIRED;
    } else if (!isEmail(formData.email)) {
      newErrors.email = MESSAGES.VALIDATION.EMAIL;
    }

    if (!formData.password) {
      newErrors.password = MESSAGES.VALIDATION.REQUIRED;
    } else if (!isPasswordValid(formData.password)) {
      newErrors.password = MESSAGES.VALIDATION.PASSWORD_MIN;
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = MESSAGES.VALIDATION.PASSWORD_MATCH;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setIsLoading(true);

    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
        password_confirm: formData.confirmPassword,
        first_name: formData.first_name,
        last_name: formData.last_name,
      });
      navigate(ROUTES.HOME);
    } catch (err: any) {
      setErrors({ general: err.message || MESSAGES.ERROR.GENERIC });
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  return (
    <div className="container mx-auto px-4 max-w-md">
      <Card padding="lg">
        <h1 className="text-2xl font-bold text-center mb-6">Регистрация</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          {errors.general && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{errors.general}</p>
            </div>
          )}

          <Input
            label="Имя пользователя"
            type="text"
            value={formData.username}
            onChange={(e) => handleChange('username', e.target.value)}
            error={errors.username}
            required
            fullWidth
          />

          <Input
            label="Email"
            type="email"
            value={formData.email}
            onChange={(e) => handleChange('email', e.target.value)}
            error={errors.email}
            required
            fullWidth
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Имя"
              type="text"
              value={formData.first_name}
              onChange={(e) => handleChange('first_name', e.target.value)}
            />
            <Input
              label="Фамилия"
              type="text"
              value={formData.last_name}
              onChange={(e) => handleChange('last_name', e.target.value)}
            />
          </div>

          <Input
            label="Пароль"
            type="password"
            value={formData.password}
            onChange={(e) => handleChange('password', e.target.value)}
            error={errors.password}
            required
            fullWidth
          />

          <Input
            label="Подтвердите пароль"
            type="password"
            value={formData.confirmPassword}
            onChange={(e) => handleChange('confirmPassword', e.target.value)}
            error={errors.confirmPassword}
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
            Зарегистрироваться
          </Button>

          <div className="text-center text-sm text-gray-600">
            Уже есть аккаунт?{' '}
            <Link to={ROUTES.LOGIN} className="text-primary-600 hover:underline">
              Войти
            </Link>
          </div>
        </form>
      </Card>
    </div>
  );
};
