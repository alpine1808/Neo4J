from neo4j import GraphDatabase, Driver

class Neo4jClient:
    def __init__(self, uri: str, user: str, password: str):
        self.driver: Driver = GraphDatabase.driver(uri, auth=(user, password))
    def session(self):
        return self.driver.session()
    def close(self):
        self.driver.close()