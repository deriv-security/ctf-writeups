FROM node:lts-alpine
WORKDIR /app
COPY ./src/package*.json ./
RUN npm install
COPY ./src .
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001
RUN chown -R nodejs:nodejs /app
USER nodejs

EXPOSE 3000

ENV NODE_ENV=production

CMD ["npm", "start"]
