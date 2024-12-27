export const validateRussianPhone = (phone) => {
  const pattern = /^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}$/;
  return pattern.test(phone);
};

export const formatPhoneNumber = (value) => {
  if (!value) return '+7';
  
  // Убираем все кроме цифр
  const phoneNumber = value.replace(/\D/g, '');
  
  // Убираем первую 7 или 8 если они есть
  const normalizedPhone = phoneNumber.replace(/^[78]/, '');
  
  // Форматируем номер
  let formattedPhone = '+7';
  if (normalizedPhone.length > 0) {
    formattedPhone += ' (' + normalizedPhone.substring(0, 3);
  }
  if (normalizedPhone.length > 3) {
    formattedPhone += ') ' + normalizedPhone.substring(3, 6);
  }
  if (normalizedPhone.length > 6) {
    formattedPhone += '-' + normalizedPhone.substring(6, 8);
  }
  if (normalizedPhone.length > 8) {
    formattedPhone += '-' + normalizedPhone.substring(8, 10);
  }
  
  return formattedPhone;
}; 