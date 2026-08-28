-- ============================================
-- Seed Data — Development/Demo
-- ============================================

-- Insert default gateway record
INSERT INTO gateway (name, device_id, status)
VALUES ('Main Gateway (Raspberry Pi)', 'GATEWAY-001', 'OFFLINE')
ON CONFLICT (device_id) DO NOTHING;

-- Insert a demo panel
INSERT INTO panels (panel_code, name, description)
VALUES ('PANEL-A', 'Panel Alpha', 'Primary working panel for SIH2026 demo')
ON CONFLICT (panel_code) DO NOTHING;

-- Insert 20 simulation node registration codes (for demo purposes)
-- Codes: 100001 to 100020
INSERT INTO node_registration_codes (code, status, expires_at)
SELECT
  LPAD((100000 + n)::text, 6, '0'),
  'PENDING',
  NOW() + INTERVAL '30 days'
FROM generate_series(1, 20) AS n
ON CONFLICT (code) DO NOTHING;
