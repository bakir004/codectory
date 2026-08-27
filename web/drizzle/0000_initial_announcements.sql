CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE TABLE IF NOT EXISTS "announcements" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "author" text NOT NULL,
  "source" text NOT NULL CHECK ("source" IN ('Professor', 'Administration')),
  "body" text NOT NULL,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL
);
INSERT INTO "announcements" ("id", "author", "source", "body", "created_at", "updated_at") VALUES
('00000000-0000-4000-8000-000000000001', 'Dr. Maya Chen', 'Professor', 'Office hours will move to Thursday this week. Bring your draft questions.', '2026-04-10T00:00:00Z', '2026-04-10T00:00:00Z'),
('00000000-0000-4000-8000-000000000002', 'Office of Student Life', 'Administration', 'Spring research showcase registration is open through Friday, April 17.', '2026-04-09T00:00:00Z', '2026-04-09T00:00:00Z')
ON CONFLICT (id) DO NOTHING;
