FROM node:latest

WORKDIR /app

# Копируем package.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем исходный код
COPY . .

# Открываем порт
EXPOSE 4200

# Запускаем dev server
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--poll", "1000"]