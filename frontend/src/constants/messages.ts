export const MESSAGES = {
  SUCCESS: {
    LOGIN: 'Успешный вход!',
    REGISTER: 'Регистрация успешна!',
    LOGOUT: 'Вы вышли из системы',
    COMMENT_ADDED: 'Комментарий добавлен',
    RATING_ADDED: 'Оценка добавлена',
    LIKE_ADDED: 'Лайк добавлен',
    LIKE_REMOVED: 'Лайк удален',
  },
  ERROR: {
    GENERIC: 'Что-то пошло не так',
    NETWORK: 'Ошибка сети. Проверьте подключение',
    UNAUTHORIZED: 'Необходима авторизация',
    NOT_FOUND: 'Не найдено',
    VALIDATION: 'Ошибка валидации данных',
  },
  VALIDATION: {
    REQUIRED: 'Это поле обязательно',
    EMAIL: 'Неверный формат email',
    PASSWORD_MIN: 'Минимум 8 символов',
    PASSWORD_MATCH: 'Пароли не совпадают',
  },
} as const;
