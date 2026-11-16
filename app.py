import hmac
import os
import psycopg
from psycopg.rows import dict_row
from apiflask import APIFlask, HTTPTokenAuth, Schema, abort
from apiflask.fields import Boolean, DateTime, Float, Integer, String
from apiflask.validators import OneOf, Regexp

DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
API_TOKEN = os.environ["API_TOKEN"]

app = APIFlask(__name__, title="Anti-Ludo-Trigger API", version="1.0")
auth = HTTPTokenAuth(scheme="Bearer") #En auth variabel som bruges til at authenticate

@auth.verify_token #Denne del siger at det her under bruges til at tjekke tokens
def verify_token(token):
	if hmac-compare_digest(token.encode(), API_TOKEN.encode()):
		return "klient"
	return None

def db():
	return psycopg.connect(
		dbname=DB_NAME,
		user=DB_USER,
		password=DB_PASSWORD,
		host="localhost",
		row_factory=dict_row,
	)

class KlientIn(Schema):
	kode = String(required=True, validate=Regexp(r"^KL-\d{4}$"))

class KlientOut(Schema):
	id = Integer()
	kode = String()
	oprettet = DateTime()

class SessionIn(Schema):
	klient_id = Integer(required=True)

class SessionOut(Schema):
	id = Integer()
	klient_id = Integer()
	startet = DateTime()
	afsluttet = DateTime(allow_none=True)
	stoppet_af_klient = Boolean()

class MaalingIn(Schema):
	session_id = Integer(required=True)
	sensor = String(required=True, validate=OneOf(["puls", "gsr"]))
	vaerdi = Float(required=True)

class MaalingOut(Schema):
	id = Integer()
	session_id = Integer()
	sensor = String()
	vaerdi = Float()
	tidspunkt = DateTime()

class HaendelseIn(Schema):
	session_id = Integer(required=True)
	type = String(required=True, validate=OneOf(["dns_opslag", "vibration", "stop"]))
	domaene_id = Integer(load_default=None, allow_none=True)

class HaendelseOut(Schema):
	id = Integer()
	session_id = Integer()
	type = String()
	domaene_id = Integer(allow_none=True)
	tidspunkt = DateTime()

@app.get("/status")
def status():
	return {"status": "ok"}

@app.post("/klienter")
@app.auth_required(auth)
@app.input(KlientIn, arg_name="data")
@app.output(KlientOut, status_code=201)

def opret_klient(data):
	try:
		with db() as conn:
			return conn.execute(
				"INSERT INTO klienter (kode) VALUES (%s) RETURNING *",
				(data["kode"],),
			).fetchone()
	except psycopg.errors.UniqueViolation:
		abort(409, "Klientkoden findes allerede")

@app.post("/sessions")
@app.auth_required(auth)
@app.input(SessionIn, arg_name="data")
@app.output(SessionOut, status_code=201)

def opret_session(data):
    try:
        with db() as conn:
            return conn.execute(
                "INSERT INTO sessions (klient_id) VALUES (%s) RETURNING *",
                (data["klient_id"],),
            ).fetchone()
    except psycopg.errors.ForeignKeyViolation:
        abort(404, "Klienten findes ikke")

@app.post("/maalinger")
@app.auth_required(auth)
@app.input(MaalingIn, arg_name="data")
@app.output(MaalingOut, status_code=201)

def gem_maaling(data):
    try:
        with db() as conn:
            return conn.execute(
                "INSERT INTO maalinger (session_id, sensor, vaerdi) "
                "VALUES (%s, %s, %s) RETURNING *",
                (data["session_id"], data["sensor"], data["vaerdi"]),
            ).fetchone()
    except psycopg.errors.ForeignKeyViolation:
        abort(404, "Sessionen findes ikke")

@app.get("/sessions/<int:session_id>/maalinger")
@app.auth_required(auth)
@app.output(MaalingOut(many=True))

def hent_maalinger(session_id):
    with db() as conn:
        return conn.execute(
            "SELECT * FROM maalinger WHERE session_id = %s ORDER BY tidspunkt",
            (session_id,),
        ).fetchall()

@app.post("/haendelser")
@app.auth_required(auth)
@app.input(HaendelseIn, arg_name="data")
@app.output(HaendelseOut, status_code=201)

def gem_haendelse(data):
    try:
        with db() as conn:
            raekke = conn.execute(
                "INSERT INTO haendelser (session_id, type, domaene_id) "
                "VALUES (%s, %s, %s) RETURNING *",
                (data["session_id"], data["type"], data["domaene_id"]),
            ).fetchone()
            if data["type"] == "stop":
                conn.execute(
                    "UPDATE sessions SET afsluttet = now(), stoppet_af_klient = true "
                    "WHERE id = %s",
                    (data["session_id"],),
                )
            return raekke
    except psycopg.errors.ForeignKeyViolation:
        abort(404, "Sessionen eller domænet findes ikke")
