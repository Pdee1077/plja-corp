# plja-chatter-feed

Cloudflare Worker that refreshes the public Market Chatter board every 15 minutes and stores the snapshot in KV. The site's `/live/board.json` Pages Function serves that snapshot (falling back to the `live-data` GitHub branch). CORS is open so Tipoff can embed the feed.

No secrets are required at runtime. It reads only public ApeWisdom, StockTwits and Yahoo endpoints.
