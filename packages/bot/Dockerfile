FROM oven/bun:1

# Install curl for container-level health checks
RUN apt-get update && apt-get install -y curl

WORKDIR /app/src

# Copy app source
COPY . .

RUN bun install

RUN bun run build

EXPOSE 3978

CMD [ "bun", "run", "start" ]
