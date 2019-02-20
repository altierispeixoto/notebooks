from neo4j import GraphDatabase


class Neo4JConnection(object):

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_patology(self, nome):
        with self._driver.session() as session:
            return session.run("CREATE (p:Patologia) "
                               " SET p.nome = $nome  RETURN id(p)", nome=nome).single().value()

    def create_principio_ativo(self, term, english_term, drugbank_id, drugbank_description, drugbank_descricao):
        with self._driver.session() as session:
            return session.run(
                "MERGE (p:ItemPrincipioAtivo {term: $term, english_term: $english_term,drugbank_id:$drugbank_id,drugbank_description:$drugbank_description,drugbank_descricao:$drugbank_descricao}) RETURN id(p)", \
                term=term, english_term=english_term, drugbank_id=drugbank_id,
                drugbank_description=drugbank_description, drugbank_descricao=drugbank_descricao).single().value()
            # return session.run("CREATE (p:ItemPrincipioAtivo {nome:$nome}) RETURN id(p)", nome=nome).single().value()

    def create_contra_indicacao_term(self, nome):
        with self._driver.session() as session:
            return session.run("CREATE (c:ContraIndicacaoTerm {nome:$nome}) RETURN id(c)", nome=nome).single().value()

    def create_relationship_principio_ativo_patologia(self, nome_patologia, nome_principio_ativo, term_frequency):
        with self._driver.session() as session:
            return session.run("MATCH (p:Patologia),(i:ItemPrincipioAtivo) "
                               "WHERE p.nome = $patologia and  i.term = $principio_ativo "
                               "CREATE (i)-[r:active_principle_indication { nome: p.nome + ' <-> ' + i.term , freq: $frequency }]->(p) RETURN type(r), r.nome",
                               patologia=nome_patologia, principio_ativo=nome_principio_ativo, frequency=term_frequency)

    def create_relationship_contra_indicacao_patologia(self, nome_patologia, nome_contra_indicacao, term_frequency):
        with self._driver.session() as session:
            return session.run("MATCH (p:Patologia),(c:ItemPrincipioAtivo) "
                               "WHERE p.nome = $patologia and  c.term = $nome_contra_indicacao "
                               "CREATE (c)-[r:counter_indication_term_associated { nome: p.nome + ' <-> ' + c.term , freq: $frequency }]->(p) RETURN type(r), r.nome",
                               patologia=nome_patologia, nome_contra_indicacao=nome_contra_indicacao,
                               frequency=term_frequency)

    def create_relationship_principio_ativo(self, term1, term2, term_frequency):
        with self._driver.session() as session:
            return session.run("MATCH (i1:ItemPrincipioAtivo),(i2:ItemPrincipioAtivo) "
                               "WHERE i1.term = $term1 and  i2.term = $term2 "
                               "CREATE (i1)-[r:active_principle_linked_term { nome: i1.term + ' <-> ' + i2.term , freq: $frequency }]->(i2) RETURN type(r), r.nome",
                               term1=term1, term2=term2, frequency=term_frequency)

    def delete_all(self):
        with self._driver.session() as session:
            return session.run("MATCH (n) DETACH DELETE n").single()