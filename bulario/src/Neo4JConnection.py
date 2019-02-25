from neo4j import GraphDatabase


class Neo4JConnection(object):

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_patology(self, disease):
        with self._driver.session() as session:
            return session.run("CREATE (p:Patologia) "
                               " SET p.disease = $disease  RETURN id(p)", disease=disease).single().value()

    def create_principio_ativo(self, name_pt_br, name_en, drugbank_id, description_en, description_pt_br):
        with self._driver.session() as session:
            return session.run(
                "MERGE (d:Drug "
                "{name_pt_br: $name_pt_br"
                ",name_en: $name_en,"
                " drugbank_id:$drugbank_id,"
                " drugbank_description_en:$description_en,"
                " description_pt_br:$description_pt_br}"
                ") RETURN id(d)",
                name_pt_br=name_pt_br, name_en=name_en, drugbank_id=drugbank_id,
                description_en=description_en, description_pt_br=description_pt_br).single().value()

    def create_relationship_drug_disease(self, drugbank_id, disease):
        with self._driver.session() as session:
            return session.run("MATCH (p:Patologia),(d:Drug) "
                               "WHERE p.disease = $disease and  d.drugbank_id = $drugbank_id "
                               "CREATE (d)-[r:indication "
                               "{ nome: p.disease + ' <-> ' + d.name_pt_br}]->(p) "
                               "RETURN type(r), r.nome",
                               disease=disease, drugbank_id=drugbank_id)

    def create_relationship_counter_indication_drug_disease(self, drugbank_id, disease):
        with self._driver.session() as session:
            return session.run("MATCH (p:Patologia),(d:Drug) "
                               "WHERE p.disease = $disease and  d.drugbank_id = $drugbank_id "
                               "CREATE (d)-[r:counter_indication "
                               "{ nome: p.disease + ' <-> ' + d.name_pt_br}]->(p) "
                               "RETURN type(r), r.nome",
                               disease=disease, drugbank_id=drugbank_id)

    def create_drug_interaction_relationship(self,drugbank_interaction_id,drugbank_id, description_pt_br):
        with self._driver.session() as session:
            return session.run("MATCH (d0:Drug),(d:Drug) "
                               "WHERE d0.drugbank_id = $drugbank_interaction_id and  d.drugbank_id = $drugbank_id "
                               "CREATE (d0)-[r:drug_interaction "
                               "{ description: $description_pt_br}]->(d) "
                               "RETURN type(r)",
                               drugbank_interaction_id=drugbank_interaction_id, drugbank_id=drugbank_id
                               , description_pt_br=description_pt_br)


    def delete_all(self):
        with self._driver.session() as session:
            return session.run("MATCH (n) DETACH DELETE n").single()
