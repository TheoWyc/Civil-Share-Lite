FROM node:20-slim

WORKDIR /app

# Installer serve globalement
RUN npm install -g serve

# Copier les fichiers
COPY . .

EXPOSE 3000

CMD ["serve", "-s", ".", "-l", "3000"]