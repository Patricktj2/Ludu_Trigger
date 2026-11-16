CREATE TABLE klienter (
	id SERIAL PRIMARY KEY,
	kode TEXT UNIQUE NOT NULL,
	OPRETTET TIMESTAMP DEFAULT now()
);

CREATE TABLE sessions (
	id SERIAL PRIMARY KEY,
	klient_id INTEGER NOT NULL REFERENCES klienter(id),
	startet TIMESTAMP DEFAULT now(),
	afsluttet TIMESTAMP,
	stoppet_af_klient BOOLEAN DEFAULT false
);

CREATE TABLE domaener (
	id SERIAL PRIMARY KEY,
	domaene TEXT UNIQUE NOT NULL,
	kategori TEXT NOT NULL
);

CREATE TABLE maalinger (
	id SERIAL PRIMARY KEY,
	session_id INTEGER NOT NULL REFERENCES sessions(id),
	sensor TEXT NOT NULL CHECK (sensor IN ('puls', 'gsr')),
	vaerdi REAL NOT NULL,
	tidspunkt TIMESTAMP DEFAULT now()
);

CREATE TABLE haendelser (
	id SERIAL PRIMARY KEY,
	session_id INTEGER NOT NULL REFERENCES sessions(id),
	type TEXT NOT NULL CHECK (type IN ('dns_opslag', 'vibration', 'stop')),
	domaene_id INTEGER REFERENCES domaener(id),
	tidspunkt TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_maalinger_session_tid ON maalinger (session_id, tidspunkt);
