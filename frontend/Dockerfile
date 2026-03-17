# ── Stage 1: Build ───────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY . .

# Build Next.js
RUN npm run build
RUN mkdir -p public

# ── Stage 2: Run ─────────────────────────────────
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy built files
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
# We created public in builder so it exists
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]
