import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False


class Neo4jService:
    def __init__(self):
        self.driver = None
        self._connected = False
        if NEO4J_AVAILABLE and config.NEO4J_URI and config.NEO4J_PASSWORD:
            try:
                self.driver = GraphDatabase.driver(
                    config.NEO4J_URI,
                    auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD),
                )
                self.driver.verify_connectivity()
                self._connected = True
            except Exception as e:
                print(f"[Neo4j] Connection failed: {e}")

    def is_connected(self):
        return self._connected

    def close(self):
        if self.driver:
            self.driver.close()

    def ingest_employees(self, employees_df):
        if not self._connected:
            return False
        with self.driver.session() as session:
            for _, row in employees_df.iterrows():
                session.run(
                    """
                    MERGE (e:Employee {id: $id})
                    SET e.name = $name, e.department = $dept,
                        e.role = $role, e.warehouse = $warehouse,
                        e.performance_score = $score, e.tier = $tier
                    MERGE (d:Department {name: $dept})
                    MERGE (e)-[:BELONGS_TO]->(d)
                    MERGE (w:Warehouse {name: $warehouse})
                    MERGE (e)-[:WORKS_AT]->(w)
                    """,
                    id=row["employee_id"],
                    name=row["name"],
                    dept=row["department"],
                    role=row["role"],
                    warehouse=row["warehouse"],
                    score=row.get("performance_score", 0),
                    tier=row.get("performance_tier", "N/A"),
                )
        return True

    def ingest_vendors(self, vendors_df):
        if not self._connected:
            return False
        with self.driver.session() as session:
            for _, row in vendors_df.iterrows():
                session.run(
                    """
                    MERGE (v:Vendor {id: $id})
                    SET v.name = $name, v.category = $cat,
                        v.contract_value = $val, v.region = $region
                    MERGE (r:Region {name: $region})
                    MERGE (v)-[:OPERATES_IN]->(r)
                    """,
                    id=row["vendor_id"],
                    name=row["vendor_name"],
                    cat=row["category"],
                    val=row["contract_value"],
                    region=row["region"],
                )
        return True

    def ingest_contracts(self, contracts_df):
        if not self._connected:
            return False
        with self.driver.session() as session:
            for _, row in contracts_df.iterrows():
                session.run(
                    """
                    MERGE (c:Contract {id: $id})
                    SET c.vendor = $vendor, c.value = $value,
                        c.start = $start, c.end = $end, c.status = $status
                    """,
                    id=row["contract_id"],
                    vendor=row["vendor_name"],
                    value=row["value"],
                    start=row["start_date"],
                    end=row["end_date"],
                    status=row["status"],
                )
        return True

    def get_graph_data(self):
        """Returns nodes and edges for visualization."""
        if not self._connected:
            return [], []
        nodes, edges = [], []
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN n LIMIT 100")
            for record in result:
                node = record["n"]
                nodes.append({
                    "id": str(node.id),
                    "label": list(node.labels)[0] if node.labels else "Node",
                    "properties": dict(node),
                })
            result = session.run(
                "MATCH (a)-[r]->(b) RETURN a, type(r) as rel, b LIMIT 200"
            )
            for record in result:
                edges.append({
                    "source": str(record["a"].id),
                    "target": str(record["b"].id),
                    "relation": record["rel"],
                })
        return nodes, edges

    def run_cypher(self, query: str):
        if not self._connected:
            return []
        with self.driver.session() as session:
            result = session.run(query)
            return [dict(r) for r in result]
