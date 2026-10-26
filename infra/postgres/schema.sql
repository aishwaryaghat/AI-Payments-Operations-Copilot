-- Synthetic demonstration schema. Do not use demo credentials in production.
CREATE TABLE IF NOT EXISTS payments (
    id BIGINT PRIMARY KEY,
    status TEXT NOT NULL CHECK (status IN ('FAILED','SUCCESS','EXCEPTION')),
    amount_cents BIGINT NOT NULL CHECK (amount_cents >= 0),
    business_date DATE NOT NULL
);
CREATE INDEX IF NOT EXISTS payments_date_status ON payments(business_date,status);
CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    event_time TIMESTAMPTZ NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    outcome TEXT NOT NULL,
    detail TEXT NOT NULL
);
INSERT INTO payments(id,status,amount_cents,business_date) VALUES
(1,'FAILED',10000,'2026-10-20'),
(2,'FAILED',25000,'2026-10-20'),
(3,'EXCEPTION',5000,'2026-10-20'),
(4,'SUCCESS',75000,'2026-10-20'),
(5,'SUCCESS',10000,'2026-10-21')
ON CONFLICT(id) DO NOTHING;
