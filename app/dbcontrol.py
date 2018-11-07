import sqlite3
from os.path import isfile, getsize
db = 'vminfo_db.sqlite3'

def create_db(): #Attempts to create or connect to vminfo_db.sqlite3 database.
	conn = sqlite3.connect(db)

	try:
		c = conn.cursor()
		c.execute("create table if not exists sim_info (vm_name text unique not null, password text not null, vncport integer not null)")
		conn.commit()

	except Exception as err:
		return err

	finally:
		conn.close()

def drop_sim_info(): #Attempts to drop the sim_info table if the database exists.
	conn = sqlite3.connect(db)

	try:
		c = conn.cursor()
		c.execute("drop table if exists sim_info")
		conn.commit()

	except Exception as err:
		return err

	finally:
		conn.close()

def add_vm(name, pw, port): #Attempts to insert vm information using passed arguments if the database exists.
	additions = ((name, pw, port))
	conn = sqlite3.connect(db)

	try:
		c = conn.cursor()
		c.execute("insert into sim_info values (?, ?, ?)", additions)
		conn.commit()

	except Exception as err:
		return err

	finally:
		conn.close()

def update_password(name, pw): #Attempts to update a vm password using the passed name and password arguments if the database exists.
	update = ((pw, name))
	conn = sqlite3.connect(db)

	try:
		c = conn.cursor()
		c.execute("update sim_info set password=? where vm_name=?", update)
		conn.commit()

	except Exception as err:
		return err

	finally:
		conn.close()

def get_password(name): #Get password for a vm (used for reboot to set the password back to normal)
	conn = sqlite3.connect(db)

	try:
		c = conn.cursor()
		query = c.execute("select password from sim_info where vm_name=?", (name,))
		result = query.fetchall()[0][0]
		return result

	except Exception as err:
		return err

	finally:
		conn.close()

def vm_info(): #Queries the database for all available VM info and returns the data in a dictionary.
	conn = sqlite3.connect(db)
	conn.text_factory = str

	try:
		c = conn.cursor()
		query = c.execute("select vm_name, password, vncport from sim_info")

		col = [desc[0] for desc in query.description]
		result = [dict(zip(col, row)) for row in query.fetchall()]

		return result

	except Exception as err:
		return err

	finally:
		conn.close()
