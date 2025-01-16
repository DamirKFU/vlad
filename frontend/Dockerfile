   # frontend/Dockerfile
   FROM node:14

   # Устанавливаем рабочую директорию
   WORKDIR /app

   # Копируем package.json и package-lock.json
   COPY package*.json ./

   # Устанавливаем зависимости
   RUN npm install

   # Копируем все файлы приложения
   COPY . .

   # Собираем приложение
   RUN npm run build

   # Устанавливаем сервер для обслуживания статических файлов
   RUN npm install -g serve

   # Открываем порт 3000
   EXPOSE 3000

   # Запускаем сервер
   CMD ["serve", "-s", "build"]