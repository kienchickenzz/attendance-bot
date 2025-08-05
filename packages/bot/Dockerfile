FROM node:20-alpine
RUN apk add --update libc6-compat python3 make g++

# Install curl for container-level health checks
RUN apk add --no-cache curl

# Install PNPM globaly
RUN npm install -g pnpm

ENV NODE_OPTIONS=--max-old-space-size=8192

WORKDIR /app/src

# Copy app source
COPY . .

RUN pnpm install

RUN pnpm build

EXPOSE 3978

CMD [ "pnpm", "start" ]
