import express from "express";
import helmet from "helmet";
import cors from "cors";
import morgan from "morgan";
import rateLimit from "express-rate-limit";
import fetch from "node-fetch";
import { z } from "zod";

const app = express();

// --- Security / Observability ---
app.use(helmet({ crossOriginResourcePolicy: false }));
app.use(cors({ origin: "*"}));
app.use(express.json());
app.use(morgan("tiny"));

const limiter = rateLimit({
  windowMs: 60 * 1000,
  max: 60, // 60 req/min per IP
  standardHeaders: true,
  legacyHeaders: false
});
app.use("/v1/", limiter);

// --- Simple auth middleware for /v1/* ---
app.use("/v1", (req, res, next) => {
  const key = process.env.GATEWAY_API_KEY;
  if (!key) return res.status(500).json({ error: "Server misconfigured: GATEWAY_API_KEY not set" });
  const incoming = req.header("X-API-Key");
  if (incoming !== key) return res.status(401).json({ error: "Unauthorized" });
  next();
});

// --- Health ---
app.get("/health", (_req, res) => {
  res.setHeader("Cache-Control", "no-store");
  res.json({ ok: true, ts: new Date().toISOString(), service: "panicapi-gateway" });
});

// --- Common helpers ---
const CRYPTOPANIC_BASE = "https://cryptopanic.com";
function boolToQuery(v: unknown) {
  if (v === undefined || v === null) return null;
  const s = String(v).toLowerCase();
  if (s === "true" || s === "1") return "1";
  if (s === "false" || s === "0") return "0";
  return null;
}

// Allowed enums
const FILTERS = ["rising","hot","bullish","bearish","important","saved","lol"] as const;
const KINDS = ["news","media"] as const;
const REGIONS = ["en","de","nl","es","fr","it","pt","ru","tr","ar","cn","jp","ko"] as const;

const PostsQuery = z.object({
  kind: z.enum(KINDS).optional(),
  filter: z.enum(FILTERS).optional(),
  currencies: z.string().optional(),
  regions: z.string().refine(
    (v) => v.split(",").every(c => (REGIONS as readonly string[]).includes(c.trim())),
    { message: "Invalid region code" }
  ).optional(),
  page: z.coerce.number().int().positive().optional(),
  public: z.string().optional(),
  following: z.string().optional(),
  metadata: z.string().optional(),
  approved: z.string().optional(),
  panic_score: z.string().optional(),
  format: z.enum(["json","rss"]).optional()
});

// --- Posts ---
app.get("/v1/news/cryptopanic/posts", async (req, res) => {
  const token = process.env.CRYPTOPANIC_TOKEN;
  if (!token) return res.status(500).json({ error: "Server misconfigured: CRYPTOPANIC_TOKEN not set" });

  // validate
  const parse = PostsQuery.safeParse(req.query);
  if (!parse.success) {
    return res.status(400).json({ error: "Bad request", details: parse.error.flatten() });
  }
  const q = parse.data;

  const upstream = new URL("/api/v1/posts/", CRYPTOPANIC_BASE);
  upstream.searchParams.set("auth_token", token);

  if (q.kind) upstream.searchParams.set("kind", q.kind);
  if (q.filter) upstream.searchParams.set("filter", q.filter);
  if (q.currencies) upstream.searchParams.set("currencies", q.currencies);
  if (q.regions) upstream.searchParams.set("regions", q.regions);
  if (q.page) upstream.searchParams.set("page", String(q.page));

  const pub = boolToQuery(q.public);
  if (pub) upstream.searchParams.set("public", pub);

  const following = boolToQuery(q.following);
  if (following) upstream.searchParams.set("following", following);

  const metadata = boolToQuery(q.metadata);
  if (metadata) upstream.searchParams.set("metadata", metadata);

  const approved = boolToQuery(q.approved);
  if (approved) upstream.searchParams.set("approved", approved);

  const panicScore = boolToQuery(q.panic_score);
  if (panicScore) upstream.searchParams.set("panic_score", panicScore);

  const format = q.format === "rss" ? "rss" : null;
  if (format) upstream.searchParams.set("format", "rss");

  const upstreamRes = await fetch(upstream.toString(), {
    headers: { "user-agent": "panicapi-gateway/1.0" }
  });

  // Pass-through body
  const cacheSeconds = 15; // small cache to protect rate limits
  res.setHeader("Cache-Control", `public, max-age=${cacheSeconds}`);
  res.setHeader("CDN-Cache-Control", `public, max-age=${cacheSeconds}`);
  res.setHeader("Vary", "Accept, X-API-Key");

  if (format) {
    const text = await upstreamRes.text();
    res.status(upstreamRes.status).type("application/rss+xml; charset=utf-8").send(text);
  } else {
    const text = await upstreamRes.text();
    const ct = upstreamRes.headers.get("content-type") || "application/json; charset=utf-8";
    res.status(upstreamRes.status).type(ct).send(text);
  }
});

// --- Portfolio (private) ---
app.get("/v1/news/cryptopanic/portfolio", async (_req, res) => {
  const token = process.env.CRYPTOPANIC_TOKEN;
  if (!token) return res.status(500).json({ error: "Server misconfigured: CRYPTOPANIC_TOKEN not set" });

  const upstream = new URL("/api/v1/portfolio/", CRYPTOPANIC_BASE);
  upstream.searchParams.set("auth_token", token);

  const upstreamRes = await fetch(upstream.toString(), {
    headers: { "user-agent": "panicapi-gateway/1.0" }
  });
  const text = await upstreamRes.text();
  const ct = upstreamRes.headers.get("content-type") || "application/json; charset=utf-8";
  res.status(upstreamRes.status).type(ct).send(text);
});

// --- Root redirect/help ---
app.get("/", (_req, res) => {
  res.type("text/plain").send("PanicAPI gateway up. Try GET /health");
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`PanicAPI listening on :${port}`);
});
