FROM node:20-slim

WORKDIR /app

# Copier package.json et installer les dépendances
COPY package.json ./
RUN npm install

# Copier le reste des fichiers
COPY . .

# Créer un volume anonyme pour node_modules (évite l'écrasement)
VOLUME ["/app/node_modules"]

EXPOSE 8000

CMD ["node", "server.js"]