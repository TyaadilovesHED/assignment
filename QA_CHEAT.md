Q&A Cheat Sheet — Likely interview questions and short answers

Q: Why not use OFFSET pagination?
A: OFFSET requires skipping rows, which is O(offset+page_size) and becomes slow. It's also unsafe when data changes because inserted/deleted rows shift offsets leading to duplicates or skips.

Q: Why add a `snapshot`?
A: Snapshot fixes the visible dataset for the session. New items after the snapshot are excluded so the user sees a consistent ordered list across pages.

Q: What happens if two rows have identical `created_at`?
A: We break ties using `id DESC`, which ensures deterministic ordering and prevents the same item from appearing on multiple pages.

Q: How to support previous page?
A: Previous-page support is complex for descending-ordered cursor pagination. Options: store cursors server-side with history, or implement a client-side stack of previous cursors. Another approach is using keyset in the opposite direction for backward navigation.

Q: How to make this scalable in production?
A: Use Postgres, add proper indexes, run queries with prepared statements, use connection pooling. For heavy read traffic, add read replicas, or cache pages in Redis if data is mostly read-only.

Q: How to expire cursors?
A: Add TTL to server-side stored cursors or include a timestamp in the cursor and reject cursors older than a chosen threshold.

Q: Any edge cases?
A: Clock skew or timezone handling: use consistent UTC times. If updated_at changes ordering, stick to created_at for pagination keys. Also watch out for very concurrent writes creating many items with identical timestamps—ensure `id` is included for determinism.

Q: How did AI help?
A: AI accelerated prototyping (skeleton server, UI layout, cursor encoding). I validated all code and fixed issues manually (cursor format validation, index usage, seed performance).