FROM node:26-alpine

WORKDIR /app

COPY package.json package-lock.json ./
COPY apps/web/package.json ./apps/web/package.json
RUN npm install

COPY apps/web ./apps/web

EXPOSE 3000

CMD ["npm", "run", "dev", "--workspace", "@creator-os/web", "--", "--hostname", "0.0.0.0"]
