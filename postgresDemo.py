# demo accessing a row from postgres database from python script.
class Demo():

    def __init__(self):

    def connect(self):
        """Connect to the PostgreSQL database.  Returns a database connection."""
        try:
            return psycopg2.connect("dbname=postgrestest")
        except:
            print "unable to connect to postgrestest"

    def execute(self, sql, params):
        # print sql, params
        conn = self.connect()
        result = conn.cursor().execute(sql, params)
        conn.commit()
        conn.close()
        # print result

    def fetchAll(self, sql, params):
        # print sql, params
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(sql, params)
        resultRows = cur.fetchall()
        conn.commit()
        conn.close()
        return resultRows

    def deleteAll(self):
        """Remove all the records from the database."""
        # first remove all registrations that reference persons
        registration_mod.RegistrationStore(self.db).deleteAll()
        self.db.execute("DELETE FROM PERSON;", ())

    def getByName(self, name):
        result = self.fetchAll(
            "SELECT * FROM PERSON WHERE name=%s;", (name,))
        if len(result) == 1:
            row = result[0]
            person = Person(row[0], row[1], row[2])
            return person
        elif len(result) > 1:
            raise NameError("more than one person with name: '%s';" % name)
        else:
            return None

    def getById(self, id):
        result = self.fetchAll(
            "SELECT * FROM PERSON WHERE id=%s;", (id,))
        if len(result) == 1:
            row = result[0]
            person = Person(row[0], row[1], row[2])
            return person
        elif len(result) > 1:
            raise NameError("more than one person with name: '%s';" % name)
        else:
            return None

    def createPerson(self, name, born):
        """create registration for person with name in tournament"""
        self.execute(
            "INSERT INTO PERSON (name,born) VALUES(%s,%s);", (name, born,))

# Person is responsible for attributes of a player
# needed by this tournament application.
class Person():

    def __init__(self, id, name, born):
        self.id = id
        self.name = name
        self.born = born
